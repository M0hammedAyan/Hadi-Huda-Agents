# config_checker.py - Check available API keys
import os
from dotenv import load_dotenv

load_dotenv()

def check_api_keys():
    keys = {
        'YOUTUBE_API_KEY': os.getenv('YOUTUBE_API_KEY'),
        'GOOGLE_MAPS_API_KEY': os.getenv('GOOGLE_MAPS_API_KEY'),
        'LIVEKIT_URL': os.getenv('LIVEKIT_URL'),
        'LIVEKIT_API_KEY': os.getenv('LIVEKIT_API_KEY'),
        'LIVEKIT_API_SECRET': os.getenv('LIVEKIT_API_SECRET'),
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
        'GEMINI_API_SECRET': os.getenv('GEMINI_API_SECRET')
    }
    
    print("API Keys Status:")
    for key, value in keys.items():
        status = "SET" if value else "EMPTY"
        print(f"{key}: {status}")
    
    return keys

if __name__ == "__main__":
    check_api_keys()