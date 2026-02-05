import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TwitchAPI:
    def __init__(self):
        self.client_id = os.getenv('TWITCH_CLIENT_ID')
        self.client_secret = os.getenv('TWITCH_CLIENT_SECRET')
        self.access_token = None
        
    def get_access_token(self):
        """Get OAuth token from Twitch"""
        url = 'https://id.twitch.tv/oauth2/token'
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        
        response = requests.post(url, params=params)
        if response.status_code == 200:
            self.access_token = response.json()['access_token']
            print("✓ Successfully authenticated with Twitch API!")
            return self.access_token
        else:
            print(f"✗ Authentication failed: {response.status_code}")
            print(response.json())
            return None
    
    def get_top_streams(self, limit=20):
        """Get top live streams"""
        if not self.access_token:
            self.get_access_token()
        
        url = 'https://api.twitch.tv/helix/streams'
        headers = {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {self.access_token}'
        }
        params = {'first': limit}
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()['data']
        else:
            print(f"Error: {response.status_code}")
            return None

# Test the API
if __name__ == "__main__":
    api = TwitchAPI()
    token = api.get_access_token()
    
    if token:
        print("\nFetching top 10 live streams...")
        streams = api.get_top_streams(limit=10)
        
        if streams:
            print(f"\n✓ Found {len(streams)} streams:")
            for i, stream in enumerate(streams, 1):
                print(f"{i}. {stream['user_name']} - {stream['game_name']} ({stream['viewer_count']} viewers)")