# test_both_apis.py - Test if one key works for both APIs
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_both_apis():
    api_key = "AIzaSyDFW1LDBY4E5_ASNnfSfKs0KZEbWzfmg2U"
    
    print("Testing YouTube API...")
    youtube_url = "https://www.googleapis.com/youtube/v3/search"
    youtube_params = {
        "part": "snippet",
        "q": "music",
        "type": "video",
        "maxResults": 1,
        "key": api_key
    }
    
    try:
        response = requests.get(youtube_url, params=youtube_params)
        if response.status_code == 200:
            print("YouTube API: WORKS")
        else:
            print("YouTube API: FAILED")
    except Exception as e:
        print(f"YouTube API Error: {e}")
    
    print("\nTesting Maps API...")
    maps_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    maps_params = {
        "location": "40.7128,-74.0060",
        "radius": 1000,
        "type": "restaurant",
        "key": api_key
    }
    
    try:
        response = requests.get(maps_url, params=maps_params)
        if response.status_code == 200:
            print("Maps API: WORKS")
        else:
            print("Maps API: FAILED")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Maps API Error: {e}")

if __name__ == "__main__":
    test_both_apis()