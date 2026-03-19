"""
Asset Tracker Pro - Base Node Firmware (Raspberry Pi)
Requires: bluepy, requests
Run: python3 pi_node.py --config config.json
"""
import time
import requests
import json
import argparse
from bluepy.btle import Scanner, DefaultDelegate

# Base default settings, overriden by config.json
config = {
    "device_id": "FF:EE:DD:CC:BB:AA",
    "device_role": "node",
    "broadcast_interval": 2.0,
    "network_key": "DEFAULT_KEY",
    "calibration_offset": 0,
    "server_url": "http://127.0.0.1:5000/api/telemetry"
}

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        rssi = dev.rssi + config.get("calibration_offset", 0)
        
        payload = {
            "node_mac": config["device_id"],
            "tag_mac": dev.addr,
            "rssi": rssi
        }
        
        headers = {"X-Network-Key": config["network_key"]}
        
        try:
            requests.post(config["server_url"], json=payload, headers=headers, timeout=1)
            print(f"Logged Telemetry -> {payload}")
        except Exception as e:
            pass # Suppress network errors during high frequency scanning

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="Path to OTA config.json", default=None)
    args = parser.parse_args()
    
    if args.config:
        with open(args.config, 'r') as f:
            config.update(json.load(f))
            
    print(f"Started Pi Receiver Node [{config['device_id']}]")
    
    scanner = Scanner().withDelegate(ScanDelegate())
    while True:
        try:
            # interval might be in ms (e.g. 2000) or seconds (e.g. 2.0)
            val = float(config.get("broadcast_interval", 2.0))
            scan_time = val / 1000.0 if val > 10 else val
            scanner.scan(scan_time)
        except Exception as e:
            time.sleep(1)

if __name__ == "__main__":
    main()
