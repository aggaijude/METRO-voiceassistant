METRO – VOICE ASSISTANT
Mini Project Documentation
--------------------------------------------------

Project Title:
METRO – Intelligent Voice Assistant with UI

Developed By:
Team Ragnarok

Team Members:
- Aggai Jude
- Nanda Krishnan A J
- Shravan

--------------------------------------------------
PROJECT DESCRIPTION
--------------------------------------------------
METRO is a desktop-based intelligent voice assistant developed using Python.
It provides real-time voice interaction, a graphical HUD-style interface,
and intelligent response generation using an online AI model.

The assistant is designed to:
- Interact with users through voice
- Respond in multiple languages
- Acknowledge system-level commands
- Provide a smooth and friendly user experience

--------------------------------------------------
KEY FEATURES
--------------------------------------------------
- Real-time voice input and output
- Interactive Metro-style animated UI
- Multilingual support (Tamil,English, Malayalam, Hindi, etc.)
- Natural and friendly conversation style
- Logical system command handling (open apps, volume control, etc.)
- Modular and extensible architecture

--------------------------------------------------
TECHNOLOGIES USED
--------------------------------------------------
Programming Language:
- Python 3.x

Libraries & Frameworks:
- LiveKit Agents
- Google Realtime AI Model
- PySide6 (GUI)
- NumPy
- SoundDevice
- python-dotenv

--------------------------------------------------
PROJECT STRUCTURE
--------------------------------------------------
agent.py          -> Main application file
.env              -> API keys and configuration
requirements.txt  -> Required Python packages
README.txt        -> Project documentation
run.py            -> Start METRO 

--------------------------------------------------
HOW TO RUN THE PROJECT
--------------------------------------------------
1. Open Command Prompt or PowerShell
2. Navigate to the project folder:
   cd "C:\path\to\project"

3. Activate virtual environment:
   .\venv\Scripts\activate 
   if venv is set otherwise:
   python -m venv venv

4. Run the assistant:
   python run.pyw

--------------------------------------------------
USAGE INSTRUCTIONS
--------------------------------------------------
Speak naturally to the assistant.

Example commands:
- "Metro open Chrome"
- "Increase volume"
- "Who developed you?"

--------------------------------------------------
NOTE ON SYSTEM COMMANDS
--------------------------------------------------
Due to operating system security restrictions on Windows,
system-level actions are acknowledged logically by the assistant.
Actual execution depends on OS permissions and environment policies.

--------------------------------------------------
ACADEMIC NOTE
--------------------------------------------------
This project is developed as a mini project for academic purposes.
It demonstrates concepts of:
- Voice-based interaction
- AI-driven intent recognition
- User interface design
- System command routing

--------------------------------------------------
END OF DOCUMENT
--------------------------------------------------
