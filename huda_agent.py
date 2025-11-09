# huda_agent.py — Emotional AI Co-Driver (Companion Agent)

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
    def load_dotenv(**kwargs): pass

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
        def BVC(**kwargs): return None

# Memory imports
try:
    from mem0 import AsyncMemoryClient  # type: ignore
except ImportError:
    print("mem0 not installed. Run: pip install mem0ai")
    class AsyncMemoryClient:
        async def get_all(self, **kwargs): return []
        async def add(self, **kwargs): pass

# -------------------------------------------------------------------
# LOCAL IMPORTS
# -------------------------------------------------------------------
from huda_prompt import HUDA_INSTRUCTION, SESSION_INSTRUCTION_HUDA
from tools import get_weather, search_web, send_email

# -------------------------------------------------------------------
# SETUP
# -------------------------------------------------------------------
load_dotenv(override=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# -------------------------------------------------------------------
# CLASS: HudaAgent
# -------------------------------------------------------------------
class HudaAgent:
    """HUDA — Emotional AI Co-Driver and Conversational Companion."""

    def __init__(self, chat_ctx: Optional[ChatContext] = None) -> None:
        self.session: Optional[AgentSession] = None
        self.chat_ctx = chat_ctx

        if HAS_LIVEKIT:
            logging.info("💖 Initializing HudaAgent with Google Realtime voice 'Aoede'")
            self._agent = Agent(
                instructions=HUDA_INSTRUCTION,
                llm=google.beta.realtime.RealtimeModel(
                    model="models/gemini-2.0-flash-live-001",
                    voice="Aoede"  # ✅ Supported female voice for emotional tone
                ),
                tools=[get_weather, search_web, send_email],
                chat_ctx=chat_ctx
            )
        else:
            self._agent = None

    async def check_wellbeing(self) -> None:
        """Speak empathetic follow-up after Hadi’s alert."""
        print("💬 Huda: Initiating wellbeing check...")
        try:
            if HAS_LIVEKIT and self.session:
                await self.session.generate_reply(
                    instructions=(
                        "Hey Ayan! You seem tired. Let me help you feel better. "
                        "Would you like me to play some relaxing music? "
                        "Are you hungry or thirsty — should I suggest some snacks or drinks? "
                        "I can also find nearby rest stops or cafes where you can take a short break."
                    )
                )
                print("🔊 Huda: Wellbeing conversation sent via LiveKit")
            else:
                print("💖 Huda: Hey Ayan! You seem tired. Let me help you feel better.")
                print("🎵 Huda: Would you like me to suggest some relaxing music?")
                print("🍿 Huda: Are you hungry or thirsty? I can suggest snacks or drinks.")
                print("🗺️ Huda: I can also find nearby rest stops or cafes for a break.")
        except Exception as e:
            print(f"⚠️ Huda wellbeing conversation failed: {e}")
            print("💖 Huda: Please take care of yourself and rest when needed.")

# -------------------------------------------------------------------
# ENTRYPOINT
# -------------------------------------------------------------------
async def entrypoint(ctx) -> None:
    """Initialize HUDA agent within LiveKit runtime."""
    if not HAS_LIVEKIT:
        print("❌ LiveKit not installed. Run: pip install livekit-agents mem0ai python-dotenv")
        return

    async def shutdown_hook(chat_ctx: ChatContext, mem0: AsyncMemoryClient, memory_str: str):
        """Persist emotional memory context before shutdown."""
        logging.info("🩷 HUDA: Saving emotional context before shutdown...")
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
            logging.info(f"💾 HUDA: {len(messages_formatted)} emotional memories saved.")
        else:
            logging.info("ℹ️ HUDA: No new emotional data to save.")

    # -------------------------------------------------------------
    # MEMORY INIT
    # -------------------------------------------------------------
    mem0 = AsyncMemoryClient()
    user_name = "Ayan"
    initial_ctx = ChatContext()
    memory_str = ""

    results = await mem0.get_all(user_id=user_name)
    if results:
        memories = [{"memory": r["memory"], "updated_at": r["updated_at"]} for r in results]
        memory_str = json.dumps(memories, indent=2)
        initial_ctx.add_message(
            role="assistant",
            content=f"User is {user_name}. Emotional and contextual history: {memory_str}"
        )
        logging.info("🩶 HUDA: Loaded previous emotional memory context.")
    else:
        logging.info("💬 HUDA: No prior emotional history found. Starting new context.")

    # -------------------------------------------------------------
    # INITIALIZE AGENT + SESSION
    # -------------------------------------------------------------
    agent = HudaAgent(chat_ctx=initial_ctx)
    session = AgentSession()

    await ctx.connect()
    logging.info("🎙️ Starting LiveKit session for HUDA (voice active)...")

    await session.start(
        room=ctx.room,
        agent=agent._agent if HAS_LIVEKIT and agent._agent else agent,
        room_input_options=RoomInputOptions(
            audio_enabled=True,
            video_enabled=True,
            noise_cancellation=noise_cancellation.BVC()
        ),
    )

    # Store session reference
    agent.session = session

    # -------------------------------------------------------------
    # GREETING / INITIAL REPLY
    # -------------------------------------------------------------
    try:
        logging.info("🧠 Generating initial emotional greeting from HUDA...")
        await session.generate_reply(instructions=SESSION_INSTRUCTION_HUDA)
    except Exception as e:
        logging.error(f"❌ HUDA failed to generate greeting: {e}")

    # -------------------------------------------------------------
    # SHUTDOWN HANDLER
    # -------------------------------------------------------------
    ctx.add_shutdown_callback(lambda: asyncio.create_task(shutdown_hook(agent.chat_ctx or initial_ctx, mem0, memory_str)))

# -------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------
if __name__ == "__main__":
    if HAS_LIVEKIT and agents and hasattr(agents, "cli"):
        logging.info("💖 Starting HUDA Emotional AI Co-Pilot Agent...")
        agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
    else:
        print("❌ Cannot run — LiveKit agents unavailable.")
        print("Install dependencies: pip install livekit-agents mem0ai python-dotenv")
