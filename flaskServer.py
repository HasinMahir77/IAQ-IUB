from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import pytz

DB_FILE = "sensor_data.db"

def setup_database():
    """Creates the SQLite table if it doesn't exist."""
    try:
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
                altitude REAL,
                pm1 REAL,
                pm2_5 REAL,
                pm10 REAL,
                CO2 REAL
            )
        """)
        conn.commit()
        conn.close()
        print("Database setup complete.")
    except sqlite3.Error as e:
        print(f"Error setting up database: {e}")

def save_to_db(payload):
    """Inserts data into the SQLite database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Get timestamp in GMT+6 (Asia/Dhaka)
        tz = pytz.timezone("Asia/Dhaka")
        timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

        # Log the data
        formatted_data = (
            f"📡 Device {payload['deviceid']} Data Received:\n"
            f"   📅 Timestamp  : {timestamp}\n"
            f"   🌡 Temp       : {payload['air_temperature']}°C\n"
            f"   💧 Humidity   : {payload['humidity']}%\n"
            f"   🌍 Pressure   : {payload['pressure']} Pa\n"
            f"   🏔 Altitude   : {payload['altitude']} m\n"
            f"   🏭 PM1        : {payload['pm1']} µg/m³\n"
            f"   🏭 PM2.5      : {payload['pm2_5']} µg/m³\n"
            f"   🏭 PM10       : {payload['pm10']} µg/m³\n"
            f"   🏭 CO2        : {payload['co2']} ppm\n"
        )
        print(formatted_data)

        # Insert into database
        cursor.execute("""
            INSERT INTO sensor_data (deviceId, timestamp, air_temperature, humidity, pressure, altitude, pm1, pm2_5, pm10, CO2)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            payload["deviceid"], timestamp, payload["air_temperature"], payload["humidity"],
            payload["pressure"], payload["altitude"], payload["pm1"],
            payload["pm2_5"], payload["pm10"], payload["co2"]
        ))

        conn.commit()
        conn.close()
        print("Data saved to database successfully.")
    except sqlite3.Error as e:
        print(f"Error saving data to database: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

app = Flask(__name__)

@app.route('/cfd', methods=['POST'])
def receive_sensor_data():
    try:
        if request.is_json:
            data = request.get_json()
            save_to_db(data)
            print(f"Received JSON data: {data}")
            return jsonify({"status": "success", "message": "JSON received"}), 200
        else:
            return jsonify({"status": "error", "message": "Request must be JSON"}), 400
    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500

if __name__ == '__main__':
    setup_database()
    app.run(host='0.0.0.0', port=5000, debug=True)
