/*
 * Asset Tracker Pro - Base Tag Firmware
 * Implements standard BLE beacon functionality applying OTA variables.
 */
#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>

// --- OTA OR WIZARD CONFIGURATION ---
// These default values are meant to be overridden by the Dashboard config generator
String device_id = "00:11:22:33:44:55";
String device_role = "tag";
int broadcast_interval = 500;
String network_key = "DEFAULT_KEY";
String tag_name = "Base_Tag";
int calibration_offset = 0; // Not strictly used by broadcaster
// -----------------------------------

BLEAdvertising *pAdvertising;

void setup() {
    Serial.begin(115200);
    Serial.println("Initializing Tag Firmware...");
    Serial.println("ID: " + device_id + " | Role: " + device_role);
    
    // Setup BLE
    BLEDevice::init(tag_name.c_str());
    BLEServer *pServer = BLEDevice::createServer();
    pAdvertising = BLEDevice::getAdvertising();
    
    // Broadcast generic service UUID (E.g. battery or custom tracking service)
    pAdvertising->addServiceUUID("180F"); 
    pAdvertising->setScanResponse(true);
    
    // Convert ms interval to 0.625ms units
    int interval_slots = broadcast_interval / 0.625;
    pAdvertising->setMinPreferred(interval_slots);  
    pAdvertising->setMaxPreferred(interval_slots);
    
    BLEDevice::startAdvertising();
    Serial.println("Broadcasting active: " + tag_name);
}

void loop() {
    // Tag specific logic (e.g. read battery, enter deep sleep)
    delay(1000);
}
