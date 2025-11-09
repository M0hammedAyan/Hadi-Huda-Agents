# agent_manager.py — Unified Dual-Agent + Drowsiness Integration

import asyncio
import logging
from dotenv import load_dotenv
from drowsiness_monitor import DrowsinessModel
from hadi_agent import HadiAgent, entrypoint as hadi_entrypoint
from huda_agent import HudaAgent, entrypoint as huda_entrypoint

# Optional LiveKit setup (fallback-safe)
HAS_LIVEKIT = False
AgentSession = None
try:
    from livekit import agents  # type: ignore
    from livekit.agents import AgentSession, RoomInputOptions  # type: ignore
    from livekit.plugins import noise_cancellation  # type: ignore
    HAS_LIVEKIT = True
except ImportError:
    print("LiveKit not installed - install with: pip install livekit-agents")
    agents = None
    AgentSession = None

from typing import Any, Optional

# Setup logging
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# -------------------------------------------------------------------
# AGENT ROUTER LOGIC
# -------------------------------------------------------------------
class AgentManager:
    """Routes between Hadi (technical) and Huda (emotional) and handles events like drowsiness."""

    def __init__(self):
        self.last_active_agent = "HUDA"
        self.user_name = "Ayan"
        self.hadi = HadiAgent()
        self.huda = HudaAgent()
        self.session: Optional[Any] = None

    def detect_agent(self, text: str) -> str:
        """Decide which agent should handle this query."""
        text_lower = text.lower()

        hadi_keywords = [
            "engine", "fuel", "temperature", "route", "map", "location",
            "battery", "speed", "system", "diagnostic", "pressure",
            "check", "sensor", "status", "data", "report", "navigation",
            "drive", "tire", "oil", "brake"
        ]

        huda_keywords = [
            "hi", "hello", "hey", "how are you", "tired", "music", "song",
            "mood", "talk", "relax", "funny", "joke", "story", "who are you",
            "who is hadi", "friend", "laugh", "good morning", "good night"
        ]

        if any(k in text_lower for k in hadi_keywords):
            self.last_active_agent = "HADI"
        elif any(k in text_lower for k in huda_keywords):
            self.last_active_agent = "HUDA"
        return self.last_active_agent

    async def dispatch(self, ctx, user_text: str):
        """Send user message to correct agent."""
        selected = self.detect_agent(user_text)
        if selected == "HADI":
            logging.info("Routing to Hadi for technical response.")
            await hadi_entrypoint(ctx)
        else:
            logging.info("Routing to Huda for emotional response.")
            await huda_entrypoint(ctx)

    async def on_hadi_alert(self):
        """Hadi attempts to wake up the driver."""
        logging.warning("🚨 Hadi: Attempting to wake up driver...")
        
        # Ensure Hadi has session access
        if self.session and hasattr(self.hadi, 'session'):
            self.hadi.session = self.session  # type: ignore
        
        await self.hadi.alert_driver()
    
    async def on_huda_conversation(self):
        """Huda starts conversation after driver wakes up."""
        logging.info("💖 Huda: Starting post-drowsiness conversation...")
        
        # Ensure Huda has session access
        if self.session and hasattr(self.huda, 'session'):
            self.huda.session = self.session  # type: ignore
        
        await self.huda.check_wellbeing()


# -------------------------------------------------------------------
# LIVEKIT ENTRYPOINT
# -------------------------------------------------------------------
async def entrypoint(ctx):
    """Main LiveKit + Drowsiness integrated runtime."""
    if not HAS_LIVEKIT:
        print("❌ LiveKit not installed. Run: pip install livekit-agents mem0ai python-dotenv")
        return

    manager = AgentManager()
    await ctx.connect()

    # Shared session for both agents
    if AgentSession and HAS_LIVEKIT:
        session = AgentSession()
        manager.session = session
        if hasattr(manager.hadi, "session"):
            manager.hadi.session = session
        if hasattr(manager.huda, "session"):
            manager.huda.session = session

    logging.info("🎧 HADI–HUDA Co-Pilot Voice Agent is active and listening...")

    # Start Huda’s LiveKit session concurrently with drowsiness detection
    huda_task = asyncio.create_task(huda_entrypoint(ctx))

    async def run_drowsiness_monitor():
        model = DrowsinessModel(alarm_path="alarm.wav")
        await model.start(
            hadi_callback=manager.on_hadi_alert,
            huda_callback=manager.on_huda_conversation,
        )

    drowsy_task = asyncio.create_task(run_drowsiness_monitor())

    # Keep both running until one finishes or system stops
    try:
        await asyncio.gather(huda_task, drowsy_task)
    except asyncio.CancelledError:
        logging.info("🛑 Tasks cancelled, shutting down gracefully.")
    finally:
        logging.info("💤 System stopped cleanly.")

# -------------------------------------------------------------------
# CONSOLE-ONLY EXECUTION (For testing without LiveKit)
# -------------------------------------------------------------------
if __name__ == "__main__":
    if HAS_LIVEKIT and agents and hasattr(agents, "cli"):
        logging.info("🚀 Launching Hadi–Huda Co-Pilot (LiveKit + Drowsiness Integration)")
        agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
    else:
        print("Running without LiveKit for testing purposes...\n")

        async def console_run():
            manager = AgentManager()
            model = DrowsinessModel(alarm_path="alarm.wav")
            await model.start(
                hadi_callback=manager.on_hadi_alert,
                huda_callback=manager.on_huda_conversation
            )

        asyncio.run(console_run())
