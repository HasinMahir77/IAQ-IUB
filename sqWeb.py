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
DEFAULT_PASSWORD = "mahirsquare"

# User credentials
users = {
    "arnoy": "63342",  # Read-only user
    "zihan": "zihansquare",  # Read-write user
}

# Set SQLite Web password
env = os.environ.copy()
env["SQLITE_WEB_PASSWORD"] = DEFAULT_PASSWORD

def run_sqlite_web():
    try:
        logger.info(f"🚀 Starting sqlite_web on http://{HOST}:{PORT} with password...")

        # Generate the authentication file with user roles (Read-Only and Read-Write)
        auth_file = "/home/iotexp5/sqlite_web_auth.txt"
        
        # Write the user credentials into the auth file
        with open(auth_file, 'w') as f:
            for username, password in users.items():
                if username == "arnoy":
                    f.write(f"{username}:{password}:r\n")  # 'r' for read-only
                else:
                    f.write(f"{username}:{password}:rw\n")  # 'rw' for read-write

        # Run sqlite_web with authentication
        subprocess.run(
            ["sqlite_web", DB_FILE, "--host", HOST, "--port", PORT, "--password", DEFAULT_PASSWORD, "--auth", auth_file],  # Fix here
            env=env,
            check=True
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to launch sqlite_web: {e}")

if __name__ == "__main__":
    run_sqlite_web()
