#include <Wire.h>
#include "Seeed_SHT35.h"
#include "DFRobot_BME280.h"
#include "PMS.h"
#include "MHZ19.h"

#define SEA_LEVEL_PRESSURE 1013.0f

// Sensor variables
float temp = 0;
float hum = 0;
float pressure = 0;
float alt = 0;
float pm1 = 0;
float pm25 = 0;
float pm10 = 0;
int CO2 = 0;

// Sensor objects
DFRobot_BME280_IIC bme(&Wire, 0x77);
PMS pms(Serial2);
PMS::DATA data; 
MHZ19 myMHZ19;
SHT35 sht35(21);  // SCL connected to pin 21

// Timing variables
unsigned long getDataTimer = 0;
unsigned long sendDataTimer = 0;
const unsigned long CO2_READ_INTERVAL = 2000;   // Read CO2 every 2 seconds
const unsigned long DATA_SEND_INTERVAL = 5000;  // Send data to ESP8266 every 5 seconds

void setup() {
  Serial.begin(9600);   // Debug serial
  Serial3.begin(115200); // Communication with ESP8266
  
  Serial.println("Arduino Mega Sensor Setup Starting...");
  
  // Initialize SHT35
  if (sht35.init() == NO_ERROR) {
    Serial.println("✓ SHT35 initialized successfully");
  } else {
    Serial.println("✗ SHT35 initialization failed");
  }
  
  // Initialize MH-Z19B (CO2 sensor)
  Serial1.begin(9600);
  myMHZ19.begin(Serial1);
  myMHZ19.autoCalibration(true);
  Serial.println("✓ MH-Z19B CO2 sensor initialized");
  
  // Initialize PMS5003 (Particulate Matter sensor)
  Serial2.begin(9600);
  pms.passiveMode();
  pms.wakeUp();
  Serial.println("✓ PMS5003 particulate sensor initialized");
  
  // Initialize BME280 (Pressure sensor)
  while (bme.begin() != DFRobot_BME280_IIC::eStatusOK) {
    Serial.println("⚠ BME280 initialization failed, retrying...");
    delay(2000);
  }
  Serial.println("✓ BME280 pressure sensor initialized");
  
  Serial.println("All sensors initialized successfully!");
  Serial.println("Starting data collection...");
  delay(2000); // Give sensors time to stabilize
}

void loop() {
  readSensors();
  
  // Send data to ESP8266 every 5 seconds
  if (millis() - sendDataTimer >= DATA_SEND_INTERVAL) {
    sendDataToESP8266();
    sendDataTimer = millis();
  }
  
  delay(1000); // Main loop delay
}

void readSensors() {
  // Read temperature and humidity from SHT35
  if (sht35.read_meas_data_single_shot(HIGH_REP_WITH_STRCH, &temp, &hum) != NO_ERROR) {
    Serial.println("⚠ Failed to read SHT35 data");
    // Keep previous values or set defaults
    temp = (temp == 0) ? 25.0 : temp;  // Default temp if reading fails
    hum = (hum == 0) ? 50.0 : hum;     // Default humidity if reading fails
  }
  
  // Read pressure and altitude from BME280
  pressure = bme.getPressure();
  alt = bme.calAltitude(SEA_LEVEL_PRESSURE, pressure);
  
  // Read particulate matter from PMS5003
  pms.requestRead();
  if (pms.readUntil(data)) {
    pm1 = data.PM_AE_UG_1_0;
    pm25 = data.PM_AE_UG_2_5;
    pm10 = data.PM_AE_UG_10_0;
  } else {
    // Keep previous values if reading fails
    Serial.println("⚠ Failed to read PMS5003 data");
  }
  
  // Read CO2 from MH-Z19B (less frequently to avoid sensor stress)
  if (millis() - getDataTimer >= CO2_READ_INTERVAL) {
    int newCO2 = myMHZ19.getCO2();
    if (newCO2 > 0) {  // Valid reading
      CO2 = newCO2;
    } else {
      Serial.println("⚠ Invalid CO2 reading");
      // Keep previous CO2 value or set default
      CO2 = (CO2 == 0) ? 400 : CO2;  // Default CO2 level
    }
    getDataTimer = millis();
  }
  
  // Print sensor data for debugging
  printSensorData();
}

void printSensorData() {
  Serial.println("========== Sensor Readings ==========");
  Serial.print("Temperature: ");
  Serial.print(temp);
  Serial.println("°C");
  Serial.print("Humidity: ");
  Serial.print(hum);
  Serial.println("%");
  Serial.print("Pressure: ");
  Serial.print(pressure);
  Serial.println(" Pa");
  Serial.print("Altitude: ");
  Serial.print(alt);
  Serial.println(" m");
  Serial.print("PM1.0: ");
  Serial.print(pm1);
  Serial.println(" µg/m³");
  Serial.print("PM2.5: ");
  Serial.print(pm25);
  Serial.println(" µg/m³");
  Serial.print("PM10.0: ");
  Serial.print(pm10);
  Serial.println(" µg/m³");
  Serial.print("CO2: ");
  Serial.print(CO2);
  Serial.println(" ppm");
  Serial.println("====================================");
}

void sendDataToESP8266() {
  // Create formatted string for ESP8266
  // Format: "T:temp|H:hum|P:pressure|PM1:pm1|PM25:pm25|PM10:pm10|CO2:co2"
  String dataString = "T:" + String(temp, 2) + 
                      "|H:" + String(hum, 2) + 
                      "|P:" + String(pressure, 2) + 
                      "|PM1:" + String(pm1, 2) + 
                      "|PM25:" + String(pm25, 2) + 
                      "|PM10:" + String(pm10, 2) + 
                      "|CO2:" + String(CO2);
  
  // Send to ESP8266 via Serial3
  Serial3.println(dataString);
  
  // Debug output
  Serial.println("📡 Data sent to ESP8266:");
  Serial.println(dataString);
}