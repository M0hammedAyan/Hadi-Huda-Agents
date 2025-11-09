# simple_api_server.py - Simplified backend without LiveKit
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json
import cv2
import time
from connectivity_manager import ConnectivityManager

app = FastAPI(title="Hadi-Huda Simple API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class YouTubeRequest(BaseModel):
    video_id: str

class BluetoothRequest(BaseModel):
    device_address: str

connectivity = ConnectivityManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connected")
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "user_message":
                text = message["text"].lower()
                
                if any(word in text for word in ["tired", "sleepy", "drowsy"]):
                    response = "HADI: Stay alert! Pull over if needed."
                elif any(word in text for word in ["music", "song", "relax"]):
                    response = "HUDA: I'll find some relaxing music for you!"
                else:
                    response = f"HUDA: I heard you say '{message['text']}'. How can I help?"
                
                await websocket.send_text(json.dumps({
                    "type": "agent_response",
                    "message": response,
                    "timestamp": time.time()
                }))
                
    except WebSocketDisconnect:
        print("WebSocket disconnected")

@app.get("/api/wifi/scan")
async def scan_wifi():
    networks = await connectivity.scan_wifi()
    return {"networks": networks}

@app.post("/api/bluetooth/connect")
async def connect_bluetooth(request: BluetoothRequest):
    success = await connectivity.connect_bluetooth(request.device_address)
    return {"connected": success, "device": request.device_address}

@app.get("/api/youtube/search")
async def search_youtube(query: str, max_results: int = 5):
    results = await connectivity.search_youtube(query, max_results)
    return {"videos": results}

@app.post("/api/youtube/play")
async def play_youtube(request: YouTubeRequest):
    return {"status": "playing", "video_id": request.video_id}

@app.get("/api/maps/nearby")
async def get_nearby_places(type: str = "gas_station"):
    places = await connectivity.get_nearby_places(40.7128, -74.0060, type)
    return {"places": places}

@app.get("/api/status")
async def get_status():
    return {
        "status": "running", 
        "agents": ["HADI", "HUDA"], 
        "features": ["wifi", "bluetooth", "youtube", "maps"],
        "mode": "simple"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)