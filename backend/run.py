#!/usr/bin/env python3
"""Backend startup script"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run
from main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002, reload=False)
