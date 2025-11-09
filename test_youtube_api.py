# test_youtube_api.py - Test YouTube API key
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_youtube_api():
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": "relaxing music",
        "type": "video",
        "maxResults": 3,
        "key": api_key
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("YouTube API Key is VALID")
            print(f"Found {len(data.get('items', []))} videos")
        else:
            print("YouTube API Key FAILED")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    test_youtube_api()