#!/usr/bin/env python3
"""
Database initialization script for GeoSpark
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from app.core.config import settings
from app.core.database import Base, engine
from app.models import *

async def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Parse database URL to get connection details
        db_url = settings.DATABASE_URL
        if db_url.startswith('postgresql://'):
            db_url = db_url.replace('postgresql://', 'postgresql+psycopg2://')
        
        # Extract database name
        db_name = db_url.split('/')[-1]
        base_url = '/'.join(db_url.split('/')[:-1])
        
        print(f"Creating database: {db_name}")
        
        # Connect to PostgreSQL server (not specific database)
        server_url = base_url.replace(db_name, 'postgres')
        server_engine = create_engine(server_url)
        
        with server_engine.connect() as conn:
            # Check if database exists
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
            if result.fetchone():
                print(f"Database '{db_name}' already exists")
            else:
                # Create database
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                print(f"Database '{db_name}' created successfully")
        
        server_engine.dispose()
        
    except Exception as e:
        print(f"Error creating database: {e}")
        print("Make sure PostgreSQL is running and accessible")
        return False
    
    return True

async def create_tables():
    """Create all database tables"""
    try:
        print("Creating database tables...")
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("Database tables created successfully")
        return True
        
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False

async def create_extensions():
    """Create PostgreSQL extensions"""
    try:
        print("Creating PostgreSQL extensions...")
        
        async with engine.begin() as conn:
            # Enable PostGIS extension
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
                print("PostGIS extension enabled")
            except Exception as e:
                print(f"Warning: Could not enable PostGIS extension: {e}")
                print("Make sure PostGIS is installed: sudo apt-get install postgis")
            
            # Enable UUID extension
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))
                print("UUID extension enabled")
            except Exception as e:
                print(f"Warning: Could not enable UUID extension: {e}")
        
        return True
        
    except Exception as e:
        print(f"Error creating extensions: {e}")
        return False

async def insert_sample_data():
    """Insert sample data for testing"""
    try:
        print("Inserting sample data...")
        
        from sqlalchemy.ext.asyncio import AsyncSession
        from app.core.database import async_session_maker
        
        async with async_session_maker() as session:
            # Create sample user
            from app.models import User
            import uuid
            
            sample_user = User(
                id=uuid.uuid4(),
                username="demo_user",
                email="demo@geospark.com",
                hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8Kz8KzK",  # "demo123"
                full_name="Demo User",
                organization="GeoSpark Demo",
                role="user",
                is_active=True
            )
            
            session.add(sample_user)
            await session.commit()
            
            print("Sample data inserted successfully")
        
        return True
        
    except Exception as e:
        print(f"Error inserting sample data: {e}")
        return False

async def main():
    """Main initialization function"""
    print("🚀 Initializing GeoSpark Database...")
    print("=" * 50)
    
    # Check if database URL is configured
    if not settings.DATABASE_URL:
        print("❌ DATABASE_URL not configured in environment variables")
        print("Please set DATABASE_URL in your .env file")
        return False
    
    print(f"Database URL: {settings.DATABASE_URL}")
    print()
    
    # Step 1: Create database
    if not await create_database():
        return False
    
    print()
    
    # Step 2: Create extensions
    if not await create_extensions():
        return False
    
    print()
    
    # Step 3: Create tables
    if not await create_tables():
        return False
    
    print()
    
    # Step 4: Insert sample data
    if not await insert_sample_data():
        return False
    
    print()
    print("✅ Database initialization completed successfully!")
    print("=" * 50)
    print("You can now start the GeoSpark application")
    print("Run: python main.py")
    
    return True

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Database initialization cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)