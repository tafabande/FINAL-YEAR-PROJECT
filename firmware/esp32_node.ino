/*
 * Asset Tracker Pro - Base Node Firmware (ESP32)
 * Scans for BLE Tags and POSTs telemetry securely to the local Dashboard.
 */
#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>
#include <WiFi.h>
#include <HTTPClient.h>

// --- OTA OR WIZARD CONFIGURATION ---
String device_id = "AA:BB:CC:DD:EE:FF";
String device_role = "node";
int broadcast_interval = 2000; // Scanning interval window (ms)
String network_key = "DEFAULT_KEY";
int calibration_offset = 0;
String tag_name = ""; // Not used by node
// Networking specifics
String server_url = "http://192.168.1.100:5000/api/telemetry";
String wifi_ssid = "YOUR_WIFI";
String wifi_pass = "YOUR_PASS";
// -----------------------------------

BLEScan* pBLEScan;

class MyAdvertisedDeviceCallbacks: public BLEAdvertisedDeviceCallbacks {
    void onResult(BLEAdvertisedDevice advertisedDevice) {
        String address = advertisedDevice.getAddress().toString().c_str();
        int rssi = advertisedDevice.getRSSI() + calibration_offset;
        
        Serial.printf("Discovered Device: %s / RSSI: %d\n", address.c_str(), rssi);
        
        // Post telemetry. Note: Production should batch these or filter un-registered MACs
        if(WiFi.status() == WL_CONNECTED) {
            HTTPClient http;
            http.begin(server_url);
            http.addHeader("Content-Type", "application/json");
            http.addHeader("X-Network-Key", network_key);
            
            // Generate clean JSON manually for speed
            String payload = "{\"node_mac\":\"" + device_id + "\",\"tag_mac\":\"" + address + "\",\"rssi\":" + String(rssi) + "}";
            
            int httpResponseCode = http.POST(payload);
            http.end();
        }
    }
};

void setup() {
    Serial.begin(115200);
    Serial.println("Initializing Receiver Node: " + device_id);
    
    // Connect tracking Wi-Fi
    WiFi.begin(wifi_ssid.c_str(), wifi_pass.c_str());
    while(WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
    Serial.println("\nWiFi Connected: " + WiFi.localIP().toString());
    
    BLEDevice::init("");
    pBLEScan = BLEDevice::getScan();
    pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
    pBLEScan->setActiveScan(true); 
    pBLEScan->setInterval(100);
    pBLEScan->setWindow(99); 
}

void loop() {
    // Scan synchronously 
    pBLEScan->start(broadcast_interval / 1000, false);
    pBLEScan->clearResults();
    delay(10);
}
