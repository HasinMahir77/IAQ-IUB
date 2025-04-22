import os
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Define DB path relative to current script
script_dir = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(script_dir, "sensor_data.db")

# SQLite Web configuration
HOST = "127.0.0.1"
PORT = "7001"
PASSWORD = "mahirsquare"

# Add password to environment
env = os.environ.copy()
env["SQLITE_WEB_PASSWORD"] = PASSWORD

def run_sqlite_web():
    try:
        logger.info(f"🚀 Starting sqlite_web on http://{HOST}:{PORT} with password...")
        subprocess.run(
            ["sqlite_web", DB_FILE, "--host", HOST, "--port", PORT, "--password"],
            env=env,
            check=True
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to launch sqlite_web: {e}")

if __name__ == "__main__":
    run_sqlite_web()
