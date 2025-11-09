# hadi_agent.py — Vehicle Co-Pilot (Technical / Diagnostic Agent)

import os
import json
import logging
import asyncio
from typing import Optional

# -------------------------------------------------------------------
# Safe optional imports
# -------------------------------------------------------------------
try:
    from dotenv import load_dotenv  # type: ignore
except ImportError:
    def load_dotenv(): pass

# LiveKit imports with fallbacks
HAS_LIVEKIT = False
try:
    from livekit import agents  # type: ignore
    from livekit.agents import AgentSession, Agent, RoomInputOptions, ChatContext  # type: ignore
    from livekit.plugins import noise_cancellation, google  # type: ignore
    HAS_LIVEKIT = True
except ImportError:
    print("LiveKit not installed. Run: pip install livekit-agents")
    agents = None

    class Agent:
        def __init__(self, **kwargs): pass
    class AgentSession:
        async def start(self, **kwargs): pass
        async def generate_reply(self, **kwargs): return "LiveKit not available"
    class ChatContext:
        def __init__(self): self.items = []
        def add_message(self, **kwargs): pass
    class RoomInputOptions:
        def __init__(self, **kwargs): pass
    class google:
        class beta:
            class realtime:
                @staticmethod
                def RealtimeModel(**kwargs): return None
    class noise_cancellation:
        @staticmethod
        def BVC(): return None

# Memory
HAS_MEM0 = False
try:
    from mem0 import AsyncMemoryClient  # type: ignore
    HAS_MEM0 = True
except ImportError:
    print("mem0 not installed. Run: pip install mem0ai")
    class AsyncMemoryClient:
        async def get_all(self, **kwargs): return []
        async def add(self, **kwargs): pass

# -------------------------------------------------------------------
# Local imports
# -------------------------------------------------------------------
from hadi_prompt import HADI_AGENT_INSTRUCTION, SESSION_INSTRUCTION_HADI
from tools import search_web, diagnose_car_issue

# -------------------------------------------------------------------
# Config
# -------------------------------------------------------------------
load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# -------------------------------------------------------------------
# CLASS: HadiAgent
# -------------------------------------------------------------------
class HadiAgent:
    """HADI — Intelligent Vehicle Systems Co-Pilot (Diagnostics / Navigation)"""

    def __init__(self, chat_ctx: Optional[ChatContext] = None) -> None:
        self.session: Optional[AgentSession] = None
        self.chat_ctx = chat_ctx

        if HAS_LIVEKIT:
            self._agent = Agent(
                instructions=HADI_AGENT_INSTRUCTION,
                llm=google.beta.realtime.RealtimeModel(
                    model="models/gemini-2.0-flash-live-001",
                    voice="Aoede"
                ),
                tools=[search_web, diagnose_car_issue],
                chat_ctx=chat_ctx
            )
        else:
            self._agent = None

    async def alert_driver(self) -> None:
        """Speak a firm wake-up warning when drowsiness detected."""
        print("🚨 Hadi: Drowsiness detected! Speaking alert...")
        try:
            if HAS_LIVEKIT and self.session:
                await self.session.generate_reply(
                    instructions="Ayan! You're losing focus. Keep your eyes open and stay alert!"
                )
                print("🔊 Hadi: Voice alert sent via LiveKit")
            else:
                print("🚨 Hadi: AYAN! YOU'RE LOSING FOCUS. KEEP YOUR EYES OPEN AND STAY ALERT!")
                print("💬 Hadi: Please pull over safely if you're too tired to drive.")
        except Exception as e:
            print(f"⚠️ Hadi alert failed: {e}")
            print("🚨 Hadi: AYAN! WAKE UP! PULL OVER SAFELY!")

# -------------------------------------------------------------------
# ENTRYPOINT
# -------------------------------------------------------------------
async def entrypoint(ctx) -> None:
    """Initialize Hadi agent within a LiveKit runtime."""
    if not HAS_LIVEKIT:
        print("❌ LiveKit not installed. Run: pip install livekit-agents mem0ai python-dotenv")
        return

    async def shutdown_hook(chat_ctx: ChatContext, mem0: AsyncMemoryClient, memory_str: str):
        """Save memory context on graceful shutdown."""
        logging.info("HADI: Initiating shutdown, saving context...")
        messages_formatted = []
        for item in getattr(chat_ctx, "items", []):
            role = getattr(item, "role", None)
            content = getattr(item, "content", None)
            if not role or not content:
                continue
            content_str = "".join(str(c) for c in content) if isinstance(content, list) else str(content)
            if memory_str and memory_str in content_str:
                continue
            if role in ["user", "assistant"]:
                messages_formatted.append({"role": role, "content": content_str.strip()})
        if messages_formatted:
            await mem0.add(messages_formatted, user_id="Ayan")
            logging.info(f"HADI: Saved {len(messages_formatted)} memory entries.")
        else:
            logging.info("HADI: No new memory to save.")

    # -------------------------------------------------------------
    # SETUP
    # -------------------------------------------------------------
    session = AgentSession()
    mem0 = AsyncMemoryClient()
    user_name = "Ayan"
    initial_ctx = ChatContext()
    memory_str = ""

    # Load memory
    results = await mem0.get_all(user_id=user_name)
    if results:
        memories = [{"memory": r["memory"], "updated_at": r["updated_at"]} for r in results]
        memory_str = json.dumps(memories, indent=2)
        initial_ctx.add_message(
            role="assistant",
            content=f"User is {user_name}. Prior context: {memory_str}"
        )
        logging.info("HADI: Loaded previous memories.")
    else:
        logging.info("HADI: Starting with fresh context.")

    # Create Hadi
    agent = HadiAgent(chat_ctx=initial_ctx)
    logging.info("✅ HADI initialized with Gemini 2.0 Flash Realtime model (voice: Aoede ).")

    # -------------------------------------------------------------
    # START LIVEKIT SESSION
    # -------------------------------------------------------------
    await ctx.connect()
    await session.start(
        room=ctx.room,
        agent=agent._agent if agent._agent else agent,
        room_input_options=RoomInputOptions(
            audio_enabled=True,
            video_enabled=True,
            noise_cancellation=noise_cancellation.BVC() if HAS_LIVEKIT else None
        ),
    )

    # First reply on connection
    await session.generate_reply(instructions=SESSION_INSTRUCTION_HADI)
    logging.info("🎯 HADI ready for interaction.")

    # Store session for runtime use (like drowsiness alert)
    agent.session = session

    ctx.add_shutdown_callback(lambda: asyncio.create_task(shutdown_hook(agent.chat_ctx or initial_ctx, mem0, memory_str)))

# -------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------
if __name__ == "__main__":
    if HAS_LIVEKIT and agents and hasattr(agents, "cli"):
        agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
    else:
        print("Cannot run — LiveKit agents unavailable.")
        print("Install dependencies: pip install livekit-agents mem0ai python-dotenv")
