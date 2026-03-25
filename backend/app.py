#!/usr/bin/env python3
"""Simple ASGI app file for uvicorn"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app

# This allows uvicorn to import: uvicorn app:app
