import json

def prepare_visualization_data():
    """Convert network data to a format optimized for web visualization"""
    
    # Load network data
    with open('data/network_multi_signal.json', 'r') as f:
        network = json.load(f)
    
    # Prepare nodes with better formatting
    nodes = []
    for streamer in network['nodes']:
        nodes.append({
            'id': streamer['username'],
            'label': streamer['display_name'],
            'size': streamer['current_viewers'] / 100,  # Scale size by viewers
            'game': streamer['game_name'],
            'viewers': streamer['current_viewers'],
            'followers': streamer['follower_count'],
            'language': streamer['language'],
            'teams': streamer['teams']
        })
    
    # Prepare edges
    edges = []
    for edge in network['edges']:
        edges.append({
            'source': edge['source'],
            'target': edge['target'],
            'weight': edge['weight'],
            'types': edge['connection_types']
        })
    
    viz_data = {
        'nodes': nodes,
        'edges': edges,
        'stats': network['metadata']
    }
    
    # Save for web visualization
    with open('docs/network_data.json', 'w') as f:
        json.dump(viz_data, f, indent=2)
    
    print(f"✓ Prepared {len(nodes)} nodes and {len(edges)} edges for visualization")
    print(f"✓ Saved to docs/network_data.json")
    
    # Print some interesting stats
    games = {}
    for node in nodes:
        game = node['game']
        games[game] = games.get(game, 0) + 1
    
    print(f"\n=== Game Distribution ===")
    for game, count in sorted(games.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"{game}: {count} streamers")

if __name__ == "__main__":
    prepare_visualization_data()