import subprocess
import sys
import os
import time

HIDE_CONSOLE = 0x08000000

def run_gui():
    import gui
    gui.start_ui()

def run_agent():
    import agent
    agent.run_agent()

def run_voice():
    import voicecontrol
    voicecontrol.run_voice()

def launch_metro():
    base_path = os.path.dirname(os.path.abspath(__file__))
    current_script = os.path.abspath(__file__)

    # Determine executable for subprocess
    # If frozen (compiled exe), sys.executable is the app itself
    # If script, sys.executable is python.exe
    if getattr(sys, 'frozen', False):
        executable = sys.executable
        # When frozen, the executable is the script itself, so we just run it with args
        args_gui = [executable, "--run-gui"] 
        args_agent = [executable, "--run-agent"]
        args_voice = [executable, "--run-voice"]
    else:
        executable = sys.executable
        # When running as script, we need to pass the script path
        args_gui = [executable, current_script, "--run-gui"]
        args_agent = [executable, current_script, "--run-agent"]
        args_voice = [executable, current_script, "--run-voice"]

    # 1. Start UI
    # In main process we wait for UI? No, we spawn it to keep main process clean 
    # OR we run UI in main process?
    # Better to run UI in main process if possible, but to ensure clean separation let's spawn all.
    # Actually, usually the main process should be the UI.
    
    # Let's check args to see if we are a worker
    if len(sys.argv) > 1:
        if "--run-gui" in sys.argv:
            run_gui()
        elif "--run-agent" in sys.argv:
            run_agent()
        elif "--run-voice" in sys.argv:
            run_voice()
        return

    # --- MAIN LAUNCHER LOGIC ---
    
    # 1. Start UI
    ui_process = subprocess.Popen(
        args_gui,
        cwd=base_path,
        creationflags=HIDE_CONSOLE
    )

    # 2. Start Agent
    agent_process = subprocess.Popen(
        args_agent, 
        creationflags=HIDE_CONSOLE,
        cwd=base_path
    )

    # 3. Start Voice
    time.sleep(2)
    voice_process = subprocess.Popen(
        args_voice, 
        creationflags=HIDE_CONSOLE,
        cwd=base_path
    )

    # Wait for UI to close
    ui_process.wait()

    # Cleanup
    try:
        agent_process.terminate()
        voice_process.terminate()
    except Exception:
        pass

if __name__ == "__main__":
    launch_metro()
