import json
import random
import uuid
from datetime import datetime, timedelta
import requests
import time

def generate_player_id():
    return f"player_{uuid.uuid4().hex[:8]}"

def generate_session_id():
    return f"session_{uuid.uuid4().hex[:8]}"

def generate_game_id():
    return f"game_{random.randint(1, 3)}"

def generate_device_info():
    os_list = ["iOS", "Android", "Windows"]
    models = ["iPhone 12", "Samsung S21", "Pixel 6", "Gaming PC"]
    os_versions = ["14.5", "11.0", "12.0", "10.0"]
    
    return {
        "os": random.choice(os_list),
        "model": random.choice(models),
        "os_version": random.choice(os_versions)
    }

def generate_game_start_event(player_id, session_id):
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "game_id": generate_game_id(),
        "player_id": player_id,
        "session_id": session_id,
        "event_type": "game_start",
        "version": "1.0",
        "device_info": generate_device_info(),
        "client_version": "2.1.0"
    }

def generate_game_end_event(player_id, session_id, game_id):
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "game_id": game_id,
        "player_id": player_id,
        "session_id": session_id,
        "event_type": "game_end",
        "version": "1.0",
        "duration": random.randint(60, 3600),
        "score": random.randint(100, 10000),
        "level_reached": random.randint(1, 10),
        "coins_earned": random.randint(10, 1000)
    }

def generate_purchase_event(player_id, session_id, game_id):
    items = [
        {"id": "boost_1", "name": "Power Boost", "price": 0.99},
        {"id": "coins_100", "name": "100 Coins Pack", "price": 1.99},
        {"id": "skin_rare", "name": "Rare Skin", "price": 4.99},
        {"id": "bundle_1", "name": "Starter Bundle", "price": 9.99}
    ]
    
    item = random.choice(items)
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "game_id": game_id,
        "player_id": player_id,
        "session_id": session_id,
        "event_type": "purchase",
        "version": "1.0",
        "item_id": item["id"],
        "item_name": item["name"],
        "currency_type": "real",
        "amount": item["price"],
        "currency_code": "USD"
    }

def generate_progress_event(player_id, session_id, game_id):
    achievements = ["first_win", "speed_demon", "collector", "warrior", "explorer"]
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "game_id": game_id,
        "player_id": player_id,
        "session_id": session_id,
        "event_type": "progress",
        "version": "1.0",
        "level": random.randint(1, 10),
        "xp_earned": random.randint(10, 100),
        "achievements": random.sample(achievements, random.randint(0, 2)),
        "current_state": {
            "health": random.randint(1, 100),
            "coins": random.randint(0, 5000),
            "inventory": random.sample(["sword", "shield", "potion", "map"], random.randint(1, 3))
        }
    }

def simulate_game_session(api_base_url="http://localhost:8000"):
    """Simulate a complete game session with multiple events."""
    player_id = generate_player_id()
    session_id = generate_session_id()
    
    # Start game
    start_event = generate_game_start_event(player_id, session_id)
    game_id = start_event["game_id"]
    response = requests.post(f"{api_base_url}/events/game-start", json=start_event)
    print(f"Game Start Event Response: {response.status_code}")
    
    # Generate 2-5 progress events
    for _ in range(random.randint(2, 5)):
        progress_event = generate_progress_event(player_id, session_id, game_id)
        response = requests.post(f"{api_base_url}/events/progress", json=progress_event)
        print(f"Progress Event Response: {response.status_code}")
        time.sleep(random.uniform(0.5, 2.0))
    
    # Maybe generate a purchase (30% chance)
    if random.random() < 0.3:
        purchase_event = generate_purchase_event(player_id, session_id, game_id)
        response = requests.post(f"{api_base_url}/events/purchase", json=purchase_event)
        print(f"Purchase Event Response: {response.status_code}")
        time.sleep(random.uniform(0.5, 2.0))
    
    # End game
    end_event = generate_game_end_event(player_id, session_id, game_id)
    response = requests.post(f"{api_base_url}/events/game-end", json=end_event)
    print(f"Game End Event Response: {response.status_code}")

def main():
    """Main function to simulate multiple game sessions."""
    print("Starting game session simulation...")
    num_sessions = 10
    
    for i in range(num_sessions):
        print(f"\nSimulating session {i+1}/{num_sessions}")
        try:
            simulate_game_session()
            # Random delay between sessions
            time.sleep(random.uniform(1.0, 3.0))
        except requests.exceptions.RequestException as e:
            print(f"Error in session {i+1}: {e}")
            continue

if __name__ == "__main__":
    main() 