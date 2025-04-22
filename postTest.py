import requests
import json

url = "http://199.250.210.176/api/cfd"
headers = {"Content-Type": "application/json"}
data = {
    "deviceid": 1,
    "temp": 22.5,
    "hum": 60.2,
    "pressure": 101325,
    "pm1": 12.3,
    "pm25": 15.4,
    "pm10": 20.1,
    "co2": 400
}

response = requests.post(url, headers=headers, data=json.dumps(data))

if response.status_code == 200:
    print("Data successfully posted:", response.json())
else:
    print("Failed to post data. Status code:", response.status_code)
