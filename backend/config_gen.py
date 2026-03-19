import json

def generate_node(node, settings):
    mode = node.get('mode', 'esp32')
    mac = node.get('mac')
    role = node.get('role', 'anchor')
    x = node.get('x', 0.0)
    y = node.get('y', 0.0)
    offset = node.get('calibration_offset', 0)
    
    server_ip = settings.get('local_ip', '192.168.1.100')
    server_url = f"http://{server_ip}:5000/api/telemetry"
    
    json_config = {
        "device_id": mac,
        "device_role": role,
        "broadcast_interval": 2000,
        "network_key": "SECURE_KEY_123",
        "calibration_offset": offset,
        "mode": mode,
        "coordinates": {"x": x, "y": y},
        "server_url": server_url
    }
    
    if mode == 'esp32':
        source = f"""// ESP32 Tracking Node Configuration
#define DEVICE_ID "{mac}"
#define DEVICE_ROLE "{role}"
#define BROADCAST_INTERVAL 2000
#define NETWORK_KEY "SECURE_KEY_123"
#define CALIBRATION_OFFSET {offset}
#define SERVER_URL "{server_url}"
#define WIFI_SSID "YOUR_SSID"
#define WIFI_PASS "YOUR_PASSWORD"
"""
        filename = "config.h"
    else:
        source = f"""# Raspberry Pi Config
{json.dumps(json_config, indent=4)}
"""
        filename = "config.json"
        
    return {
        "json": json.dumps(json_config, indent=2),
        "source": source,
        "filename": filename,
        "snippet": source
    }

def generate_tag(tag, settings):
    mac = tag.get('mac')
    name = tag.get('name', 'Tag')
    category = tag.get('category', 'Asset')
    machine = tag.get('machine', '')
    interval = tag.get('interval', 500)
    
    json_config = {
        "device_id": mac,
        "device_role": "tag",
        "tag_name": name,
        "machine_name": machine,
        "category": category,
        "broadcast_interval": interval,
        "network_key": "SECURE_KEY_123",
        "calibration_offset": 0,
        "tx_power": 4
    }
    
    source = f"""// ESP32 BLE Tag Configuration
#define DEVICE_ID "{mac}"
#define DEVICE_ROLE "tag"
#define TAG_NAME "{name}"
#define MACHINE_NAME "{machine}"
#define CATEGORY "{category}"
#define BROADCAST_INTERVAL {interval}
#define NETWORK_KEY "SECURE_KEY_123"
"""
    
    return {
        "json": json.dumps(json_config, indent=2),
        "source": source,
        "filename": "tag_config.h",
        "snippet": source
    }
