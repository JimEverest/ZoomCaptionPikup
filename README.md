# Zoom Caption Grabber

一个用于实时捕获和记录Zoom会议字幕的Python工具。该工具可以自动监控Zoom的实时字幕窗口，捕获所有对话内容，并将其保存为文本文件。

## 功能特点

- 自动检测和监控Zoom字幕窗口
- 实时捕获字幕内容，包括说话者、时间戳和对话内容
- 智能去重处理，避免重复内容
- 自动保存为格式化的文本文件
- 支持窗口丢失后自动重新检测
- 支持会议过程中的实时监控和更新

## 系统要求

- Windows 10 或更高版本
- Python 3.6+
- Zoom 客户端（需要启用实时字幕功能）

## 依赖库

```bash
pip install uiautomation
pip install pywin32
```

## 安装步骤

1. 克隆或下载本项目到本地
2. 安装所需的依赖库：
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

1. 启动Zoom会议并开启实时字幕功能
2. 确保字幕窗口处于打开状态
3. 运行脚本：
   ```bash
   python test.py
   ```
4. 程序会自动检测字幕窗口并开始监控
5. 捕获的内容会自动保存在用户目录的 `ZoomTranscript` 文件夹中

## 输出文件

- 文件保存路径：`~/ZoomTranscript/`
- 文件命名格式：`zoom_YYYY-MMM-DD_HH-MM-SS_HH-MM-SS.txt`
  - 第一个时间戳为录制开始时间
  - 第二个时间戳为录制结束时间
- 文件内容格式：`[时间戳] 说话者: 内容`

## 注意事项

1. 确保Zoom会议已经开始并且字幕功能已开启
2. 字幕窗口必须保持打开状态
3. 不要最小化字幕窗口
4. 程序运行期间请勿手动关闭字幕窗口
5. 如果字幕窗口意外关闭，程序会自动尝试重新检测

## 常见问题

1. **找不到字幕窗口**
   - 确认Zoom会议是否已开始
   - 检查字幕功能是否已启用
   - 确保字幕窗口处于打开状态

2. **内容重复**
   - 程序内置了智能去重机制
   - 只有更长/更新的内容才会被记录

3. **程序无响应**
   - 检查Zoom是否正常运行
   - 重启程序重新尝试

## 开发说明

- `TranscriptManager` 类负责核心功能实现
- `monitor_transcript()` 函数处理窗口监控和数据采集
- 使用 Windows API 和 UI Automation 进行窗口操作
- 采用实时保存机制，确保数据安全

## 免责声明

本工具仅供学习和研究使用，请遵守相关法律法规和Zoom的使用条款。不得用于任何商业用途。

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进这个项目。

## 许可证

MIT License











这个app的使命是实现会议助手， 即除了获取transcript之外， 还提供一些实时的summary， 每个人的观点总结， 会议导航， 会议纪要总结， 保存等功能。 

1. 实时的summary
	根据当前所有transcript， 实时总结出summary
2. 实时的每个人的观点总结
	实时的总结每个人的主要观点， 以及User应该采取的对话策略
3. **实时会议导航**
	需要根据一些会议策略和议题， 以及当前的所有transcript， 从以下方面进行分析， 并提出建议来建议User下一步的发言内容。
	输入项： 会议主题(Text Box)， 会议目标(Text Area)， User name(Text box)， 会议时长(drop down),  实时建议频率(text box)， 实时功能开关(slider).
4. 会议纪要总结：
	将transcript整理成MM
5. 保存按钮：
	- 保存Transcript, my performance review,Retrospective review,  每个人的观点总结, Meeting Minutes 等等

对于summary， 观点总结， 会议导航等等功能， 我准备用LLM（GPT4o API）来实现（暂时先不用实现这几个具体的功能，只需要一个简单dummy函数模拟即可）。
第一步， 我需要实现一个UI， 来显示几个区块：
1. 实时的显示区， 包括transcript， summary， 每个人的观点， 导航区
2. 输入区 会议主题， 目标， 背景， 关键人物，语言选择（Textbox） ， 备注
3. 操作按钮区（保存， 手动调用各项实时功能的按钮等）

注意: 请确保现在的已有的功能正常工作， 不要修改现有transcript获取功能！
可以小幅修改，稳步迭代， 千万不要将程序改的面目全非无法正常运行！！