"""
PostgreSQL Database Configuration
Stores credentials and connection details
"""

import os
from urllib.parse import quote
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL Configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
DB_NAME = os.getenv('DB_NAME', 'carbonsense_db')
DB_PORT = int(os.getenv('DB_PORT', 5432))

# URL-encode password to handle special characters
DB_PASSWORD_ENCODED = quote(DB_PASSWORD, safe='')

DB_CONFIG = {
    'host': DB_HOST,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'database': DB_NAME,
    'port': DB_PORT
}

# Connection Pool settings
POOL_CONFIG = {
    'pool_size': 10,
    'max_overflow': 20,
    'pool_timeout': 30,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}

# Database URL with psycopg2 (PostgreSQL driver)
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD_ENCODED}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
