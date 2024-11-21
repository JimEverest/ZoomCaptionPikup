import win32gui
import win32con
import win32api
from ctypes import windll, byref, create_unicode_buffer, create_string_buffer
import array

def get_window_text_with_buffer(hwnd):
    """使用虚拟缓冲区获取窗口文本"""
    try:
        # 获取窗口类名
        class_name = create_unicode_buffer(256)
        win32gui.GetClassName(hwnd, class_name)
        
        # 如果是编辑框或富文本框，使用EM_GETTEXT
        if class_name.value in ['Edit', 'RichEdit20W']:
            length = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0) + 1
            buffer = create_unicode_buffer(length)
            win32gui.SendMessage(hwnd, win32con.EM_GETTEXT, length, buffer)
            return buffer.value
        
        # 获取虚拟缓冲区大小
        buffer_size = windll.user32.SendMessageW(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0) + 1
        buffer = create_unicode_buffer(buffer_size)
        
        # 获取文本
        windll.user32.SendMessageW(hwnd, win32con.WM_GETTEXT, buffer_size, buffer)
        return buffer.value
    except Exception as e:
        print(f"获取文本时出错: {e}")
        return ""

# ... [其余代码保持不变] ... 