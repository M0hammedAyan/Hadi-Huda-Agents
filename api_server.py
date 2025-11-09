# api_server.py - FastAPI backend for React frontend
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json
from agent_manager import AgentManager
from drowsiness_monitor import DrowsinessModel
from connectivity_manager import ConnectivityManager

app = FastAPI(title="Hadi-Huda API", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class YouTubeRequest(BaseModel):
    video_id: str

# Global manager instances
manager = AgentManager()
connectivity = ConnectivityManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connected")
    
    # Start drowsiness monitoring
    model = DrowsinessModel(alarm_path="alarm.wav")
    
    async def send_alert(alert_type: str, message: str):
        try:
            await websocket.send_text(json.dumps({
                "type": alert_type,
                "message": message,
                "timestamp": asyncio.get_event_loop().time()
            }))
        except Exception as e:
            print(f"Failed to send alert: {e}")
    
    async def hadi_callback():
        await send_alert("hadi_alert", "⚠️ WAKE UP! Stay alert and focused!")
    
    async def huda_callback():
        await send_alert("huda_conversation", "💖 Hey! You seem tired. Need music, snacks, or a rest stop?")
    
    # Start monitoring in background
    monitor_task = asyncio.create_task(model.start(
        hadi_callback=hadi_callback,
        huda_callback=huda_callback
    ))
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "user_message":
                # Route to appropriate agent
                agent_type = manager.detect_agent(message["text"])
                response = f"{agent_type}: Processing '{message['text']}'"
                await send_alert("agent_response", response)
                
    except WebSocketDisconnect:
        print("WebSocket disconnected")
        monitor_task.cancel()
    except Exception as e:
        print(f"WebSocket error: {e}")
        monitor_task.cancel()

@app.post("/api/bluetooth/connect")
async def connect_bluetooth():
    return {"status": "connected", "device": "Car Audio System"}

@app.post("/api/youtube/play")
async def play_youtube(request: YouTubeRequest):
    # Simulate YouTube integration
    print(f"Playing YouTube video: {request.video_id}")
    return {"status": "playing", "video_id": request.video_id, "title": "Relaxing Music"}

@app.get("/api/maps/nearby")
async def get_nearby_places(type: str = "gas_station"):
    places_data = {
        "gas_station": [
            {"name": "Shell Station", "distance": "0.5 miles", "rating": 4.2},
            {"name": "BP Gas", "distance": "0.8 miles", "rating": 4.0},
            {"name": "Exxon", "distance": "1.2 miles", "rating": 4.1}
        ],
        "restaurant": [
            {"name": "McDonald's", "distance": "0.3 miles", "rating": 3.8},
            {"name": "Starbucks", "distance": "0.6 miles", "rating": 4.3},
            {"name": "Subway", "distance": "0.9 miles", "rating": 4.0}
        ],
        "rest_stop": [
            {"name": "Highway Rest Area", "distance": "2.1 miles", "rating": 3.9},
            {"name": "Travel Center", "distance": "3.5 miles", "rating": 4.2}
        ]
    }
    return {"places": places_data.get(type, [])}

@app.get("/api/status")
async def get_status():
    return {"status": "running", "agents": ["HADI", "HUDA"], "features": ["drowsiness_detection", "bluetooth", "youtube", "maps"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)