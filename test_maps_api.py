# test_maps_api.py - Test Google Maps API key
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_maps_api():
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    
    # Test Places API
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": "40.7128,-74.0060",  # NYC coordinates
        "radius": 1000,
        "type": "gas_station",
        "key": api_key
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Maps API Key is VALID")
            print(f"Found {len(data.get('results', []))} places")
        else:
            print("Maps API Key FAILED")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    test_maps_api()