# TrackerPro: Dummy's Guide 🚀

Welcome to **TrackerPro**, the easiest way to track your assets indoors! This guide will get you up and running in minutes, even if you've never used a tracking system before.

---

## 1. How it Works (The Simple Version)
*   **Tags:** Small devices attached to your assets (forklifts, pallets, tools). They shout "I'm here!" every second.
*   **Nodes:** Receivers mounted on walls or ceilings. They listen to the tags and tell the server how loud they are (RSSI).
*   **Server:** Calculates exactly where the tag is based on which nodes heard it loudest.

---

## 2. Quick Start Steps 🛠️

### Step A: Start the Server
1. Open a terminal in the project folder.
2. Run the system using the provided batch file:
   ```powershell
   .\run.bat
   ```
3. Open your browser to `http://localhost:5000`.

### Step B: Setup your Space
1. Click on **Config Setup** in the sidebar.
2. Go to **Network** and set your floor plan image URL.
3. Go to **Nodes & Tags** and click **Add Node**.
    *   Add at least **3 nodes**.
    *   Place them in the corners of your room.
    *   Enter their coordinates (e.g., Node 1 at X:0, Y:0; Node 2 at X:100, Y:0, etc.).

### Step C: Prepare the Hardware
1. For each node and tag, click the **Package Generator** (blue/green button) in the setup tables.
2. Copy the code snippet.
3. Paste it into your Arduino IDE and upload it to your ESP32.
    *   *Note: Don't forget to put your WiFi name and password in the code!*

---

## 3. No Hardware? No Problem! (Simulation Mode) 🎮
If you want to see how it looks right now without any real devices:
1. Keep the server running.
2. Open a second terminal.
3. Run the simulation script:
   ```powershell
   python backend\mock_telemetry.py
   ```
4. Go back to the **Live Telemetry** dashboard. You'll see "Forklift A" and "Pallet Jack 1" moving around on your map!

---

## 4. Understanding the Dashboard 📊
*   **Green Dot:** High confidence! We know exactly where it is.
*   **Yellow/Red Dot:** Low confidence. Maybe it's only being heard by one node.
*   **Telemetry Volume:** Shows you how much data is hitting your server in real-time.

---

## 5. Troubleshooting ❓
*   **Nodes are "Offline":** Check if they are powered on and connected to the same WiFi as the server.
*   **Jumpiness on Map:** This is normal for RSSI tracking. You can adjust "Environmental Factor" in the **Calibration** tab to smooth it out.
*   **No Data:** Make sure the `Server Host IP` in the **Network** tab matches your computer's actual IP address.

---
*Happy Tracking!* 📍
