# TrackerPro Complete Setup Guide

Welcome to **TrackerPro**, the easiest way to track your assets indoors! This guide will get you up and running in minutes. 

## 1. System Overview & Requirements

The TrackerPro system consists of three main components:
1.  **Backend Server:** A Python Flask application providing a RESTful API and positioning logic.
2.  **Frontend Dashboard:** A vanilla HTML/JS/CSS web application served directly by the backend.
3.  **Hardware Firmware:** Code for the tracking "Tags" and listening "Nodes" (ESP32 or Raspberry Pi).

**Prerequisites:**
*   **Docker Desktop** installed on your server/computer.
*   **Arduino IDE** (if using ESP32 hardware).
*   **A local Wi-Fi network** that all devices (server, nodes, and tags) can connect to.

---

## 2. Quick Start (Docker - Recommended)

The simplest and most modular way to run TrackerPro is via Docker. This avoids needing to manually install Python, manage dependencies, or launch multiple terminals.

1. Open a terminal in the project folder.
2. Run the system using Docker Compose:
   ```bash
   docker-compose up -d --build
   ```
   *Windows users can simply double-click the `run.bat` script!*
3. Open your browser to `http://localhost:5000`.
4. **Login Credentials:**
    *   **Username:** `admin`
    *   **Password:** `admin0`

*Note: The Docker setup automatically runs a Mock Telemetry simulator in the background so you can immediately see fake "tags" moving around on your dashboard.*

---

## 3. Advanced Setup (Manual Python)

If you prefer not to use Docker, you can run the server directly via Python (requires Python 3.8+).

1.  Open a terminal in the project root directory.
2.  Install the required Python packages:
    ```powershell
    pip install -r backend\requirements.txt
    ```
3.  Start the main server:
    ```powershell
    python backend\app.py
    ```
4.  (Optional) Open a second terminal to run the mock telemetry simulator:
    ```powershell
    python backend\mock_telemetry.py
    ```

---

## 4. Setup your Space via Dashboard

1. Click on **Config Setup** in the sidebar.
2. Go to **Network** and set your **Floor Plan Image URL**. Adjust the **Environmental Factor (Path Loss)** based on obstacles in the room.
3. Go to **Nodes & Tags** and click **Add Node**.
    *   Add at least **3 nodes**.
    *   Place them in the corners of your room.
    *   Accurately measure and enter the X and Y coordinates (in meters) for each node's physical location.

---

## 5. Firmware Setup (Hardware)

The `firmware` folder contains the code needed for your physical tracking devices.

### ESP32 Setup (Arduino IDE)
1.  **Install Arduino IDE:** Download and install from the official Arduino website.
2.  **Add ESP32 Board Support:** Go to *File -> Preferences*. Add `https://dl.espressif.com/dl/package_esp32_index.json` to the *Additional Boards Manager URLs*. Go to *Tools -> Board -> Boards Manager*, search for `esp32`, and install it.
3.  For each node and tag, click the **Package Generator** (blue/green button) in the dashboard setup tables.
4.  Copy the code snippet and paste it into your Arduino IDE.
5.  *Important:* Update the Wi-Fi credentials (`SSID` and `PASSWORD`) and the `SERVER_IP` to match your backend server.
6.  Upload to your ESP32 boards.

---

## 6. Understanding the Dashboard & Troubleshooting

*   **Green Dot:** High confidence! We know exactly where it is.
*   **Yellow/Red Dot:** Low confidence. Maybe it's only being heard by one node.
*   **Telemetry Volume:** Shows you how much data is hitting your server in real-time.

**Troubleshooting:**
*   **Nodes are "Offline":** Check if they are powered on and connected to the same WiFi as the server.
*   **Jumpiness on Map:** This is normal for RSSI tracking. You can adjust "Environmental Factor" in the **Calibration** tab to smooth it out.
*   **No Data:** Make sure the `Server Host IP` in the **Network** tab matches your computer's actual IP address.
