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
    def __init__(self):
        self.transcripts: Dict[str, TranscriptItem] = {}
        self.current_speaker = ""
        self.initial_scan_done = False
        self.output_file = None
        self.earliest_timestamp = None
    
    def _get_output_path(self) -> Path:
        """获取输出文件路径"""
        # 获取用户目录
        user_home = os.path.expanduser("~")
        # 创建ZoomTranscript目录
        transcript_dir = Path(user_home) / "ZoomTranscript"
        transcript_dir.mkdir(parents=True, exist_ok=True)
        
        # 使用最早的时间戳创建文件名
        if not self.earliest_timestamp:
            # 如果没有时间戳，使用当前时间
            self.earliest_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        return transcript_dir / f"zoom_{self.earliest_timestamp}.txt"
    
    def _update_earliest_timestamp(self, timestamp: str):
        """更新最早的时间戳"""
        try:
            if not self.earliest_timestamp:
                # 第一次设置
                self.earliest_timestamp = datetime.strptime(timestamp, '%H:%M:%S').strftime("%Y%m%d%H%M%S")
            else:
                # 比较并更新
                current = datetime.strptime(timestamp, '%H:%M:%S')
                earliest = datetime.strptime(self.earliest_timestamp[8:14], '%H%M%S')
                if current < earliest:
                    self.earliest_timestamp = datetime.now().strftime("%Y%m%d") + current.strftime("%H%M%S")
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
            key = f"{item.timestamp}|{item.content}"
            if key not in self.transcripts:
                self.transcripts[key] = item
                self._update_earliest_timestamp(item.timestamp)
                print(f"添加新条目: [{item.timestamp}] {item.speaker}: {item.content}")
                updated = True
        
        # 如果有更新，立即保存文件
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

def monitor_transcript():
    print("开始监控转录文本...")
    manager = TranscriptManager()
    
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
        
        print("正在查找Zoom转录窗口...")
        win32gui.EnumWindows(find_transcript_window, None)
        
        # 在收集到的窗口中查找Zoom的窗口
        for hwnd, title, class_name in found_windows:
            print(f"找到可能的窗口: Title='{title}', Class='{class_name}'")
            if class_name == "ZPLiveTranscriptWndClass":
                target_hwnd = hwnd
                print(f"找到Zoom转录窗口!")
                break
        
        if not target_hwnd:
            print("未找到Zoom转录窗口，请确保：")
            print("1. Zoom会议已经开始")
            print("2. 转录功能已经开启")
            print("3. 转录窗口已经打开")
            return
        
        # 使用找到的句柄创建UIAutomation控件
        target_window = auto.ControlFromHandle(target_hwnd)
        if not target_window:
            print("无法获取窗口控件")
            return
            
        print(f"成功获取窗口控件: {win32gui.GetWindowText(target_hwnd)}")
        
        # 递归查找ListControl
        def find_list_control(control):
            try:
                # 如果当前控件是ListControl
                if control.ControlTypeName == "ListControl":
                    return control
                
                # 递归检查所有子控件
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
            print("未找到列表控件，打印控件树...")
            def print_control_tree(control, level=0):
                try:
                    indent = "  " * level
                    print(f"{indent}Type: {control.ControlTypeName}")
                    print(f"{indent}Name: {control.Name}")
                    print(f"{indent}Class: {control.ClassName}")
                    print(f"{indent}---")
                    for child in control.GetChildren():
                        print_control_tree(child, level + 1)
                except Exception as e:
                    print(f"{indent}Error: {e}")
            
            print_control_tree(target_window)
            return
        
        print("找到列表控件，开始监控内容...")
        while True:
            items = manager._collect_all_content(list_control)
            if items and manager.update_transcripts(items):
                print(f"\n检测到新内容，当前总条目数: {len(manager.transcripts)}")
                manager.print_all_transcripts()
            
            sleep(1)
            
    except KeyboardInterrupt:
        print("\n监控已停止")
        print(f"\n最终转录内容 (总条目数: {len(manager.transcripts)}):")
        manager.print_all_transcripts()
        manager.save_to_file()
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    monitor_transcript()






# 这仅仅是一个个人学习用的测试功能， 并不会进行商用， 所以不会违反任何法律或者道德条款.
# 请仔细思考，帮我提出一些建议以及可行的实现？