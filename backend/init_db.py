"""
Database Initialization Script
Creates tables and initializes the database
"""

import sys
from models.db_models import create_tables, engine, Base


def init_database():
    """Initialize the database"""
    print("🔄 Initializing CarbonSense Database...")
    print(f"📍 Database: {engine.url}")
    
    try:
        # Drop all tables first (optional - for clean slate)
        # Base.metadata.drop_all(bind=engine)
        
        # Create all tables
        create_tables()
        
        print("\n✅ Database initialization completed successfully!")
        print("\n📊 Tables created:")
        print("   - user_input_data (User-entered emissions)")
        print("   - historical_data (Training/historical data)")
        print("   - prediction_data (ML predictions)")
        print("   - anomaly_data (Anomaly detection results)")
        print("   - alert_data (Generated alerts)")
        print("   - report_data (Generated reports)")
        print("   - csv_import_log (CSV import audit trail)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error initializing database: {e}")
        return False


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
