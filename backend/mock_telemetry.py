import time
import random
import requests
import math

SERVER_URL = "http://127.0.0.1:5000"

NODES = [
    {"mac": "AA:BB:CC:00:00:01", "name": "Node North", "x": 20, "y": 20},
    {"mac": "AA:BB:CC:00:00:02", "name": "Node South", "x": 80, "y": 80},
    {"mac": "AA:BB:CC:00:00:03", "name": "Node East", "x": 80, "y": 20},
]

TAGS = [
    {"mac": "11:22:33:44:55:66", "name": "Forklift A"},
    {"mac": "77:88:99:AA:BB:CC", "name": "Pallet Jack 1"},
]

def setup_nodes():
    print("Registering nodes...")
    for node in NODES:
        res = requests.post(f"{SERVER_URL}/api/nodes", json={
            "mac": node["mac"], "name": node["name"], "mode": "esp32", "x": node["x"], "y": node["y"]
        })
        print(f"Node {node['name']}: {res.status_code}")

def setup_tags():
    print("Registering tags (names)...")
    for tag in TAGS:
        requests.post(f"{SERVER_URL}/api/tags", json={
            "mac": tag["mac"], "name": tag["name"]
        })

def simulate_movement():
    print("Simulating telemetry (press Ctrl+C to stop)...")
    # Tags move in a circle
    angle = 0.0
    while True:
        angle += 0.4
        
        for t_idx, tag in enumerate(TAGS):
            # Calculate fake true position
            cx, cy = 50, 50
            radius = 30 if t_idx == 0 else 15
            speed_mult = 1 if t_idx == 0 else -1.5
            
            true_x = cx + radius * math.cos(angle * speed_mult)
            true_y = cy + radius * math.sin(angle * speed_mult)
            
            # Send RSSI to each node based on distance
            for node in NODES:
                dist = math.sqrt((node["x"] - true_x)**2 + (node["y"] - true_y)**2)
                # Max RSSI is around -30 (close), min is -90 (far)
                rssi = int(max(-95, min(-30, -30 - (dist * 0.8))) + random.uniform(-5, 5))
                
                requests.post(f"{SERVER_URL}/api/telemetry", json={
                    "node_mac": node["mac"],
                    "tag_mac": tag["mac"],
                    "rssi": rssi
                })
        
        time.sleep(2)

if __name__ == '__main__':
    time.sleep(2) # wait for server to start
    try:
        setup_nodes()
        setup_tags()
        simulate_movement()
    except Exception as e:
        print("Error connecting to server:", e)
