import requests
import json
import time

url = "http://mahir.iotexperience.com/cfd/data"
headers = {"Content-Type": "application/json"}
data = {
    "deviceid": 99,
    "temp": 22.5,
    "hum": 60.2,
    "pressure": 101325,
    "pm1": 12.3,
    "pm25": 15.4,
    "pm10": 20.1,
    "co2": 400
}

start_time = time.perf_counter()
response = requests.post(url, headers=headers, data=json.dumps(data))
end_time = time.perf_counter()

latency = (end_time - start_time) * 1000  # Convert to milliseconds

if response.status_code == 200:
    print("Data successfully posted:", response.json())
else:
    print("Failed to post data. Status code:", response.status_code)

print(f"Request latency: {latency:.2f} ms")
