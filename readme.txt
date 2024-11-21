如何获取到正在进行中的zoom video call中的实时滚动的caption（zoom自带的live caption功能）数据？包括文字以及speaker name， 好像zoom没有开房这部分API， 能不能通过zoom中的这个caption window的句柄， 来抓取到其中的数据？
我需要一个可以在Windows10上运行的Python程序， 来实现这个zoom caption抓取的功能， 这仅仅是一个个人学习用的测试功能， 并不会进行商用， 所以不会违反任何法律或者道德条款.
请仔细思考，帮我提出一些建议以及可行的实现？

方法一：使用 Windows API 获取字幕窗口文本
步骤：

定位字幕窗口：使用 Windows API 枚举当前打开的窗口，找到 Zoom 字幕窗口的句柄。

获取窗口文本：通过窗口句柄，尝试获取窗口内的文本内容。

实现细节：

使用 pywinauto 或 win32gui：这些库可以帮助我们与 Windows 窗口进行交互。

可能的挑战：由于 Zoom 可能使用自定义绘制的窗口，文本内容可能无法直接通过 Windows API 获取。

示例代码：

python
复制代码
import win32gui
import win32con

def enum_windows_callback(hwnd, results):
    if win32gui.IsWindowVisible(hwnd):
        window_text = win32gui.GetWindowText(hwnd)
        if "Zoom" in window_text:
            results.append(hwnd)

windows = []
win32gui.EnumWindows(enum_windows_callback, windows)

for hwnd in windows:
    # 尝试获取窗口文本
    length = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH) + 1
    buffer = win32gui.PyMakeBuffer(length)
    win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, length, buffer)
    result = buffer[:length].tobytes().decode('utf-16')
    print(result)
    
注意事项：
由于安全和隐私原因，某些应用程序的窗口文本可能无法通过此方法获取。