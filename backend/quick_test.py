#!/usr/bin/env python3
import requests
import json

print("Testing LSTM endpoints...")

# Test LSTM endpoint
try:
    payload = {
        "historical_data": [500, 520, 530, 525, 540, 550],
        "months_ahead": 12
    }
    r = requests.post('http://localhost:8888/api/v2/forecast/lstm', json=payload, timeout=5)
    print(f"Status: {r.status_code}")
    print(f"Response: {json.dumps(r.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
