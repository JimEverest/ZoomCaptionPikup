import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from datetime import datetime
import queue
import uiautomation as auto
from test import TranscriptManager, monitor_transcript
import re

class MeetingNavigator:
    def __init__(self, root):
        self.root = root
        self.root.title("Meeting Navigator")
        self.root.geometry("1200x800")
        
        # 创建消息队列用于线程间通信
        self.message_queue = queue.Queue()
        
        # 初始化Transcript相关变量
        self.transcript_thread = None
        self.transcript_manager = None
        self.last_update = datetime.now()
        
        # 初始化变量
        self.init_variables()
        
        # 创建主分割区域
        self.create_main_layout()
        
        # 启动UI更新循环
        self.update_ui()
        
        # 启动转录监控
        self.start_transcript_monitor()
    
    def init_variables(self):
        """初始化所有变量"""
        # 折叠状态变量
        self.summary_expanded = tk.BooleanVar(value=True)
        self.views_expanded = tk.BooleanVar(value=True)
        self.nav_expanded = tk.BooleanVar(value=True)
        
        # 控制栏变量
        self.duration_var = tk.StringVar(value="60min")
        self.username_var = tk.StringVar()
        self.language_var = tk.StringVar(value="En")
        self.freq_var = tk.StringVar(value="30")
        self.live_var = tk.BooleanVar(value=False)
    
    def create_main_layout(self):
        """创建主布局"""
        # 创建左右分割的主面板
        self.main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧面板
        left_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(left_frame, weight=1)
        
        # 右侧面板
        right_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(right_frame, weight=1)
        
        # 创建左侧内容
        self.create_left_panel(left_frame)
        # 创建右侧内容
        self.create_right_panel(right_frame)
    
    def create_left_panel(self, parent):
        """创建左侧面板"""
        # Live Transcript区域
        transcript_frame = ttk.LabelFrame(parent, text="Live Transcript")
        transcript_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.transcript_text = scrolledtext.ScrolledText(transcript_frame)
        self.transcript_text.pack(fill=tk.BOTH, expand=True)
        
        # Live Summary区域（可折叠）
        self.summary_frame = ttk.LabelFrame(parent, text="Live Summary")
        self.summary_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        summary_header = ttk.Frame(self.summary_frame)
        summary_header.pack(fill=tk.X)
        ttk.Label(summary_header, text="Click to expand/collapse").pack(side=tk.LEFT)
        ttk.Checkbutton(summary_header, variable=self.summary_expanded,
                       command=self.toggle_summary).pack(side=tk.RIGHT)
        
        self.summary_text = scrolledtext.ScrolledText(self.summary_frame, height=6)
        self.summary_text.pack(fill=tk.BOTH, expand=True)
        
        # Each one's view区域（可折叠）
        self.views_frame = ttk.LabelFrame(parent, text="Each one's view")
        self.views_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        views_header = ttk.Frame(self.views_frame)
        views_header.pack(fill=tk.X)
        ttk.Label(views_header, text="Click to expand/collapse").pack(side=tk.LEFT)
        ttk.Checkbutton(views_header, variable=self.views_expanded,
                       command=self.toggle_views).pack(side=tk.RIGHT)
        
        self.views_text = scrolledtext.ScrolledText(self.views_frame, height=6)
        self.views_text.pack(fill=tk.BOTH, expand=True)
        
        # Navigation guidance区域（可折叠）
        self.nav_frame = ttk.LabelFrame(parent, text="Navigation guidance")
        self.nav_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        nav_header = ttk.Frame(self.nav_frame)
        nav_header.pack(fill=tk.X)
        ttk.Label(nav_header, text="Click to expand/collapse").pack(side=tk.LEFT)
        ttk.Checkbutton(nav_header, variable=self.nav_expanded,
                       command=self.toggle_nav).pack(side=tk.RIGHT)
        
        self.nav_text = scrolledtext.ScrolledText(self.nav_frame, height=6)
        self.nav_text.pack(fill=tk.BOTH, expand=True)
    
    def toggle_summary(self):
        """切换Summary区域的展开/折叠状态"""
        if self.summary_expanded.get():
            self.summary_text.pack(fill=tk.BOTH, expand=True)
        else:
            self.summary_text.pack_forget()
        self.adjust_transcript_height()
    
    def toggle_views(self):
        """切换Views区域的展开/折叠状态"""
        if self.views_expanded.get():
            self.views_text.pack(fill=tk.BOTH, expand=True)
        else:
            self.views_text.pack_forget()
        self.adjust_transcript_height()
    
    def toggle_nav(self):
        """切换Navigation区域的展开/折叠状态"""
        if self.nav_expanded.get():
            self.nav_text.pack(fill=tk.BOTH, expand=True)
        else:
            self.nav_text.pack_forget()
        self.adjust_transcript_height()
    
    def adjust_transcript_height(self):
        """调整Transcript区域的高度"""
        collapsed_count = (not self.summary_expanded.get()) + \
                         (not self.views_expanded.get()) + \
                         (not self.nav_expanded.get())
        self.transcript_text.configure(height=10 + collapsed_count * 6)
    
    def get_context(self):
        """获取所有上下文信息"""
        return {
            "duration": self.duration_var.get(),
            "username": self.username_var.get(),
            "language": self.language_var.get(),
            "live_freq": self.freq_var.get(),
            "live_on": self.live_var.get(),
            "context": self.context_text.get("1.0", tk.END).strip(),
            "agenda": self.agenda_text.get("1.0", tk.END).strip(),
            "topics": self.topics_text.get("1.0", tk.END).strip(),
            "stakeholders": self.stakeholders_text.get("1.0", tk.END).strip(),
            "notes": self.notes_text.get("1.0", tk.END).strip()
        }
    
    def update_transcript_display(self, transcript_item):
        """更新转录内容显示"""
        try:
            # 获取当前显示的最后一行
            last_line = self.transcript_text.get("end-2c linestart", "end-1c")
            if last_line:
                # 解析最后一行的时间戳和说话者
                match = re.match(r'\[([\d:]+)\] ([^:]+):', last_line)
                if match:
                    last_timestamp, last_speaker = match.groups()
                    # 如果新内容与最后一行来自同一时间和说话者，则替换最后一行
                    if (transcript_item.timestamp == last_timestamp and 
                        transcript_item.speaker == last_speaker):
                        self.transcript_text.delete("end-2c linestart", "end-1c")
            
            # 追加新内容
            self.transcript_text.insert(tk.END, f"{transcript_item.to_string()}\n")
            self.transcript_text.see(tk.END)  # 自动滚动到底部
            
        except Exception as e:
            print(f"更新转录显示错误: {e}")
    
    def create_right_panel(self, parent):
        """创建右侧面板"""
        # 顶部控制栏
        self.create_control_bar(parent)
        
        # Meeting Context
        context_frame = ttk.LabelFrame(parent, text="Meeting Context")
        context_frame.pack(fill=tk.X, padx=5, pady=5)
        self.context_text = scrolledtext.ScrolledText(context_frame, height=4)
        self.context_text.pack(fill=tk.BOTH, expand=True)
        
        # Meeting Agenda/Target
        agenda_frame = ttk.LabelFrame(parent, text="Meeting Agenda/Target")
        agenda_frame.pack(fill=tk.X, padx=5, pady=5)
        self.agenda_text = scrolledtext.ScrolledText(agenda_frame, height=4)
        self.agenda_text.pack(fill=tk.BOTH, expand=True)
        
        # Meeting Topics
        topics_frame = ttk.LabelFrame(parent, text="Meeting Topics")
        topics_frame.pack(fill=tk.X, padx=5, pady=5)
        self.topics_text = scrolledtext.ScrolledText(topics_frame, height=4)
        self.topics_text.pack(fill=tk.BOTH, expand=True)
        
        # Meeting Stakeholders
        stakeholders_frame = ttk.LabelFrame(parent, text="Meeting Stakeholders")
        stakeholders_frame.pack(fill=tk.X, padx=5, pady=5)
        self.stakeholders_text = scrolledtext.ScrolledText(stakeholders_frame, height=4)
        self.stakeholders_text.pack(fill=tk.BOTH, expand=True)
        
        # Notes
        notes_frame = ttk.LabelFrame(parent, text="Notes")
        notes_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.notes_text = scrolledtext.ScrolledText(notes_frame, height=4)
        self.notes_text.pack(fill=tk.BOTH, expand=True)
        
        # 底部按钮栏
        self.create_button_bar(parent)
    
    def create_control_bar(self, parent):
        """创建顶部控制栏"""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Duration
        ttk.Label(control_frame, text="Duration").pack(side=tk.LEFT, padx=2)
        self.duration_var = tk.StringVar(value="60min")
        ttk.Combobox(control_frame, textvariable=self.duration_var, 
                    values=["30min", "60min", "90min", "120min"], 
                    width=8).pack(side=tk.LEFT, padx=2)
        
        # For (username)
        ttk.Label(control_frame, text="For").pack(side=tk.LEFT, padx=2)
        self.username_var = tk.StringVar()
        ttk.Entry(control_frame, textvariable=self.username_var, 
                 width=15).pack(side=tk.LEFT, padx=2)
        
        # Language
        ttk.Label(control_frame, text="Language").pack(side=tk.LEFT, padx=2)
        self.language_var = tk.StringVar(value="En")
        ttk.Entry(control_frame, textvariable=self.language_var,
                 width=5).pack(side=tk.LEFT, padx=2)
        
        # LIVE Freq
        ttk.Label(control_frame, text="LIVE Freq").pack(side=tk.LEFT, padx=2)
        self.freq_var = tk.StringVar(value="30")
        ttk.Entry(control_frame, textvariable=self.freq_var,
                 width=5).pack(side=tk.LEFT, padx=2)
        
        # LIVE on switch
        self.live_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(control_frame, text="LIVE on",
                       variable=self.live_var).pack(side=tk.LEFT, padx=2)
    
    def create_button_bar(self, parent):
        """创建底部按钮栏"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 右对齐按钮
        ttk.Button(button_frame, text="Save", 
                  command=self.save_all).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Summarize", 
                  command=self.manual_summarize).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Viewpoints", 
                  command=self.manual_viewpoints).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Navigate", 
                  command=self.manual_navigation).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Submit", 
                  command=self.submit_all).pack(side=tk.RIGHT, padx=5)
    
    def start_transcript_monitor(self):
        """启动转录监控线程"""
        def run_monitor():
            try:
                with auto.UIAutomationInitializerInThread():
                    # 直接使用monitor_transcript的返回值作为transcript_manager
                    self.transcript_manager = monitor_transcript(
                        lambda msg_type, content: self.message_queue.put((msg_type, content))
                    )
            except Exception as e:
                self.message_queue.put(("error", f"Transcript monitor error: {str(e)}"))
        
        if self.transcript_thread is None or not self.transcript_thread.is_alive():
            self.transcript_thread = threading.Thread(target=run_monitor)
            self.transcript_thread.daemon = True
            self.transcript_thread.start()
    
    def update_ui(self):
        """更新UI的周期性任务"""
        try:
            # 处理消息队列中的消息
            while not self.message_queue.empty():
                msg_type, msg_content = self.message_queue.get_nowait()
                if msg_type == "transcript":  # 改回原来的消息类型
                    self.update_transcript_display(msg_content)
                elif msg_type == "error":
                    self.show_error(msg_content)
            
            # 如果实时功能开启，执行实时更新
            if self.live_var.get():
                self.update_live_features()
            
            # 继续周期性更新
            self.root.after(1000, self.update_ui)
            
        except Exception as e:
            print(f"UI更新错误: {e}")
            self.root.after(1000, self.update_ui)
    
    def update_live_features(self):
        """更新实时功能"""
        try:
            # 获取更新频率
            freq = int(self.freq_var.get())
            current_time = datetime.now()
            
            # 检查是否需要更新
            if (current_time - self.last_update).total_seconds() >= freq:
                self.manual_summarize()
                self.manual_viewpoints()
                self.manual_navigation()
                self.last_update = current_time
        except Exception as e:
            print(f"实时更新错误: {e}")
    
    def show_error(self, error_message):
        """显示错误消息"""
        # 这里可以实现错误提示UI
        print(f"Error: {error_message}")
    
    # 按钮回调函数
    def save_all(self):
        """保存所有内容"""
        try:
            # 保存会议信息
            meeting_info = {
                "context": self.context_text.get("1.0", tk.END).strip(),
                "agenda": self.agenda_text.get("1.0", tk.END).strip(),
                "topics": self.topics_text.get("1.0", tk.END).strip(),
                "stakeholders": self.stakeholders_text.get("1.0", tk.END).strip(),
                "notes": self.notes_text.get("1.0", tk.END).strip()
            }
            # TODO: 实现保存逻辑
            print("保存成功")
        except Exception as e:
            self.show_error(f"保存失败: {str(e)}")
    
    def manual_summarize(self):
        """手动触发总结"""
        try:
            # TODO: 调用LLM进行总结
            dummy_summary = "This is a dummy summary..."
            self.summary_text.delete("1.0", tk.END)
            self.summary_text.insert("1.0", dummy_summary)
        except Exception as e:
            self.show_error(f"总结生成失败: {str(e)}")
    
    def manual_viewpoints(self):
        """手动触发观点分析"""
        try:
            # TODO: 调用LLM进行观点分析
            dummy_viewpoints = "These are dummy viewpoints..."
            self.views_text.delete("1.0", tk.END)
            self.views_text.insert("1.0", dummy_viewpoints)
        except Exception as e:
            self.show_error(f"观点分析失败: {str(e)}")
    
    def manual_navigation(self):
        """手动触发导航建议"""
        try:
            # TODO: 调用LLM生成导航建议
            dummy_navigation = "This is a dummy navigation guidance..."
            self.nav_text.delete("1.0", tk.END)
            self.nav_text.insert("1.0", dummy_navigation)
        except Exception as e:
            self.show_error(f"导航建议生成失败: {str(e)}")
    
    def submit_all(self):
        """提交所有内容"""
        try:
            # TODO: 实现提交逻辑
            print("提交成功")
        except Exception as e:
            self.show_error(f"提交失败: {str(e)}")

def main():
    root = tk.Tk()
    app = MeetingNavigator(root)
    root.mainloop()

if __name__ == "__main__":
    main()