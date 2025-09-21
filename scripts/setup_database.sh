#!/bin/bash

# GeoSpark Database Setup Script
# This script helps you set up PostgreSQL with PostGIS for GeoSpark

set -e

echo "🚀 GeoSpark Database Setup"
echo "=========================="

# Check if running on Ubuntu/Debian
if command -v apt-get &> /dev/null; then
    echo "📦 Installing PostgreSQL and PostGIS..."
    
    # Update package list
    sudo apt-get update
    
    # Install PostgreSQL
    sudo apt-get install -y postgresql postgresql-contrib
    
    # Install PostGIS
    sudo apt-get install -y postgis postgresql-14-postgis-3
    
    echo "✅ PostgreSQL and PostGIS installed successfully"
    
elif command -v brew &> /dev/null; then
    echo "📦 Installing PostgreSQL and PostGIS via Homebrew..."
    
    # Install PostgreSQL
    brew install postgresql
    
    # Install PostGIS
    brew install postgis
    
    echo "✅ PostgreSQL and PostGIS installed successfully"
    
else
    echo "❌ Unsupported operating system"
    echo "Please install PostgreSQL and PostGIS manually"
    echo "Visit: https://postgis.net/install/"
    exit 1
fi

# Start PostgreSQL service
echo "🔄 Starting PostgreSQL service..."
if command -v systemctl &> /dev/null; then
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
elif command -v brew &> /dev/null; then
    brew services start postgresql
fi

# Wait for PostgreSQL to start
sleep 3

# Create database and user
echo "🗄️ Creating GeoSpark database and user..."

# Get PostgreSQL version
PG_VERSION=$(psql --version | grep -oE '[0-9]+\.[0-9]+' | head -1)

if command -v sudo &> /dev/null; then
    sudo -u postgres psql << EOF
-- Create user
CREATE USER geospark WITH PASSWORD 'geospark123';

-- Create database
CREATE DATABASE geospark_db OWNER geospark;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE geospark_db TO geospark;

-- Connect to the database and enable extensions
\c geospark_db
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\q
EOF
else
    # For macOS with Homebrew
    psql postgres << EOF
-- Create user
CREATE USER geospark WITH PASSWORD 'geospark123';

-- Create database
CREATE DATABASE geospark_db OWNER geospark;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE geospark_db TO geospark;

-- Connect to the database and enable extensions
\c geospark_db
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

\q
EOF
fi

echo "✅ Database and user created successfully"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://geospark:geospark123@localhost:5432/geospark_db
REDIS_URL=redis://localhost:6379/0

# API Keys (Optional - add your keys here)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Security Configuration
SECRET_KEY=your_secret_key_here_change_this_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
APP_NAME=GeoSpark
APP_VERSION=1.0.0
DEBUG=True
HOST=0.0.0.0
PORT=8000

# External APIs (Optional)
SOLAR_API_KEY=your_solar_api_key_here
WIND_API_KEY=your_wind_api_key_here
WEATHER_API_KEY=your_weather_api_key_here

# Elasticsearch Configuration
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_INDEX=renewable_energy_data

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
MAX_REQUESTS_PER_HOUR=1000

# File Upload Configuration
MAX_FILE_SIZE_MB=10
ALLOWED_FILE_TYPES=pdf,txt,csv,json,xlsx

# Monitoring
ENABLE_METRICS=True
METRICS_PORT=9090
EOF
    echo "✅ .env file created"
else
    echo "ℹ️ .env file already exists, skipping creation"
fi

echo ""
echo "🎉 Database setup completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Install Python dependencies: pip install -r requirements.txt"
echo "2. Initialize the database: python scripts/init_db.py"
echo "3. Start the application: python main.py"
echo ""
echo "Database connection details:"
echo "- Host: localhost"
echo "- Port: 5432"
echo "- Database: geospark_db"
echo "- Username: geospark"
echo "- Password: geospark123"
echo ""
echo "⚠️  Remember to change the default password in production!"