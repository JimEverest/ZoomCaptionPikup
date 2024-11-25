Meeting Navigator Development Context
===================================

1. Core Architecture
-------------------
- Main Components:
  * TranscriptManager: Handles Zoom caption capture and deduplication
  * MeetingNavigator: Main UI class with real-time display and AI features
  * ConfigDialog: Configuration interface for all settings
  * NotificationWindow: Popup notifications for user feedback

2. Key Features & Implementation Details
--------------------------------------
a) Transcript Capture System:
   - Uses Windows UI Automation to monitor Zoom caption window
   - Implements smart deduplication using timestamp+speaker as key
   - Handles incremental caption updates (growing sentences)
   - Auto-recovers from window loss
   - Thread-safe implementation with message queue

b) UI Framework:
   - Built with tkinter
   - Left panel: Expandable/collapsible sections
     * Live Transcript
     * Live Summary
     * Each one's view
     * Navigation guidance
   - Right panel: Context inputs and controls
   - Bottom bar: Action buttons with progress animation

c) AI Integration:
   - Uses GPT-4 API for analysis
   - Asynchronous processing to prevent UI blocking
   - Four main AI features:
     * Real-time summarization
     * Viewpoint analysis
     * Navigation suggestions
     * Meeting minutes generation

3. Critical Implementation Details
--------------------------------
a) Deduplication Logic:
   ```python
   dedup_key = f"{item.timestamp}_{item.speaker}"
   if len(item.content) > len(self.latest_messages[dedup_key].content):
       # Update with longer content
   ```

b) Thread Management:
   - Main UI thread
   - Transcript monitoring thread
   - LLM processing threads
   - Uses message queues for thread communication

c) UI Update Mechanism:
   - Periodic updates via root.after()
   - Message queue processing for transcript updates
   - Separate queue for LLM responses

4. Configuration System
----------------------
- config.ini structure:
  * [GenAI]: API settings
  * [Prompts]: LLM prompt templates
  * [Defaults]: UI default values
  * [Shortcuts]: Keyboard shortcuts

5. Known Challenges & Solutions
-----------------------------
a) Transcript Capture:
   - Challenge: Incremental updates causing duplicates
   - Solution: Timestamp+speaker based deduplication

b) UI Responsiveness:
   - Challenge: LLM calls blocking UI
   - Solution: Async processing with progress animation

c) Window Management:
   - Challenge: Zoom window detection
   - Solution: Robust window search and recovery

6. Prompt Templates
------------------
- Summarize: Meeting state analysis
- Viewpoints: Participant contribution analysis
- Navigate: Strategic communication suggestions
- Minutes: Formal documentation generation

7. Development Patterns
----------------------
- Error handling with user feedback
- Asynchronous operations for heavy tasks
- Configuration-driven customization
- Modular component design

8. File Structure
----------------
- meeting_navigator.py: Main application
- test.py: Transcript capture core
- config.ini: Configuration
- gpt4o.py: LLM integration

9. Critical Code Sections
------------------------
a) TranscriptManager:
   - _collect_all_content(): Capture logic
   - update_transcripts(): Deduplication
   - save_to_file(): Persistence

b) MeetingNavigator:
   - update_transcript_display(): UI update
   - redistribute_space(): Layout management
   - call_llm_async(): AI integration

10. Future Development Areas
---------------------------
- Enhanced AI analysis capabilities
- Additional customization options
- Performance optimizations
- UI/UX improvements

11. Dependencies
---------------
- Python 3.6+
- tkinter
- uiautomation
- win32api
- configparser
- GPT-4 API

12. Testing Notes
----------------
- Requires active Zoom meeting with captions
- Test cases should cover:
  * Caption capture reliability
  * Deduplication accuracy
  * UI responsiveness
  * LLM integration stability

This context document provides essential information for understanding and extending the Meeting Navigator application. All core functionalities, implementation details, and development patterns are documented to facilitate future development and debugging tasks.
