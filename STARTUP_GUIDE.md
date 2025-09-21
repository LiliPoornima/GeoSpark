# 🚀 GeoSpark Complete Setup Guide

Welcome to GeoSpark! This guide will help you get the complete AI-powered renewable energy analysis platform running on your system.

## 📋 What You'll Get

✅ **React/Vite Frontend** - Modern web interface  
✅ **FastAPI Backend** - RESTful API with comprehensive endpoints  
✅ **Database Setup** - PostgreSQL with PostGIS for geospatial data  
✅ **Simplified Demo** - Runs without external dependencies  
✅ **Testing Suite** - Comprehensive testing tools and guides  

## 🎯 Quick Start Options

### Option 1: One-Click Setup (Recommended)
```bash
# Make the setup script executable
chmod +x setup_and_test.sh

# Run complete setup and testing
./setup_and_test.sh
```

This will:
- Check prerequisites
- Install all dependencies
- Set up configuration
- Run comprehensive tests
- Generate a test report

### Option 2: Step-by-Step Setup

#### 1. Prerequisites Check
```bash
# Check Python (3.8+ required)
python --version

# Check Node.js (optional for frontend)
node --version
```

#### 2. Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies (if you want the frontend)
cd frontend
npm install
cd ..
```

#### 3. Configuration
```bash
# Create environment file
cp env.example .env
# Edit .env with your settings
```

#### 4. Database Setup (Optional)
```bash
# For PostgreSQL setup
chmod +x scripts/setup_database.sh
./scripts/setup_database.sh

# Initialize database
python scripts/init_db.py
```

#### 5. Start the Application
```bash
# Start API server
python main.py

# In another terminal, start frontend
cd frontend
npm run dev
```

## 🎮 Demo Mode (No Dependencies Required)

If you want to test GeoSpark without setting up databases or external services:

```bash
# Run the demo
python demo.py

# Or run interactive demo
python demo.py --interactive

# Or use quick start
python quick_start.py
```

## 🌐 Access Points

Once running, you can access:

- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health
- **Frontend Interface**: http://localhost:3000
- **Frontend Login**: Use `demo` / `demo123`

## 🧪 Testing

### Run All Tests
```bash
# Comprehensive API testing
python test_api.py

# Performance testing
python test_api.py --performance-requests 20

# Test with custom URL
python test_api.py --url http://localhost:8000
```

### Manual Testing
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test site analysis
curl -X POST "http://localhost:8000/api/v1/site-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "location": {
      "latitude": 40.7128,
      "longitude": -74.0060,
      "area_km2": 100
    },
    "project_type": "solar"
  }'
```

## 📁 Project Structure

```
GeoSpark/
├── frontend/                 # React/Vite frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   └── contexts/        # React contexts
│   ├── package.json
│   └── vite.config.ts
├── app/                     # FastAPI backend
│   ├── agents/             # AI agents
│   ├── services/           # Business logic
│   ├── api/               # API routes
│   ├── models/            # Database models
│   └── core/              # Core functionality
├── scripts/               # Setup and utility scripts
├── docs/                  # Documentation
├── demo.py               # Demo version
├── main.py               # Main API server
├── test_api.py           # API testing
├── quick_start.py        # Quick start script
└── setup_and_test.sh     # Complete setup script
```

## 🔧 Configuration

### Environment Variables (.env)
```env
# Application
APP_NAME=GeoSpark
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/geospark_db

# Security
SECRET_KEY=your_secret_key_here

# API Keys (Optional)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

### Frontend Configuration
The frontend automatically connects to the API at `http://localhost:8000`. To change this, edit `frontend/src/services/api.ts`.

## 🚨 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
uvicorn main:app --port 8001
```

#### 2. Python Dependencies Issues
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Frontend Build Issues
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

#### 4. Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql

# Test connection
psql -U geospark -d geospark_db -c "\l"
```

### Getting Help

1. **Check the logs**: Look at the console output for error messages
2. **Run tests**: Use `python test_api.py` to diagnose API issues
3. **Check documentation**: Visit `/docs` endpoint for API documentation
4. **Demo mode**: Use `python demo.py` to test without dependencies

## 🎯 Usage Examples

### 1. Site Analysis via API
```python
import requests

# Analyze a solar site
response = requests.post("http://localhost:8000/api/v1/site-analysis", json={
    "location": {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "area_km2": 100
    },
    "project_type": "solar"
})

result = response.json()
print(f"Site Score: {result['analysis']['overall_score']:.1%}")
```

### 2. Text Analysis
```python
import requests

# Analyze renewable energy text
response = requests.post("http://localhost:8000/api/v1/text-analysis", json={
    "text": "This solar farm project shows excellent potential for renewable energy generation.",
    "analysis_type": "general"
})

result = response.json()
print(f"Sentiment: {result['analysis']['llm_analysis']['sentiment']}")
```

### 3. Frontend Usage
1. Open http://localhost:3000
2. Login with `demo` / `demo123`
3. Navigate to "Site Analysis"
4. Enter coordinates and project details
5. Click "Analyze Site"
6. View results and recommendations

## 📊 Performance

### Expected Performance
- **API Response Time**: < 2 seconds for site analysis
- **Frontend Load Time**: < 3 seconds
- **Concurrent Users**: 50+ (depending on hardware)
- **Database Queries**: < 100ms average

### Monitoring
- Health check: `GET /health`
- System status: `GET /api/v1/system-status`
- Data statistics: `GET /api/v1/data-statistics`

## 🔒 Security

### Demo Credentials
- Username: `demo`
- Password: `demo123`

### Production Security
- Change default passwords
- Use strong SECRET_KEY
- Enable HTTPS
- Configure proper CORS
- Set up authentication

## 🚀 Deployment

### Development
```bash
# Start API
python main.py

# Start frontend
cd frontend && npm run dev
```

### Production
```bash
# Build frontend
cd frontend && npm run build

# Start API with production settings
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📈 Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Test the Frontend**: Use the web interface at http://localhost:3000
3. **Run Analysis**: Try different locations and project types
4. **Customize**: Modify the code for your specific needs
5. **Deploy**: Set up for production use

## 🎉 Success!

If you see this message and the tests pass, GeoSpark is successfully running on your system! You now have a complete AI-powered renewable energy analysis platform ready to use.

**Happy analyzing! 🌱⚡**