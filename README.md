# Meeting Navigator

An intelligent meeting assistant that combines real-time Zoom caption capturing with AI-powered meeting analysis and guidance. This tool helps you stay focused, understand key points, and navigate meetings effectively.

## Key Features

### Real-time Transcript Capture
- Automatically detects and monitors Zoom caption window
- Captures speaker names, timestamps, and dialogue content
- Smart deduplication for accurate transcript recording
- Auto-recovery from window loss or disconnection

### AI-Powered Meeting Analysis
- **Live Summary**: Real-time meeting content summarization
- **Viewpoint Analysis**: Tracks each participant's key points and perspectives
- **Navigation Guidance**: Provides strategic suggestions for your next contribution
- **Meeting Minutes**: Generates structured meeting documentation

### Smart UI Design
- Expandable/collapsible sections for better space utilization
- Real-time content updates with smooth animations
- Progress indicators for AI processing tasks
- Configurable layout to focus on what matters most

### Customization & Control
- Adjustable update frequency for live features
- Language selection for multilingual support
- Configurable meeting context and parameters
- Flexible note-taking capabilities

## Technical Highlights

- **Asynchronous Processing**: Non-blocking UI with background AI processing
- **Intelligent Deduplication**: Smart handling of incremental caption updates
- **Robust Error Handling**: Automatic recovery from various failure scenarios
- **Configurable Prompts**: Customizable AI interaction templates

## System Requirements

- Windows 10 or later
- Python 3.6+
- Zoom client with live caption feature enabled
- Internet connection for AI features

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your API settings in `config.ini`

## Usage

1. Start a Zoom meeting with captions enabled
2. Launch Meeting Navigator:
   ```bash
   python meeting_navigator.py
   ```
3. Input meeting context and parameters
4. Enable live features as needed

## Configuration

The `config.ini` file allows you to customize:
- Default meeting parameters
- AI prompt templates
- UI preferences
- API settings

## Key Benefits

- **Enhanced Meeting Engagement**: Stay focused on the discussion with real-time AI assistance
- **Strategic Communication**: Get AI-powered suggestions for impactful contributions
- **Comprehensive Documentation**: Automatic capture and organization of meeting content
- **Time Efficiency**: Reduce note-taking burden with automated features
- **Flexible Operation**: Work seamlessly with your existing Zoom meetings

## Development Status

This project is actively maintained and enhanced. Current focus areas:
- Enhanced AI analysis capabilities
- Additional customization options
- Performance optimizations
- UI/UX improvements

## License

MIT License - feel free to use and modify for your needs.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for improvements.

## Acknowledgments

Built with:
- Python Tkinter for UI
- GPT-4 for AI analysis
- Windows UI Automation for caption capture
- Various open-source libraries

---

**Note**: This tool is designed for educational and research purposes. Please ensure compliance with Zoom's terms of service and relevant privacy regulations in your use case.