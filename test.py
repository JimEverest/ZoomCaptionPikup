import uiautomation as auto
from time import sleep
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict
import re
import win32api
import win32con
import win32gui
import os
from pathlib import Path
import time
import threading

@dataclass
class TranscriptItem:
    """字幕条目的数据类"""
    speaker: str
    timestamp: str
    content: str
    
    def to_string(self) -> str:
        """转换为字符串格式"""
        return f"[{self.timestamp}] {self.speaker}: {self.content}"

class TranscriptManager:
    def __init__(self, message_callback=None):
        self.transcripts: Dict[str, TranscriptItem] = {}
        self.current_speaker = ""
        self.initial_scan_done = False
        self.output_file = None
        self.earliest_timestamp = None
        self.latest_timestamp = None
        self.latest_messages = {}
        self.message_callback = message_callback
    
    def _get_output_path(self) -> Path:
        """获取输出文件路径"""
        # 获取用户目录
        user_home = os.path.expanduser("~")
        # 创建ZoomTranscript目录
        transcript_dir = Path(user_home) / "ZoomTranscript"
        transcript_dir.mkdir(parents=True, exist_ok=True)
        
        # 获取当前系统日期和时间
        current_time = datetime.now()
        
        # 如果没有最早和最晚时间戳，使用默认值
        if not self.earliest_timestamp or not self.latest_timestamp:
            self.earliest_timestamp = current_time.strftime("%H-%M-%S")
            self.latest_timestamp = current_time.strftime("%H-%M-%S")
        
        # 构建文件名：zoom_YYYY-MMM-DD_HH-MM-SS_HH-MM-SS.txt
        # 使用strftime的 %b 来获取月份缩写
        file_name = f"zoom_{current_time.strftime('%Y-%b-%d')}_{self.earliest_timestamp}_{self.latest_timestamp}.txt"
        
        return transcript_dir / file_name
    
    def _update_earliest_timestamp(self, timestamp: str):
        """更新最早的时间戳"""
        try:
            current_time = datetime.strptime(timestamp, '%H:%M:%S')
            formatted_time = current_time.strftime("%H-%M-%S")
            
            if not self.earliest_timestamp:
                self.earliest_timestamp = formatted_time
                self.latest_timestamp = formatted_time
            else:
                # 比较并更新最早时间
                earliest = datetime.strptime(self.earliest_timestamp, '%H-%M-%S')
                if current_time < earliest:
                    self.earliest_timestamp = formatted_time
                
                # 比较并更新最晚时间
                latest = datetime.strptime(self.latest_timestamp, '%H-%M-%S')
                if current_time > latest:
                    self.latest_timestamp = formatted_time
                    
        except Exception as e:
            print(f"更新时间戳时出错: {e}")
    
    def save_to_file(self):
        """保存内容到文件"""
        try:
            output_path = self._get_output_path()
            
            # 按时间戳排序
            sorted_items = sorted(
                self.transcripts.values(),
                key=lambda x: datetime.strptime(x.timestamp, '%H:%M:%S')
            )
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                for item in sorted_items:
                    f.write(f"{item.to_string()}\n")
            
            print(f"内容已保存到: {output_path}")
            
        except Exception as e:
            print(f"保存文件时出错: {e}")
    
    def _send_key(self, vk_code):
        """发送单个按键"""
        win32api.keybd_event(vk_code, 0, 0, 0)
        sleep(0.05)
        win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
        sleep(0.05)

    def _collect_all_content(self, list_control) -> List[TranscriptItem]:
        """收集所有内容"""
        collected_items = []
        try:
            if not self.initial_scan_done:
                print("执行初始扫描...")
                list_control.SetFocus()
                sleep(0.5)
                
                # 改进的滚动到顶部逻辑
                print("滚动到顶部...")
                # 先按End键确保激活滚动
                self._send_key(win32con.VK_END)
                sleep(0.2)
                
                # 多次尝试滚动到顶部
                for _ in range(3):  # 尝试3次
                    # 连续多次按Home键
                    for _ in range(10):
                        self._send_key(win32con.VK_HOME)
                        sleep(0.1)
                    
                    # 检查是否到达顶部
                    items = self._parse_visible_items(list_control)
                    if items and items[0].timestamp:
                        print(f"已到达顶部，最早时间戳: {items[0].timestamp}")
                        break
                    sleep(0.5)
                
                print("开始向下滚动收集内容...")
                no_new_content_count = 0
                last_content_hash = ""
                seen_timestamps = set()
                
                while no_new_content_count < 3:
                    items = self._parse_visible_items(list_control)
                    if items:
                        # 使用时间戳检查是否有新内容
                        current_timestamps = {item.timestamp for item in items}
                        new_timestamps = current_timestamps - seen_timestamps
                        
                        if new_timestamps:
                            # 只添加新的内容
                            new_items = [item for item in items if item.timestamp in new_timestamps]
                            collected_items.extend(new_items)
                            seen_timestamps.update(new_timestamps)
                            print(f"发现 {len(new_items)} 个新条目")
                            no_new_content_count = 0
                        else:
                            no_new_content_count += 1
                    else:
                        no_new_content_count += 1
                    
                    # 使用Page Down键滚动
                    self._send_key(win32con.VK_NEXT)
                    sleep(0.3)  # 稍微增加等待时间
                
                self.initial_scan_done = True
                print(f"初始扫描完成，共收集到 {len(collected_items)} 个条目")
            else:
                # 已完成初始扫描，只获取当前可见内容
                collected_items = self._parse_visible_items(list_control)
            
            return collected_items
            
        except Exception as e:
            print(f"收集内容时出错: {e}")
            return collected_items

    def _parse_visible_items(self, list_control) -> List[TranscriptItem]:
        """解析当前可见的条目"""
        items = []
        try:
            for item in list_control.GetChildren():
                if item.ControlTypeName == "ListItemControl":
                    transcript = self._parse_list_item(item)
                    if transcript:
                        key = f"{transcript.timestamp}|{transcript.content}"
                        if key not in self.transcripts:
                            items.append(transcript)
            return items
        except Exception as e:
            print(f"解析可见条目时出错: {e}")
            return []

    def _parse_list_item(self, item) -> TranscriptItem:
        """解析单个ListItemControl"""
        try:
            if not item.Name:
                return None
            
            name_parts = item.Name.split('\n')
            if len(name_parts) < 2:
                return None
            
            header = name_parts[0].strip()
            content = name_parts[1].strip()
            
            time_match = re.search(r'\d{2}:\d{2}:\d{2}', header)
            if not time_match:
                return None
            
            timestamp = time_match.group(0)
            speaker_part = header[:time_match.start()].strip()
            
            if speaker_part:
                self.current_speaker = speaker_part
            speaker = speaker_part if speaker_part else self.current_speaker
            
            return TranscriptItem(speaker=speaker, timestamp=timestamp, content=content)
            
        except Exception as e:
            print(f"解析列表项时出错: {e}")
            return None
    
    def update_transcripts(self, new_items: List[TranscriptItem]):
        """更新转录内容"""
        updated = False
        for item in new_items:
            # 使用时间戳和说话者作为去重的key
            dedup_key = f"{item.timestamp}_{item.speaker}"
            
            # 检查是否需要更新
            should_update = False
            if dedup_key not in self.latest_messages:
                should_update = True
            else:
                # 如果新内容更长，则更新
                if len(item.content) > len(self.latest_messages[dedup_key].content):
                    # 删除旧内容
                    old_key = f"{item.timestamp}|{self.latest_messages[dedup_key].content}"
                    if old_key in self.transcripts:
                        del self.transcripts[old_key]
                    should_update = True

            if should_update:
                # 更新最新消息字典
                self.latest_messages[dedup_key] = item
                # 更新转录字典
                key = f"{item.timestamp}|{item.content}"
                self.transcripts[key] = item
                self._update_earliest_timestamp(item.timestamp)
                print(f"添加新条目: [{item.timestamp}] {item.speaker}: {item.content}")
                updated = True
                
                # 通知UI更新
                if self.message_callback:
                    self.message_callback("transcript", item)
        
        # 如果有更新，保存文件
        if updated:
            self.save_to_file()
        
        return updated
    
    def print_all_transcripts(self):
        """打印所有转录内容"""
        try:
            print("\n当前所有转录内容:")
            print("-" * 60)
            print(f"总条目数: {len(self.transcripts)}")
            
            if not self.transcripts:
                print("没有找到任何转录内容")
                return
            
            # 按时间戳排序
            sorted_items = sorted(
                self.transcripts.values(),
                key=lambda x: datetime.strptime(x.timestamp, '%H:%M:%S')
            )
            
            for item in sorted_items:
                print(f"[{item.timestamp}] {item.speaker}: {item.content}")
            
            print("-" * 60)
            
        except Exception as e:
            print(f"打印转录内容时出错: {e}")

def monitor_transcript(message_callback=None):
    print("开始监控转录文本...")
    manager = TranscriptManager(message_callback)
    
    # 如果在主线程中运行，需要初始化UIAutomation
    if threading.current_thread() is threading.main_thread():
        auto.InitializeUIAutomationInCurrentThread()
    
    # 返回manager实例，让UI可以直接使用
    return manager, lambda: monitor_transcript_loop(manager)

def monitor_transcript_loop(manager):
    """实际的监控循环"""
    try:
        while True:  # 外层循环
            try:
                # 查找Zoom字幕窗口
                target_hwnd = None
                found_windows = []
                
                def find_transcript_window(hwnd, extra):
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        class_name = win32gui.GetClassName(hwnd)
                        if "转录" in title or "字幕" in title or "Transcript" in title or "Caption" in title:
                            found_windows.append((hwnd, title, class_name))
                    return True  # 总是返回True继续枚举
                
                print("\n正在查找Zoom转录窗口...")
                win32gui.EnumWindows(find_transcript_window, None)
                
                # 在收集到的窗口中查找Zoom的窗口
                for hwnd, title, class_name in found_windows:
                    print(f"找到可能的窗口: Title='{title}', Class='{class_name}'")
                    if class_name == "ZPLiveTranscriptWndClass":
                        target_hwnd = hwnd
                        print(f"到Zoom转录窗口!")
                        break
                
                if not target_hwnd:
                    print("未找到Zoom转录窗口，请确保：")
                    print("1. Zoom会议已经开始")
                    print("2. 转录功能已经开启")
                    print("3. 转录窗口已经打开")
                    print("将在5秒后重试...")
                    time.sleep(5)  # 等待5秒后重试
                    continue  # 继续外层循环，重新查找窗口
                
                # 使用找到的句柄创建UIAutomation控件
                target_window = auto.ControlFromHandle(target_hwnd)
                if not target_window:
                    print("无法获取窗口控件，将在5秒后重试...")
                    time.sleep(5)
                    continue  # 继续外层循环，重新查找窗口
                    
                print(f"成功获取窗口控件: {win32gui.GetWindowText(target_hwnd)}")
                
                # 递归查找ListControl
                def find_list_control(control):
                    try:
                        if control.ControlTypeName == "ListControl":
                            return control
                        
                        for child in control.GetChildren():
                            result = find_list_control(child)
                            if result:
                                return result
                        return None
                    except Exception as e:
                        print(f"检查控件时出错: {e}")
                        return None
                
                print("查找列表控件...")
                list_control = find_list_control(target_window)
                
                if not list_control:
                    print("未找到列表控件，将在5秒后重试...")
                    time.sleep(5)
                    continue  # 继续外层循环，重新查找窗口
                
                print("找到列表控件，开始监控内容...")
                
                # 内层循环：监控已找到的窗口
                while True:
                    try:
                        items = manager._collect_all_content(list_control)
                        if items and manager.update_transcripts(items):
                            print(f"\n检测到新内容，当前总条目数: {len(manager.transcripts)}")
                            manager.print_all_transcripts()
                        
                        time.sleep(1)
                        
                        if not win32gui.IsWindow(target_hwnd):
                            print("转录窗口已关闭，重新开始查找...")
                            break
                        
                    except Exception as e:
                        print(f"监控过程中出错: {e}")
                        time.sleep(1)
                        continue

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"发生错误: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(5)
                
    except Exception as e:
        print(f"监控循环出错: {e}")

if __name__ == "__main__":
    monitor_transcript()