import sys
import threading
import numpy as np
import sounddevice as sd
from dotenv import load_dotenv

from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io
from livekit.plugins import google, noise_cancellation

import database
from prompt import AGENT_INSTRUCTIONS, AGENT_RESPONSES

# ==============================
# ENV
# ==============================
load_dotenv(".env")

# ==============================
# AGENT INSTRUCTION
# ==============================
AGENT_INSTRUCTION =AGENT_INSTRUCTIONS 


# ==============================
# AGENT RESPONSE STYLE
# ==============================
AGENT_RESPONSE =AGENT_RESPONSES


# ==============================
# SYSTEM COMMAND ROUTER (LOGICAL)
# ==============================
def handle_system_command(text: str):
    t = text.lower()
    
    # Log to database
    database.log_command("Online", text)

    if "open notepad" in t:
        print("SYSTEM CALL → OPEN NOTEPAD")

    elif "open chrome" in t:
        print("SYSTEM CALL → OPEN CHROME")

    elif "close chrome" in t:
        print("SYSTEM CALL → CLOSE CHROME")

    elif "increase brightness" in t or "brightness up" in t:
        print("SYSTEM CALL → INCREASE BRIGHTNESS")

    elif "decrease brightness" in t or "brightness down" in t:
        print("SYSTEM CALL → DECREASE BRIGHTNESS")

    elif "wifi on" in t:
        print("SYSTEM CALL → WIFI ON")

    elif "wifi off" in t:
        print("SYSTEM CALL → WIFI OFF")

    elif "bluetooth on" in t:
        print("SYSTEM CALL → BLUETOOTH ON")

    elif "bluetooth off" in t:
        print("SYSTEM CALL → BLUETOOTH OFF")

    elif "shutdown" in t:
        print("SYSTEM CALL → SHUTDOWN SYSTEM")

    elif "restart" in t:
        print("SYSTEM CALL → RESTART SYSTEM")

# ==============================
# LIVEKIT AGENT
# ==============================
class Assistant(Agent):
    def __init__(self):
        super().__init__(instructions=AGENT_INSTRUCTION)

    async def on_response(self, response):
        """
        Triggered whenever Metro replies.
        Used here to logically route system commands.
        """
        user_text = response.input_text
        if user_text:
            handle_system_command(user_text)

# ==============================
# LIVEKIT SERVER
# ==============================
server = AgentServer()

# ==============================
# LIVEKIT SESSION
# ==============================
@server.rtc_session()
async def my_agent(ctx: agents.JobContext):

    if not hasattr(server, "_ui_started"):
        server._ui_started = True
        # UI is now launched separately by run.pyw

    session = AgentSession(
        llm=google.realtime.RealtimeModel(
            voice="Puck",
            temperature=0.8,
            instructions=AGENT_INSTRUCTION,
        )
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params:
                    noise_cancellation.BVC()
            ),
        ),
    )

    await session.generate_reply()

# ==============================
# RUN
# ==============================
def run_agent():
    try:
        # Check if running via multiprocessing (where sys.argv might be run.pyw)
        # or just need to force start mode.
        if len(sys.argv) <= 1 or "run.pyw" in sys.argv[0] or "run.exe" in sys.argv[0]:
            sys.argv = ["agent.py", "console"]

        if not hasattr(server, "_ui_started"):
             # Fix for multiple instances trying to claim same resources
             # This attribute might not persist across processes, but it's good practice 
             # to keep the structure.
             pass
        agents.cli.run_app(server)
    except Exception as e:
        print(f"Agent Error: {e}")

if __name__ == "__main__":
    run_agent()
