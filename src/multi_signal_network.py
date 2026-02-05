import json
import time
from datetime import datetime
import os

class MultiSignalNetwork:
    def __init__(self, data_file):
        with open(data_file, 'r') as f:
            self.streamers = json.load(f)
        
        print(f"Loaded {len(self.streamers)} streamers")
    
    def build_network(self):
        """Build network based on multiple connection signals"""
        print("\nBuilding multi-signal network...")
        
        edges = []
        
        # 1. SHARED TEAMS - Strong connection
        print("1. Analyzing team connections...")
        team_edges = self._find_team_connections()
        edges.extend(team_edges)
        print(f"   Found {len(team_edges)} team-based connections")
        
        # 2. SAME GAME/CATEGORY - Medium connection
        print("2. Analyzing game category connections...")
        game_edges = self._find_game_connections()
        edges.extend(game_edges)
        print(f"   Found {len(game_edges)} game-based connections")
        
        # 3. SHARED TAGS - Weak connection
        print("3. Analyzing tag connections...")
        tag_edges = self._find_tag_connections()
        edges.extend(tag_edges)
        print(f"   Found {len(tag_edges)} tag-based connections")
        
        # 4. SAME LANGUAGE - Context connection
        print("4. Analyzing language connections...")
        lang_edges = self._find_language_connections()
        edges.extend(lang_edges)
        print(f"   Found {len(lang_edges)} language-based connections")
        
        # Merge duplicate edges and sum weights
        merged_edges = self._merge_edges(edges)
        
        # Create network data
        network = {
            'nodes': self.streamers,
            'edges': merged_edges,
            'metadata': {
                'total_nodes': len(self.streamers),
                'total_edges': len(merged_edges),
                'collection_date': datetime.now().isoformat(),
                'connection_types': {
                    'teams': len(team_edges),
                    'games': len(game_edges),
                    'tags': len(tag_edges),
                    'language': len(lang_edges)
                }
            }
        }
        
        # Save network
        output_file = 'data/network_multi_signal.json'
        with open(output_file, 'w') as f:
            json.dump(network, f, indent=2)
        
        print(f"\n✓ Network built successfully!")
        print(f"✓ Saved to {output_file}")
        print(f"\n=== Network Stats ===")
        print(f"Nodes: {network['metadata']['total_nodes']}")
        print(f"Edges: {network['metadata']['total_edges']}")
        
        return network
    
    def _find_team_connections(self):
        """Find connections based on shared teams"""
        edges = []
        
        for i, s1 in enumerate(self.streamers):
            for s2 in self.streamers[i+1:]:
                teams1 = set(s1['teams'])
                teams2 = set(s2['teams'])
                shared_teams = teams1 & teams2
                
                if shared_teams:
                    edges.append({
                        'source': s1['username'],
                        'target': s2['username'],
                        'type': 'team',
                        'weight': len(shared_teams) * 3,  # Teams are strong signals
                        'shared_teams': list(shared_teams)
                    })
        
        return edges
    
    def _find_game_connections(self):
        """Find connections based on same game/category"""
        edges = []
        
        # Group streamers by game
        games = {}
        for streamer in self.streamers:
            game = streamer['game_name']
            if game not in games:
                games[game] = []
            games[game].append(streamer)
        
        # Create connections within each game
        for game, streamers_in_game in games.items():
            if len(streamers_in_game) > 1:
                for i, s1 in enumerate(streamers_in_game):
                    for s2 in streamers_in_game[i+1:]:
                        edges.append({
                            'source': s1['username'],
                            'target': s2['username'],
                            'type': 'game',
                            'weight': 2,  # Medium strength
                            'game': game
                        })
        
        return edges
    
    def _find_tag_connections(self):
        """Find connections based on shared tags"""
        edges = []
        
        for i, s1 in enumerate(self.streamers):
            for s2 in self.streamers[i+1:]:
                tags1 = set(s1['tags'])
                tags2 = set(s2['tags'])
                shared_tags = tags1 & tags2
                
                # Only create edge if they share 2+ tags
                if len(shared_tags) >= 2:
                    edges.append({
                        'source': s1['username'],
                        'target': s2['username'],
                        'type': 'tags',
                        'weight': len(shared_tags),  # Weak signal
                        'shared_tags': list(shared_tags)
                    })
        
        return edges
    
    def _find_language_connections(self):
        """Find connections based on same language"""
        edges = []
        
        # Group by language
        languages = {}
        for streamer in self.streamers:
            lang = streamer['language']
            if lang not in languages:
                languages[lang] = []
            languages[lang].append(streamer)
        
        # Only create language connections for non-English
        # (English is too common to be meaningful)
        for lang, streamers_in_lang in languages.items():
            if lang != 'en' and len(streamers_in_lang) > 1:
                for i, s1 in enumerate(streamers_in_lang):
                    for s2 in streamers_in_lang[i+1:]:
                        edges.append({
                            'source': s1['username'],
                            'target': s2['username'],
                            'type': 'language',
                            'weight': 1,  # Context signal
                            'language': lang
                        })
        
        return edges
    
    def _merge_edges(self, edges):
        """Merge duplicate edges and combine weights"""
        edge_dict = {}
        
        for edge in edges:
            # Create a unique key for each pair
            key = tuple(sorted([edge['source'], edge['target']]))
            
            if key not in edge_dict:
                edge_dict[key] = {
                    'source': edge['source'],
                    'target': edge['target'],
                    'weight': edge['weight'],
                    'connection_types': [edge['type']],
                    'details': {}
                }
            else:
                # Add weight and connection type
                edge_dict[key]['weight'] += edge['weight']
                edge_dict[key]['connection_types'].append(edge['type'])
            
            # Store type-specific details
            if edge['type'] == 'team' and 'shared_teams' in edge:
                edge_dict[key]['details']['teams'] = edge['shared_teams']
            elif edge['type'] == 'game' and 'game' in edge:
                edge_dict[key]['details']['game'] = edge['game']
            elif edge['type'] == 'tags' and 'shared_tags' in edge:
                edge_dict[key]['details']['tags'] = edge['shared_tags']
            elif edge['type'] == 'language' and 'language' in edge:
                edge_dict[key]['details']['language'] = edge['language']
        
        return list(edge_dict.values())

if __name__ == "__main__":
    # Find the most recent comprehensive data file
    data_files = [f for f in os.listdir('data') if f.startswith('comprehensive_')]
    if not data_files:
        print("No comprehensive data files found!")
        print("Run enhanced_collector.py first")
        exit(1)
    
    latest_file = f"data/{sorted(data_files)[-1]}"
    print(f"Using data file: {latest_file}")
    
    # Build network
    builder = MultiSignalNetwork(latest_file)
    network = builder.build_network()
    
    # Show some example connections
    print("\n=== Sample Connections ===")
    for i, edge in enumerate(network['edges'][:5]):
        print(f"\n{i+1}. {edge['source']} ↔ {edge['target']}")
        print(f"   Weight: {edge['weight']}")
        print(f"   Connection types: {', '.join(edge['connection_types'])}")
        if edge['details']:
            print(f"   Details: {edge['details']}")