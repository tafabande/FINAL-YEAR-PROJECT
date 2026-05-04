# TrackerPro Complete Setup Guide

This document provides a comprehensive technical guide for setting up all elements of the TrackerPro project, from the backend server and frontend dashboard to the physical ESP32/Raspberry Pi hardware firmware.

---

## 1. System Overview & Requirements

The TrackerPro system consists of three main components:
1.  **Backend Server:** A Python Flask application providing a RESTful API and positioning logic.
2.  **Frontend Dashboard:** A vanilla HTML/JS/CSS web application served directly by the backend.
3.  **Hardware Firmware:** Code for the tracking "Tags" and listening "Nodes" (ESP32 or Raspberry Pi).

**Prerequisites:**
*   **Python 3.8+** installed on your server/computer.
*   **Arduino IDE** (if using ESP32 hardware).
*   **A local Wi-Fi network** that all devices (server, nodes, and tags) can connect to.

---

## 2. Backend & Server Setup

The backend handles all telemetry data, calculates positions, and serves the frontend dashboard. It uses SQLite for a zero-configuration database.

### Step 2.1: Install Dependencies
1.  Open a terminal in the project root directory.
2.  (Optional but recommended) Create a virtual environment:
    ```powershell
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  Install the required Python packages:
    ```powershell
    pip install -r backend\requirements.txt
    ```
    *Note: The primary requirement is `Flask==3.0.2`.*

### Step 2.2: Database Initialization
You do not need to run manual migration scripts. The database (`database.db`) automatically initializes and seeds itself with default configurations and admin accounts the first time `models.py` or `app.py` is executed.

### Step 2.3: Starting the Server
You can start the server using the provided batch script or manually:
*   **Using Batch Script:**
    Double-click `run.bat` or execute `.\run.bat` in the terminal. This will start both the main server and the mock telemetry generator.
*   **Manual Start:**
    ```powershell
    python backend\app.py
    ```

The server will start on `http://0.0.0.0:5000`.

---

## 3. Frontend Setup

The frontend does not require a separate Node.js server or build step. It is served statically by the Flask backend.

1.  Ensure the Flask backend is running.
2.  Open your web browser and navigate to: `http://127.0.0.1:5000` (or the IP address of the machine running the server).
3.  **Login Credentials:** The default credentials created upon initialization are:
    *   **Username:** `admin`
    *   **Password:** `admin0`

---

## 4. Firmware Setup (Hardware)

The `firmware` folder contains the code needed for your physical tracking devices.

### Option A: ESP32 Setup (Arduino IDE)
This is the standard approach using low-cost ESP32 microcontrollers.

1.  **Install Arduino IDE:** Download and install from the official Arduino website.
2.  **Add ESP32 Board Support:**
    *   Go to *File -> Preferences*.
    *   Add `https://dl.espressif.com/dl/package_esp32_index.json` to the *Additional Boards Manager URLs*.
    *   Go to *Tools -> Board -> Boards Manager*, search for `esp32`, and install it.
3.  **Flashing a Node (Receiver):**
    *   Open `firmware\esp32_node.ino` in the Arduino IDE.
    *   *Alternative:* You can use the **Package Generator** in the Frontend UI (Config Setup -> Nodes) to generate pre-configured code for a specific node.
    *   Update the Wi-Fi credentials (`SSID` and `PASSWORD`) and the `SERVER_IP` to match your backend server.
    *   Select your ESP32 board in *Tools -> Board* and the correct COM port. Click Upload.
4.  **Flashing a Tag (Broadcaster):**
    *   Open `firmware\esp32_tag.ino`.
    *   *Alternative:* Use the Package Generator in the Frontend UI (Config Setup -> Tags).
    *   Update the Wi-Fi credentials and `SERVER_IP`.
    *   Upload to your ESP32 Tag.

### Option B: Raspberry Pi Node Setup
If you are using Raspberry Pis as listening nodes instead of ESP32s:
1.  Copy `firmware\pi_node.py` to your Raspberry Pi.
2.  Ensure Python 3 is installed on the Pi.
3.  Run the script: `python3 pi_node.py` (You may need to edit the script first to point to your server IP).

---

## 5. System Configuration via UI

Once the server is running and you are logged into the dashboard, you must configure the tracking environment.

1.  **Network & Environment:**
    *   Navigate to **Config Setup**.
    *   Set the **Floor Plan Image URL** to match your facility map.
    *   Adjust the **Environmental Factor (Path Loss)** based on how many obstacles (walls, racks) are in the room.
2.  **Adding Nodes (Anchors):**
    *   Go to the **Nodes & Tags** section.
    *   Click **Add Node**.
    *   You must have at least **3 Nodes** placed around the perimeter of your tracking area for triangulation to work.
    *   Accurately measure and enter the X and Y coordinates (in meters or your preferred unit) for each node's physical location.
3.  **Adding Tags:**
    *   Click **Add Tag**.
    *   Register the MAC address of the ESP32 tag so the system knows what to track.
    *   Assign it a name and category (e.g., "Forklift 1").

---

## 6. Simulation & Testing

If you want to test the software without physical hardware, you can run the mock telemetry generator.

1.  Ensure the main backend server (`app.py`) is running.
2.  In a separate terminal, run:
    ```powershell
    python backend\mock_telemetry.py
    ```
3.  This script will inject simulated RSSI signals into the database. You will immediately see virtual tags moving around on the Live Telemetry dashboard map. (Note: `run.bat` automatically starts this simulator for you).

---
*Setup Complete! You are now ready to begin tracking assets.*
