import speech_recognition as sr
import pyttsx3
import database
import subprocess
import screen_brightness_control as sbc
import ctypes
import time

# ---------------- TTS (Only for listening, not for speaking) ----------------
engine = pyttsx3.init()
engine.setProperty('rate', 180)
engine.setProperty('volume', 0)

# ---------------- LISTEN ----------------
def listen(r, source):
    print("Listening...")
    try:
        audio = r.listen(source, timeout=3, phrase_time_limit=5)
    except sr.WaitTimeoutError:
        return ""

    try:
        command = r.recognize_google(audio).lower()
        print("Heard:", command)
        return command
    except sr.UnknownValueError:
        return ""
    except:
        return ""

# ---------------- VOLUME CONTROL ----------------
VK_VOLUME_UP = 0xAF
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_MUTE = 0xAD

def volume_up():
    for _ in range(3):
        ctypes.windll.user32.keybd_event(VK_VOLUME_UP, 0, 0, 0)
        ctypes.windll.user32.keybd_event(VK_VOLUME_UP, 0, 2, 0)
        time.sleep(0.05)

def volume_down():
    for _ in range(3):
        ctypes.windll.user32.keybd_event(VK_VOLUME_DOWN, 0, 0, 0)
        ctypes.windll.user32.keybd_event(VK_VOLUME_DOWN, 0, 2, 0)
        time.sleep(0.05)

def volume_mute():
    ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, 0, 0)
    ctypes.windll.user32.keybd_event(VK_VOLUME_MUTE, 0, 2, 0)

# ---------------- BRIGHTNESS CONTROL ----------------
def change_brightness(step):
    try:
        current = sbc.get_brightness()[0]
        new_brightness = max(0, min(100, current + step))
        sbc.set_brightness(new_brightness)
        return True
    except:
        return False

# ---------------- SYSTEM CONTROLS ----------------
def lock_pc():
    ctypes.windll.user32.LockWorkStation()

def sleep_pc():
    ctypes.windll.PowrProf.SetSuspendState(0, 1, 0)

def shutdown_pc():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Confirm shutdown?")
        r.adjust_for_ambient_noise(source, duration=0.5)
        confirm = listen(r, source)
    
    if "yes" in confirm:
        time.sleep(5)
        subprocess.run(["shutdown", "/s", "/t", "0"])

def restart_pc():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Confirm restart?")
        r.adjust_for_ambient_noise(source, duration=0.5)
        confirm = listen(r, source)

    if "yes" in confirm:
        time.sleep(5)
        subprocess.run(["shutdown", "/r", "/t", "0"])

# ---------------- APPLICATION CONTROL ----------------
apps = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "command prompt": "cmd.exe",
    "file explorer": "explorer.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "brave": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    "discord": r"C:\Users\aggai\AppData\Local\Discord\Update.exe --processStart Discord.exe",
    "telegram": r"C:\Users\aggai\AppData\Roaming\Telegram Desktop\Telegram.exe",
    "instagram": r"shell:AppsFolder\Facebook.InstagramBeta_8xx8rvfyw5nnt!App",
    "pycharm": r"C:\Program Files\JetBrains\PyCharm Community Edition\bin\pycharm64.exe",
    "android studio": r"C:\Program Files\Android\Android Studio\bin\studio64.exe",
    "flutter": r"C:\src\flutter\bin\flutter.bat",
    "antigravity": r"C:\Users\aggai\AppData\Local\Programs\antigravity\Antigravity.exe",
    "vs code": r"D:\Microsoft VS Code\Code.exe",
    "microsoft store": r"shell:AppsFolder\Microsoft.WindowsStore_8wekyb3d8bbwe!App",
    "settings": "ms-settings:",
    "clock": r"shell:AppsFolder\Microsoft.WindowsAlarms_8wekyb3d8bbwe!App",
    "cloud": r"shell:AppsFolder\Microsoft.CloudExperienceHost_cw5n1h2txyewy!App",
}

def open_app(name):
    if name in apps:
        try:
            path = apps[name]
            if path.startswith("shell:") or path.startswith("ms-settings"):
                import os
                os.startfile(path)
            elif name == "file explorer":
                subprocess.Popen(path, shell=True)
            elif " --" in path or " /" in path:
                subprocess.Popen(path, shell=True)
            else:
                subprocess.Popen(path)
        except:
            pass

# Map app names to their process names for closing
close_process = {
    "chrome": "chrome.exe",
    "notepad": "notepad.exe",
    "calculator": "Calculator.exe",
    "paint": "mspaint.exe",
    "command prompt": "cmd.exe",
    "file explorer": "explorer.exe",
    "word": "WINWORD.EXE",
    "excel": "EXCEL.EXE",
    "powerpoint": "POWERPNT.EXE",
    "edge": "msedge.exe",
    "brave": "brave.exe",
    "discord": "Discord.exe",
    "telegram": "Telegram.exe",
    "instagram": "Instagram.exe",
    "pycharm": "pycharm64.exe",
    "android studio": "studio64.exe",
    "antigravity": "Antigravity.exe",
    "vs code": "Code.exe",
    "clock": "Time.exe",
    "settings": "SystemSettings.exe",
    "microsoft store": "WinStore.App.exe",
}

def close_app(name):
    if name in close_process:
        subprocess.run(f"taskkill /IM {close_process[name]} /F", shell=True, capture_output=True)

def close_all_apps():
    # Skip explorer.exe as it is critical for Windows desktop
    skip = {"explorer.exe"}
    for name, process in close_process.items():
        if process.lower() not in skip:
            subprocess.run(f"taskkill /IM {process} /F", shell=True, capture_output=True)
    print("All apps closed.")

# ---------------- MEDIA CONTROL ----------------
def play_pause():
    ctypes.windll.user32.keybd_event(0xB3, 0, 0, 0)
    ctypes.windll.user32.keybd_event(0xB3, 0, 2, 0)

def next_track():
    ctypes.windll.user32.keybd_event(0xB0, 0, 0, 0)
    ctypes.windll.user32.keybd_event(0xB0, 0, 2, 0)

def previous_track():
    ctypes.windll.user32.keybd_event(0xB1, 0, 0, 0)
    ctypes.windll.user32.keybd_event(0xB1, 0, 2, 0)

# ---------------- SCREENSHOT ----------------
def take_screenshot():
    ctypes.windll.user32.keybd_event(0x2C, 0, 0, 0)
    ctypes.windll.user32.keybd_event(0x2C, 0, 2, 0)

# ---------------- MAIN LOOP (SILENT MODE) ----------------
# ---------------- MAIN LOOP (SILENT MODE) ----------------
def run_voice():
    r = sr.Recognizer()
    # Dynamic energy threshold can help with efficiency
    r.dynamic_energy_threshold = False 
    r.energy_threshold = 400 # Initial guess, adjust if needed

    with sr.Microphone() as source:
        print("Calibrating background noise... Please wait.")
        r.adjust_for_ambient_noise(source, duration=1)
        print("Calibration done. Listening active.")

        while True:
            command = listen(r, source)
            if not command:
                continue

            # Log to database
            database.log_command("Offline", command)

            # Exit command
            if any(word in command for word in ["exit", "quit", "stop", "goodbye"]):
                break

            # Volume control
            elif any(phrase in command for phrase in ["increase volume", "volume up", "turn up volume"]):
                volume_up()

            elif any(phrase in command for phrase in ["decrease volume", "volume down", "turn down volume"]):
                volume_down()

            elif "mute" in command:
                volume_mute()

            # Brightness control
            elif any(phrase in command for phrase in ["increase brightness", "brightness up", "brighter"]):
                change_brightness(10)

            elif any(phrase in command for phrase in ["decrease brightness", "brightness down", "darker"]):
                change_brightness(-10)

            # Application control
            elif "open" in command:
                for app in apps:
                    if app in command:
                        open_app(app)
                        break

            elif any(phrase in command for phrase in ["close all apps", "close all", "close everything"]):
                close_all_apps()

            elif "close" in command:
                for app in close_process:
                    if app in command:
                        close_app(app)
                        break

            # Media control
            elif any(phrase in command for phrase in ["play", "pause", "play pause"]):
                play_pause()

            elif "next track" in command or "next song" in command:
                next_track()

            elif "previous track" in command or "previous song" in command:
                previous_track()

            # System controls
            elif any(phrase in command for phrase in ["lock computer", "lock pc", "lock screen"]):
                lock_pc()

            elif any(phrase in command for phrase in ["sleep", "go to sleep"]):
                sleep_pc()

            elif any(phrase in command for phrase in ["shutdown", "turn off computer", "power off"]):
                shutdown_pc()

            elif any(phrase in command for phrase in ["restart", "reboot computer"]):
                restart_pc()

            # Screenshot
            elif any(phrase in command for phrase in ["screenshot", "take screenshot", "capture screen"]):
                take_screenshot()

if __name__ == "__main__":
    run_voice()

