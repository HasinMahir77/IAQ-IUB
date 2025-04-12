from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import sqlite3
import json
from datetime import datetime
import pytz
# SQLite Database setup
DB_FILE = "sensor_data.db"

def setup_database():
    """Creates the SQLite table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deviceId INTEGER,
            timestamp TEXT,
            air_temperature REAL,
            humidity REAL,
            pressure REAL,
            pm1 REAL,
            pm2_4 REAL,
            pm10 REAL,
            CO2 REAL
        )
    """)
    conn.commit()
    conn.close()

def save_to_db(payload):
    """Inserts MQTT data into the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Get timestamp in GMT +6 (Asia/Dhaka)
    tz = pytz.timezone("Asia/Dhaka")
    timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    # Print the formatted data
    formatted_data = (
        f"📡 Device {payload['deviceid']} Data Received:\n"
        f"   📅 Timestamp  : {timestamp}\n"
        f"   🌡 Temp       : {payload['temp']}°C\n"
        f"   💧 Humidity   : {payload['hum']}%\n"
        f"   🌍 Pressure   : {payload['pressure']} Pa\n"
        f"   🏭 PM1        : {payload['pm1']} µg/m³\n"
        f"   🏭 PM2.5      : {payload['pm25']} µg/m³\n"
        f"   🏭 PM10       : {payload['pm10']} µg/m³\n"
        f"   🏭 CO2        : {payload['co2']} ppm\n"
    )
    print(formatted_data)

    # Insert into database
    cursor.execute("""
        INSERT INTO sensor_data (deviceId, timestamp, air_temperature, humidity, pressure, pm1, pm2_4, pm10, CO2)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (payload["deviceid"], timestamp, payload["temp"], payload["hum"], payload["pressure"], 
          payload["pm1"], payload["pm25"], payload["pm10"], payload["co2"]))
    
    conn.commit()
    conn.close()


app = Flask(__name__)

@app.route('/cfd', methods=['POST'])
def receive_sensor_data():
    if request.is_json:
        data = request.get_json()
        save_to_db(data)
        print("Received JSON data:", data)
        return jsonify({"status": "success", "message": "JSON received"}), 200
    else:
        return jsonify({"status": "error", "message": "Request must be JSON"}), 400

if __name__ == '__main__':
    setup_database()
    app.run(host='0.0.0.0', port=5150, debug=True)
