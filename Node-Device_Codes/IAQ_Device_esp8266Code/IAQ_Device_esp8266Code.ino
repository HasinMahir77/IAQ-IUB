#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <Ticker.h>

// WiFi credentials - Update these for your network
#define WIFI_SSID "IUB-Wave"
#define WIFI_PASSWORD ""

// Flask server details
#define SERVER_URL "http://mahir.iotexperience.com/cfd/data"

// Device configuration
int deviceid = 4;

// Timers and event handlers
Ticker wifiReconnectTimer;
Ticker dataSendTimer;
Ticker restartTimer;
WiFiEventHandler wifiConnectHandler;
WiFiEventHandler wifiDisconnectHandler;

// Data handling variables
String dataBuffer = "";
bool dataReady = false;
unsigned long lastSerialReadTime = 0;
const unsigned long serialTimeout = 1500; // 1.5 seconds timeout for incomplete data

// Sensor data variables
float temp = 0;
float hum = 0;
float pressure = 0;
float pm1 = 0;
float pm25 = 0;
float pm10 = 0;
int co2 = 0;

// Function prototypes
void onWifiConnect(const WiFiEventStationModeGotIP& event);
void onWifiDisconnect(const WiFiEventStationModeDisconnected& event);
void sendData();
void connectToWifi();
void restartDevice();
void parseDataString(String inputString);
void readSerialData();

void setup() {
    Serial.begin(115200);  // Must match Arduino Mega's Serial3 baud rate
    Serial.println();
    Serial.println("ESP8266 HTTP Client for Keystudio MEGA Plus");
    Serial.println("Connecting to Flask Server: " + String(SERVER_URL));
    Serial.println("Device ID: " + String(deviceid));
    Serial.println("Waiting for data from Arduino Mega via UART...");

    // Register Wi-Fi event handlers
    wifiConnectHandler = WiFi.onStationModeGotIP(onWifiConnect);
    wifiDisconnectHandler = WiFi.onStationModeDisconnected(onWifiDisconnect);

    // Connect to Wi-Fi
    connectToWifi();

    // Set up timer to send data every 10 seconds (Arduino sends every 5 seconds)
    dataSendTimer.attach(10, sendData);
    
    Serial.println("Setup complete. Ready to receive and forward sensor data...");
}

void loop() {
    readSerialData(); // Continuously read and parse serial data
}

void connectToWifi() {
    Serial.println("Connecting to Wi-Fi: " + String(WIFI_SSID));
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
}

void onWifiConnect(const WiFiEventStationModeGotIP& event) {
    Serial.println("Connected to Wi-Fi successfully!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    
    // Cancel restart timer if Wi-Fi reconnects
    if (restartTimer.active()) {
        restartTimer.detach();
        Serial.println("Restart timer canceled - Wi-Fi reconnected.");
    }
}

void onWifiDisconnect(const WiFiEventStationModeDisconnected& event) {
    Serial.println("Disconnected from Wi-Fi.");
    
    // Try to reconnect after 2 seconds
    wifiReconnectTimer.once(2, connectToWifi);
    
    // Start restart timer if not already active
    if (!restartTimer.active()) {
        restartTimer.once(60, restartDevice);
        Serial.println("Restart timer started. Device will restart in 60 seconds if not reconnected.");
    }
}

void parseDataString(String inputString) {
    // Parse data format: "T:22.5|H:60.5|P:1013.2|PM1:5.0|PM25:12.5|PM10:15.0|CO2:400"
    int result = sscanf(inputString.c_str(), "T:%f|H:%f|P:%f|PM1:%f|PM25:%f|PM10:%f|CO2:%d", 
                        &temp, &hum, &pressure, &pm1, &pm25, &pm10, &co2);

    if (result == 7) {
        Serial.println("✓ Data parsed successfully:");
        Serial.printf("  Temperature: %.2f°C\n", temp);
        Serial.printf("  Humidity: %.2f%%\n", hum);
        Serial.printf("  Pressure: %.2f Pa\n", pressure);
        Serial.printf("  PM1: %.2f µg/m³\n", pm1);
        Serial.printf("  PM2.5: %.2f µg/m³\n", pm25);
        Serial.printf("  PM10: %.2f µg/m³\n", pm10);
        Serial.printf("  CO2: %d ppm\n", co2);
        dataReady = true;
    } else {
        Serial.println("✗ Error: Invalid data format received");
        Serial.println("Expected format: T:xx.x|H:xx.x|P:xxxx.x|PM1:xx.x|PM25:xx.x|PM10:xx.x|CO2:xxx");
        Serial.println("Received: " + inputString);
    }
}

void sendData() {
    if (!WiFi.isConnected()) {
        Serial.println("⚠ Wi-Fi not connected. Skipping data transmission.");
        return;
    }

    if (dataReady) {
        // Create JSON payload matching Flask server's expected format
        String payload = "{";
        payload += "\"deviceid\":" + String(deviceid) + ",";
        payload += "\"temp\":" + String(temp, 2) + ",";
        payload += "\"hum\":" + String(hum, 2) + ",";
        payload += "\"pressure\":" + String(pressure, 2) + ",";
        payload += "\"pm1\":" + String(pm1, 2) + ",";
        payload += "\"pm25\":" + String(pm25, 2) + ",";
        payload += "\"pm10\":" + String(pm10, 2) + ",";
        payload += "\"co2\":" + String(co2);
        payload += "}";

        WiFiClient client;
        HTTPClient http;

        http.begin(client, SERVER_URL);
        http.addHeader("Content-Type", "application/json");
        http.setTimeout(5000); // 5 second timeout

        Serial.println("📡 Sending data to Flask server...");
        Serial.println("Payload: " + payload);

        int httpResponseCode = http.POST(payload);

        if (httpResponseCode > 0) {
            String response = http.getString();
            Serial.printf("✓ HTTP Response Code: %d\n", httpResponseCode);
            
            if (httpResponseCode == 200) {
                Serial.println("✓ Data sent successfully!");
                Serial.println("Server response: " + response);
            } else {
                Serial.println("⚠ Server returned non-200 status");
                Serial.println("Response: " + response);
            }
        } else {
            Serial.printf("✗ HTTP POST Failed. Error: %s\n", http.errorToString(httpResponseCode).c_str());
        }

        http.end();
        dataReady = false; // Reset the flag after sending
    } else {
        Serial.println("⚠ No new sensor data available to send");
    }
}

void readSerialData() {
    if (Serial.available()) {
        lastSerialReadTime = millis();

        while (Serial.available()) {
            char incomingChar = Serial.read();
            
            if (incomingChar == '\n' || incomingChar == '\r') {
                if (dataBuffer.length() > 0) {
                    Serial.println("📥 Received from Arduino: " + dataBuffer);
                    parseDataString(dataBuffer);
                    dataBuffer = ""; // Clear buffer after parsing
                }
            } else {
                dataBuffer += incomingChar;
            }
        }
    }

    // Clear incomplete data after timeout
    if (millis() - lastSerialReadTime > serialTimeout && dataBuffer.length() > 0) {
        Serial.println("⚠ UART timeout - clearing incomplete data: " + dataBuffer);
        dataBuffer = "";
    }
}

void restartDevice() {
    Serial.println("🔄 Device has been disconnected for 1 minute. Restarting...");
    delay(1000);
    ESP.restart();
}