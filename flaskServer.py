from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from datetime import datetime
import pytz
import logging
import os

app = Flask(__name__)

# === Logging setup ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# === Database setup ===
script_dir = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(script_dir, "sensor_data.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_FILE}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class SensorData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deviceId = db.Column(db.Integer)
    timestamp = db.Column(db.String(64))
    air_temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    pressure = db.Column(db.Float)
    altitude = db.Column(db.Float)
    pm1 = db.Column(db.Float)
    pm2_5 = db.Column(db.Float)
    pm10 = db.Column(db.Float)
    co2 = db.Column(db.Float)

# Create the DB tables before anything
with app.app_context():
    db.create_all()
    logger.info("✅ Database initialized")

# === Flask-Admin Setup ===
admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')
admin.add_view(ModelView(SensorData, db.session))

@app.route('/cfd/data', methods=['POST'])
def receive_sensor_data():
    try:
        if request.is_json:
            data = request.get_json()

            tz = pytz.timezone("Asia/Dhaka")
            timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

            new_entry = SensorData(
                deviceId=data.get("deviceid"),
                timestamp=timestamp,
                air_temperature=data.get("temp"),
                humidity=data.get("hum"),
                pressure=data.get("pressure"),
                altitude=10,
                pm1=data.get("pm1"),
                pm2_5=data.get("pm25"),
                pm10=data.get("pm10"),
                co2=data.get("co2")
            )
            db.session.add(new_entry)
            db.session.commit()

            logger.info(f"📡 Device {data['deviceid']} Data Received and Stored.")

            return jsonify({"status": "success", "message": "JSON received"}), 200
        else:
            return jsonify({"status": "error", "message": "Request must be JSON"}), 400
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return jsonify({"status": "error", "message": "Internal server error"}), 500

@app.route('/cfd/test', methods=['GET'])
def test_route():
    return "Server is online", 200

if __name__ == '__main__':
    app.run(port=7000)
