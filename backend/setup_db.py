"""
Database Setup Script
Creates the database and initializes tables
"""

import pymysql
from config.db_config import DB_CONFIG, DB_PASSWORD_ENCODED
import sys


def create_database_if_not_exists():
    """Create the carbonsense_db database if it doesn't exist"""
    try:
        # Connect to MySQL without specifying a database
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            port=DB_CONFIG['port']
        )
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        db_name = DB_CONFIG['database']
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.commit()
        
        print(f"✓ Database '{db_name}' ready")
        cursor.close()
        conn.close()
        
        return True
        
    except pymysql.Error as e:
        print(f"❌ MySQL Error: {e}")
        return False


def init_all():
    """Create database and initialize tables"""
    print("🔄 Setting up CarbonSense Database...")
    
    # Step 1: Create database
    print("\n1️⃣  Creating database...")
    if not create_database_if_not_exists():
        return False
    
    # Step 2: Create tables
    print("2️⃣  Creating tables...")
    try:
        from models.db_models import create_tables
        create_tables()
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    print("\n✅ Database setup completed!")
    return True


if __name__ == "__main__":
    success = init_all()
    sys.exit(0 if success else 1)
