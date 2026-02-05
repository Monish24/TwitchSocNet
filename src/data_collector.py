import requests
import json
import time
from datetime import datetime
from twitch_api import TwitchAPI

class EnhancedCollector:
    def __init__(self):
        self.api = TwitchAPI()
        self.api.get_access_token()
        
    def get_channel_teams(self, broadcaster_id):
        """Get teams a broadcaster belongs to"""
        url = 'https://api.twitch.tv/helix/teams/channel'
        headers = {
            'Client-ID': self.api.client_id,
            'Authorization': f'Bearer {self.api.access_token}'
        }
        params = {'broadcaster_id': broadcaster_id}
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()['data']
        return []
    
    def get_channel_info(self, broadcaster_id):
        """Get detailed channel info including tags"""
        url = 'https://api.twitch.tv/helix/channels'
        headers = {
            'Client-ID': self.api.client_id,
            'Authorization': f'Bearer {self.api.access_token}'
        }
        params = {'broadcaster_id': broadcaster_id}
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()['data'][0]
        return None
    
    def get_Follower_count(self, broadcaster_id):
        """Get follower count"""
        url = 'https://api.twitch.tv/helix/channels/followers'
        headers = {
            'Client-ID': self.api.client_id,
            'Authorization': f'Bearer {self.api.access_token}'
        }
        params = {'broadcaster_id': broadcaster_id}
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()['total']
        return 0
    
    def collect_comprehensive_data(self, limit=100):
        """Collect comprehensive data including teams, tags, and categories"""
        print(f"Collecting comprehensive data on top {limit} streamers...")
        
        # Get top streams
        streams = self.api.get_top_streams(limit=limit)
        if not streams:
            return None
        
        comprehensive_data = []
        
        for i, stream in enumerate(streams, 1):
            print(f"Processing {i}/{len(streams)}: {stream['user_name']}")
            
            # Get channel info (tags, language, etc)
            channel_info = self.get_channel_info(stream['user_id'])
            
            # Get teams
            teams = self.get_channel_teams(stream['user_id'])
            team_names = [team['team_name'] for team in teams]
            
            # Get follower count
            followers = self.get_Follower_count(stream['user_id'])
            
            # Combine all data
            streamer_data = {
                'id': stream['user_id'],
                'username': stream['user_login'],
                'display_name': stream['user_name'],
                'game_id': stream['game_id'],
                'game_name': stream['game_name'],
                'current_viewers': stream['viewer_count'],
                'stream_title': stream['title'],
                'language': stream['language'],
                'started_at': stream['started_at'],
                'tags': channel_info['tags'] if channel_info else [],
                'teams': team_names,
                'follower_count': followers,
                'is_mature': stream['is_mature']
            }
            
            comprehensive_data.append(streamer_data)
            time.sleep(0.5)  # Rate limiting
        
        # Save to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'data/comprehensive_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(comprehensive_data, f, indent=2)
        
        print(f"\n✓ Collected {len(comprehensive_data)} streamers")
        print(f"✓ Saved to {filename}")
        
        return comprehensive_data

if __name__ == "__main__":
    collector = EnhancedCollector()
    data = collector.collect_comprehensive_data(limit=100)
    
    if data:
        # Print some statistics
        games = {}
        for streamer in data:
            game = streamer['game_name']
            games[game] = games.get(game, 0) + 1
        
        print(f"\n=== Top Games ===")
        for game, count in sorted(games.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"{game}: {count} streamers")
        
        teams_count = sum(1 for s in data if s['teams'])
        print(f"\n✓ {teams_count} streamers are in teams")