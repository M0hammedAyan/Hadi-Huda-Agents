# connectivity_manager.py - Unified connectivity for WiFi, Bluetooth, YouTube, Maps
import asyncio
import subprocess
import json
import requests
from typing import Dict, List, Optional
import platform
import os
from dotenv import load_dotenv

load_dotenv()

class ConnectivityManager:
    def __init__(self):
        self.wifi_connected = False
        self.bluetooth_devices = {}
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.livekit_url = os.getenv('LIVEKIT_URL')
        self.livekit_api_key = os.getenv('LIVEKIT_API_KEY')
        self.livekit_api_secret = os.getenv('LIVEKIT_API_SECRET')
        
    # WiFi Management
    async def scan_wifi(self) -> List[Dict]:
        """Scan available WiFi networks"""
        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    ["netsh", "wlan", "show", "profiles"], 
                    capture_output=True, text=True
                )
                networks = []
                for line in result.stdout.split('\n'):
                    if "All User Profile" in line:
                        ssid = line.split(':')[1].strip()
                        networks.append({"ssid": ssid, "signal": "Unknown"})
                return networks
        except Exception as e:
            print(f"WiFi scan error: {e}")
            return []
    
    async def connect_wifi(self, ssid: str, password: str) -> bool:
        """Connect to WiFi network"""
        try:
            if platform.system() == "Windows":
                # Create profile
                profile_xml = f'''<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>'''
                
                with open(f"{ssid}.xml", "w") as f:
                    f.write(profile_xml)
                
                subprocess.run(["netsh", "wlan", "add", "profile", f"filename={ssid}.xml"])
                result = subprocess.run(["netsh", "wlan", "connect", f"name={ssid}"])
                self.wifi_connected = result.returncode == 0
                return self.wifi_connected
        except Exception as e:
            print(f"WiFi connection error: {e}")
            return False
    
    # Bluetooth Management
    async def scan_bluetooth(self) -> List[Dict]:
        """Scan for Bluetooth devices"""
        try:
            if platform.system() == "Windows":
                # Simulate Bluetooth scan (requires additional libraries for real implementation)
                return [
                    {"name": "Car Audio", "address": "XX:XX:XX:XX:XX:01", "connected": False},
                    {"name": "Phone", "address": "XX:XX:XX:XX:XX:02", "connected": False}
                ]
        except Exception as e:
            print(f"Bluetooth scan error: {e}")
            return []
    
    async def connect_bluetooth(self, device_address: str) -> bool:
        """Connect to Bluetooth device"""
        try:
            # Simulate connection (real implementation needs pybluez or similar)
            self.bluetooth_devices[device_address] = {"connected": True}
            return True
        except Exception as e:
            print(f"Bluetooth connection error: {e}")
            return False
    
    # YouTube Integration
    async def search_youtube(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search YouTube videos"""
        try:
            # Using YouTube Data API v3
            if not self.youtube_api_key:
                return self._mock_youtube_results(query)
            
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet",
                "q": query,
                "type": "video",
                "maxResults": max_results,
                "key": self.youtube_api_key
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return [
                    {
                        "video_id": item["id"]["videoId"],
                        "title": item["snippet"]["title"],
                        "thumbnail": item["snippet"]["thumbnails"]["default"]["url"]
                    }
                    for item in data.get("items", [])
                ]
        except Exception as e:
            print(f"YouTube search error: {e}")
            return self._mock_youtube_results(query)
    
    def _mock_youtube_results(self, query: str) -> List[Dict]:
        """Mock YouTube results for demo"""
        return [
            {"video_id": "dQw4w9WgXcQ", "title": f"Relaxing Music for {query}", "thumbnail": ""},
            {"video_id": "9bZkp7q19f0", "title": f"Driving Songs - {query}", "thumbnail": ""},
            {"video_id": "kJQP7kiw5Fk", "title": f"Focus Music - {query}", "thumbnail": ""}
        ]
    
    # Maps Integration
    async def get_nearby_places(self, lat: float, lng: float, place_type: str = "gas_station") -> List[Dict]:
        """Get nearby places using Google Maps API"""
        try:
            if not self.maps_api_key:
                return self._mock_places_data(place_type)
            
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                "location": f"{lat},{lng}",
                "radius": 5000,
                "type": place_type,
                "key": self.maps_api_key
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return [
                    {
                        "name": place["name"],
                        "rating": place.get("rating", 0),
                        "distance": "Unknown",
                        "address": place.get("vicinity", "")
                    }
                    for place in data.get("results", [])[:5]
                ]
        except Exception as e:
            print(f"Maps API error: {e}")
            return self._mock_places_data(place_type)
    
    def _mock_places_data(self, place_type: str) -> List[Dict]:
        """Mock places data for demo"""
        places_data = {
            "gas_station": [
                {"name": "Shell Station", "distance": "0.5 miles", "rating": 4.2, "address": "123 Main St"},
                {"name": "BP Gas", "distance": "0.8 miles", "rating": 4.0, "address": "456 Oak Ave"}
            ],
            "restaurant": [
                {"name": "McDonald's", "distance": "0.3 miles", "rating": 3.8, "address": "789 Pine St"},
                {"name": "Starbucks", "distance": "0.6 miles", "rating": 4.3, "address": "321 Elm St"}
            ]
        }
        return places_data.get(place_type, [])
    
    async def get_directions(self, origin: str, destination: str) -> Dict:
        """Get driving directions"""
        try:
            if not self.maps_api_key:
                return {
                    "distance": "15.2 miles",
                    "duration": "22 minutes",
                    "steps": ["Head north on Main St", "Turn right on Highway 101"]
                }
            
            url = "https://maps.googleapis.com/maps/api/directions/json"
            params = {
                "origin": origin,
                "destination": destination,
                "mode": "driving",
                "key": self.maps_api_key
            }
            
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data["routes"]:
                    route = data["routes"][0]["legs"][0]
                    return {
                        "distance": route["distance"]["text"],
                        "duration": route["duration"]["text"],
                        "steps": [step["html_instructions"] for step in route["steps"][:5]]
                    }
        except Exception as e:
            print(f"Directions error: {e}")
            return {"error": str(e)}