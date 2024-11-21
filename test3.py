import uiautomation as auto
from time import sleep

def get_transcript_text():
    # 查找转录窗口
    window = auto.WindowControl(ClassName="ZPLiveTranscriptWndClass")
    if not window.Exists(3):
        return None
    
    all_text = []
    
    # 递归获取所有文本
    def collect_text(element):
        # 获取当前元素的文本
        if element.Name and element.Name not in ["关闭", "最小化", "最大化", "系统"]:
            all_text.append(element.Name)
        
        # 检查是否有TextPattern
        try:
            text_pattern = element.GetTextPattern()
            if text_pattern:
                text = text_pattern.DocumentRange.GetText(-1)
                if text:
                    all_text.append(text)
        except:
            pass
        
        # 检查ValuePattern
        try:
            value_pattern = element.GetValuePattern()
            if value_pattern and value_pattern.Value:
                all_text.append(value_pattern.Value)
        except:
            pass
        
        # 递归处理所有子元素
        for child in element.GetChildren():
            collect_text(child)
    
    try:
        # 获取所有可能的文本内容
        collect_text(window)
        
        # 过滤和清理文本
        filtered_text = [t for t in all_text if t.strip() and 
                        t not in ["关闭", "最小化", "最大化", "系统"]]
        
        if filtered_text:
            return "\n".join(filtered_text)
    except Exception as e:
        print(f"获取文本时出错: {e}")
    
    return None

def monitor_transcript():
    print("开始监控转录文本...")
    last_text = ""
    
    while True:
        try:
            # 获取文本
            text = get_transcript_text()
            
            # 如果有新文本且不同于上次的文本
            if text and text != last_text:
                # 分割成行并过滤掉空行和系统按钮文本
                lines = [line.strip() for line in text.split('\n') 
                        if line.strip() and 
                        line.strip() not in ["关闭", "最小化", "最大化", "系统"]]
                
                if lines:
                    print("\n新文本:")
                    for line in lines:
                        print(f"-> {line}")
                    last_text = text
            
            sleep(0.5)
            
        except KeyboardInterrupt:
            print("\n监控已停止")
            break
        except Exception as e:
            print(f"错误: {e}")
            sleep(1)

def print_element_tree(element, level=0):
    """调试用：打印元素树结构"""
    print("  " * level + f"Name: {element.Name}, Class: {element.ClassName}, AutomationId: {element.AutomationId}")
    for child in element.GetChildren():
        print_element_tree(child, level + 1)

if __name__ == "__main__":
    # 如果需要调试，取消下面的注释
    # window = auto.WindowControl(ClassName="ZPLiveTranscriptWndClass")
    # if window.Exists(3):
    #     print("窗口结构:")
    #     print_element_tree(window)
    # else:
    #     print("未找到窗口")
    
    monitor_transcript() 