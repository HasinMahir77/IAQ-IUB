import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Number of concurrent posts
NUM_POSTS = 500

url = "http://mahir.iotexperience.com/cfd/data"
headers = {"Content-Type": "application/json"}

def send_post(device_id):
    data = {
        "deviceid": device_id,
        "temp": 22.5,
        "hum": 60.2,
        "pressure": 101325,
        "pm1": 12.3,
        "pm25": 15.4,
        "pm10": 20.1,
        "co2": 400
    }
    start = time.perf_counter()
    response = requests.post(url, headers=headers, data=json.dumps(data))
    end = time.perf_counter()
    latency = (end - start) * 1000  # in milliseconds

    try:
        response.json()
        json_missed = False
    except ValueError:
        json_missed = True

    return {
        "device_id": device_id,
        "status": response.status_code,
        "latency": latency,
        "json_missed": json_missed
    }

latencies = []
missed_jsons = 0

start_benchmark = time.perf_counter()

with ThreadPoolExecutor(max_workers=NUM_POSTS) as executor:
    futures = [executor.submit(send_post, device_id) for device_id in range(10000, 10000 - NUM_POSTS, -1)]
    for future in as_completed(futures):
        result = future.result()
        print(f"Device {result['device_id']}: Status {result['status']}, Latency {result['latency']:.2f} ms")

        latencies.append(result["latency"])
        if result["json_missed"]:
            missed_jsons += 1

end_benchmark = time.perf_counter()

print("\n--- Benchmark Summary ---")
print(f"Number of Posts:    {NUM_POSTS}")
print(f"Max time:    {max(latencies):.2f} ms")
print(f"Min time:    {min(latencies):.2f} ms")
print(f"Average time:{sum(latencies)/len(latencies):.2f} ms")
print(f"JSONs missed:{missed_jsons}")
print(f"Total time:  {end_benchmark - start_benchmark:.2f} s")
