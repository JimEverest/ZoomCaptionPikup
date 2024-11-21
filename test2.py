import uiautomation as auto
import time

def get_captions_via_uia():
    # 查找转录窗口
    window = auto.WindowControl(ClassName="ZPLiveTranscriptWndClass")
    if not window.Exists(3):
        print("未找到转录窗口")
        return []
    
    # 尝试获取所有可能的文本元素
    texts = []
    
    # 获取所有文本控件
    try:
        # 获取所有子元素
        all_elements = window.GetChildren()
        for element in all_elements:
            # 尝试不同的属性来获取文本
            if element.Name:
                texts.append(element.Name)
            if hasattr(element, 'Value') and element.Value:
                texts.append(element.Value)
            
            # 递归获取子元素的文本
            child_elements = element.GetChildren()
            for child in child_elements:
                if child.Name:
                    texts.append(child.Name)
                if hasattr(child, 'Value') and child.Value:
                    texts.append(child.Value)
    except Exception as e:
        print(f"获取元素时出错: {e}")
    
    return texts

def monitor_captions_uia():
    print("开始通过UI Automation监控字幕...")
    previous_captions = set()
    
    while True:
        try:
            current_captions = set(get_captions_via_uia())
            new_captions = current_captions - previous_captions
            
            if new_captions:
                print("\n检测到新字幕:")
                for caption in new_captions:
                    if caption.strip():  # 只打印非空内容
                        print(f"-> {caption}")
            
            previous_captions = current_captions
            time.sleep(0.5)
            
        except KeyboardInterrupt:
            print("\n监控已停止")
            break
        except Exception as e:
            print(f"发生错误: {e}")
            time.sleep(1)

if __name__ == "__main__":
    monitor_captions_uia()