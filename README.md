# Indoor Air Quality (IAQ) Monitoring System

## Project Overview
This comprehensive Indoor Air Quality (IAQ) monitoring system is a networked IoT solution designed to collect, transmit, and analyze environmental sensor data in real-time. The project integrates multiple sensors to provide detailed insights into air quality such as air temperature, humidity, carbon dioxide, air pressure, and particulate matter.

## System Architecture
The IAQ monitoring system is a cloud-connected solution that collects sensor data and transmits it to a remote server for storage and analysis:

### Hardware Components
- Arduino Mega
- ESP8266 Wi-Fi Module
- Sensor Suite:
  - SHT35 Temperature and Humidity Sensor
  - BME280 Pressure and Altitude Sensor
  - PMS5003 Particulate Matter Sensor
  - MH-Z19B CO2 Sensor

### Software Components
- Arduino Sensor Collection Code
- ESP8266 Wi-Fi Data Transmission
- Remote Flask Web Server
- Cloud-based SQLite Database
- Data Visualization and Analysis Tools

## Sensor Metrics
The system tracks the following environmental parameters:
- Temperature (°C)
- Humidity (%)
- Atmospheric Pressure (Pa)
- Altitude (m)
- Particulate Matter:
  - PM1.0 (µg/m³)
  - PM2.5 (µg/m³)
  - PM10 (µg/m³)
- Carbon Dioxide (CO2 ppm)

## Key Features
- Real-time sensor data collection
- Wireless data transmission to remote server
- Cloud-based SQLite database storage
- Web-based data access via remote endpoints
- Performance benchmarking
- Remote CSV data export

## Repository Structure
```
hasinmahir77-iaq-iub/
│
├── Node-Device_Codes/
│   ├── Calibration/
│   ├── IAQ_Device_ArduinoCode/
│   ├── IAQ_Device_esp8266Code/
│   └── Libraries/
│
├── benchmark.py        # Performance testing script
├── flaskServer.py      # Remote web server
├── postTest.py         # Standalone data posting test
├── sqWeb.py            # SQLite web interface
└── LICENSE             # MIT License
```

## System Workflow
1. Sensors collect environmental data on Arduino Mega
2. ESP8266 transmits data to remote server at `mahir.iotexperience.com`
3. Flask web server receives and stores data in SQLite database
4. Data can be accessed via web endpoints:
   - Get latest readings
   - Download full device data as CSV
   - Perform performance testing

## Setup and Installation
### Prerequisites
- Arduino IDE
- Python 3.x
- Flask
- Required Python Libraries:
  - requests
  - sqlite3
  - pytz

### Hardware Setup
1. Connect sensors to Arduino Mega
2. Configure ESP8266 for Wi-Fi transmission
3. Set up appropriate serial communication

### Software Configuration
1. Install required Python libraries
2. Configure Wi-Fi credentials in ESP8266 code
3. Set server URL in transmission scripts

## Usage
### Data Collection
1. Power on the Arduino and ESP8266
2. Sensor data will be automatically collected and transmitted
3. Data is stored in the remote SQLite database

### Web Interface
- Access sensor data via remote Flask endpoints
- Retrieve latest readings
- Download full device data as CSV

### Performance Testing
Run `benchmark.py` to test data transmission performance

## Authors
- Hasin Mahir
- Tahfizul Hasan Zihan

## Disclaimer
This project is for educational and research purposes. Ensure proper calibration and maintenance of sensors for accurate readings.
