#!/bin/bash
# Restart backend server
cd /Users/kiran/vnr_hackathon/carbonsense/carbonsense/backend

# Kill existing processes
for pid in $(lsof -t -i :8888); do
    echo "Killing process $pid on port 8888"
    kill -TERM $pid 2>/dev/null || true
done

# Wait for port to be freed
sleep 2

# Start fresh backend
echo "Starting backend on port 8888..."
python3 -m uvicorn main:app --port 8888 --reload > /tmp/backend_restart.log 2>&1 &
sleep 3

# Run tests
echo "Running tests..."
python3 test_phase3_lstm.py
