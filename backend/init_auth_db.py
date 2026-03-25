#!/usr/bin/env python3
"""
Database initialization script for CarbonSense Auth Tables.
Creates User and UserEmissions tables with proper relationships.
"""

import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.db_models import Base, User, UserEmissions
from config.db_config import SQLALCHEMY_DATABASE_URL, DB_HOST, DB_NAME, DB_USER

def init_database():
    """Initialize database tables for authentication system."""
    try:
        print("🔗 Connecting to database...")
        engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)
        
        # Test connection
        with engine.connect() as conn:
            print(f"✅ Connected to {DB_NAME} on {DB_HOST}")
        
        # Create all tables
        print("📋 Creating authentication tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ User table created (if not exists)")
        print("✅ UserEmissions table created (if not exists)")
        
        # Create a demo user for testing
        print("\n👤 Creating demo user for testing...")
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Check if demo user exists
        demo_user = session.query(User).filter(User.email == "demo@example.com").first()
        if demo_user:
            print("⚠️  Demo user already exists (demo@example.com)")
            print(f"   User ID: {demo_user.id}")
        else:
            from services.auth_service import AuthService
            demo_user = User(
                name="Demo User",
                email="demo@example.com",
                password_hash=AuthService.hash_password("demo123")
            )
            session.add(demo_user)
            session.commit()
            print("✅ Demo user created successfully!")
            print(f"   Email: demo@example.com")
            print(f"   Password: demo123")
            print(f"   User ID: {demo_user.id}")
        
        session.close()
        
        print("\n✨ Database initialization complete!")
        print("\n📝 Next steps:")
        print("   1. Start the backend: python3 main.py")
        print("   2. Go to http://localhost:3000/register to create an account")
        print("   3. Or use the demo account: demo@example.com / demo123")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing database: {str(e)}")
        print(f"\n⚙️  Check your database connection:")
        print(f"   Host: {DB_HOST}")
        print(f"   Port: 3306")
        print(f"   Database: {DB_NAME}")
        print(f"   User: {DB_USER}")
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
