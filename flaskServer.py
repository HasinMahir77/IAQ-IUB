from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import pytz
import logging
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(script_dir, "sensor_data.db")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

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
        logger.info("Database setup complete.")
    except sqlite3.Error as e:
        logger.error(f"Error setting up database: {e}")

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
        logger.info(formatted_data)

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
        logger.info("Data saved to database successfully.")
    except sqlite3.Error as e:
        logger.error(f"Error saving data to database: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

app = Flask(__name__)

@app.route('/cfd', methods=['POST'])
def receive_sensor_data():
    try:
        if request.is_json:
            data = request.get_json()

            # Map the keys from the received data to the expected format
            mapped_data = {
                "deviceid": data.get("deviceid"),
                "air_temperature": data.get("temp"),  # Map 'temp' to 'air_temperature'
                "humidity": data.get("hum"),  # Map 'hum' to 'humidity'
                "pressure": data.get("pressure"),
                "altitude": 10,  # Placeholder if no altitude data is sent
                "pm1": data.get("pm1"),
                "pm2_5": data.get("pm25"),  # Map 'pm25' to 'pm2_5'
                "pm10": data.get("pm10"),
                "co2": data.get("co2")
            }

            save_to_db(mapped_data)
            logger.info(f"Received JSON data: {mapped_data}")
            return jsonify({"status": "success", "message": "JSON received"}), 200
        else:
            logger.warning("Received non-JSON data.")
            return jsonify({"status": "error", "message": "Request must be JSON"}), 400
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500

if __name__ == '__main__':
    setup_database()
    app.run(host='0.0.0.0', port=3000, debug=True)
