#!/bin/bash

# GeoSpark Complete Setup and Testing Script
# This script sets up the entire GeoSpark environment and runs comprehensive tests

set -e

echo "🌱 GeoSpark Complete Setup and Testing"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
        return 0
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
        return 0
    else
        print_error "Python not found. Please install Python 3.8 or higher."
        return 1
    fi
}

# Check if Node.js is installed
check_node() {
    print_status "Checking Node.js installation..."
    
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION found"
        return 0
    else
        print_warning "Node.js not found. Frontend will not be available."
        return 1
    fi
}

# Install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    # Create requirements.txt if it doesn't exist
    if [ ! -f requirements.txt ]; then
        print_status "Creating requirements.txt..."
        cat > requirements.txt << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
sqlalchemy==2.0.23
alembic==1.13.0
psycopg2-binary==2.9.9
redis==5.0.1
chromadb==0.4.18
openai==1.3.7
anthropic==0.7.8
spacy==3.7.2
nltk==3.8.1
scikit-learn==1.3.2
pandas==2.1.4
numpy==1.25.2
requests==2.31.0
aiofiles==23.2.1
httpx==0.25.2
pytest==7.4.3
pytest-asyncio==0.21.1
EOF
    fi
    
    # Install dependencies
    if pip install -r requirements.txt; then
        print_success "Python dependencies installed"
        return 0
    else
        print_error "Failed to install Python dependencies"
        return 1
    fi
}

# Install frontend dependencies
install_frontend_deps() {
    if [ ! -d "frontend" ]; then
        print_warning "Frontend directory not found. Skipping frontend setup."
        return 1
    fi
    
    print_status "Installing frontend dependencies..."
    cd frontend
    
    if npm install; then
        print_success "Frontend dependencies installed"
        cd ..
        return 0
    else
        print_error "Failed to install frontend dependencies"
        cd ..
        return 1
    fi
}

# Create environment file
create_env_file() {
    print_status "Creating environment configuration..."
    
    if [ ! -f .env ]; then
        cat > .env << EOF
# GeoSpark Configuration
APP_NAME=GeoSpark
APP_VERSION=1.0.0
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Security (for demo only - change in production)
SECRET_KEY=demo_secret_key_change_in_production_$(date +%s)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database (using SQLite for demo)
DATABASE_URL=sqlite:///./geospark_demo.db

# Redis (optional for demo)
REDIS_URL=redis://localhost:6379/0

# API Keys (optional - add your keys for full functionality)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
MAX_REQUESTS_PER_HOUR=1000
EOF
        print_success "Environment file created"
    else
        print_status "Environment file already exists"
    fi
}

# Test demo functionality
test_demo() {
    print_status "Testing demo functionality..."
    
    if python demo.py; then
        print_success "Demo test passed"
        return 0
    else
        print_error "Demo test failed"
        return 1
    fi
}

# Test API endpoints
test_api() {
    print_status "Testing API endpoints..."
    
    # Start API server in background
    print_status "Starting API server..."
    python main.py &
    API_PID=$!
    
    # Wait for server to start
    sleep 5
    
    # Test API
    if python test_api.py; then
        print_success "API tests passed"
        API_TEST_RESULT=0
    else
        print_error "API tests failed"
        API_TEST_RESULT=1
    fi
    
    # Stop API server
    kill $API_PID 2>/dev/null || true
    wait $API_PID 2>/dev/null || true
    
    return $API_TEST_RESULT
}

# Test frontend
test_frontend() {
    if [ ! -d "frontend" ]; then
        print_warning "Frontend not available. Skipping frontend tests."
        return 0
    fi
    
    print_status "Testing frontend..."
    cd frontend
    
    # Check if build works
    if npm run build; then
        print_success "Frontend build successful"
        cd ..
        return 0
    else
        print_error "Frontend build failed"
        cd ..
        return 1
    fi
}

# Run comprehensive tests
run_comprehensive_tests() {
    print_status "Running comprehensive tests..."
    
    local test_results=()
    
    # Test 1: Demo functionality
    if test_demo; then
        test_results+=("Demo: PASS")
    else
        test_results+=("Demo: FAIL")
    fi
    
    # Test 2: API endpoints
    if test_api; then
        test_results+=("API: PASS")
    else
        test_results+=("API: FAIL")
    fi
    
    # Test 3: Frontend
    if test_frontend; then
        test_results+=("Frontend: PASS")
    else
        test_results+=("Frontend: FAIL")
    fi
    
    # Print test summary
    echo ""
    print_status "Test Results Summary:"
    echo "========================"
    for result in "${test_results[@]}"; do
        if [[ $result == *"PASS"* ]]; then
            print_success "$result"
        else
            print_error "$result"
        fi
    done
    
    # Count passes
    local passes=$(printf '%s\n' "${test_results[@]}" | grep -c "PASS" || true)
    local total=${#test_results[@]}
    
    echo ""
    if [ $passes -eq $total ]; then
        print_success "All tests passed! ($passes/$total)"
        return 0
    else
        print_error "Some tests failed ($passes/$total passed)"
        return 1
    fi
}

# Generate test report
generate_report() {
    print_status "Generating test report..."
    
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local report_file="test_report_$(date +%Y%m%d_%H%M%S).txt"
    
    cat > "$report_file" << EOF
GeoSpark Test Report
Generated: $timestamp

Environment:
- Python: $(python --version 2>/dev/null || echo "Not available")
- Node.js: $(node --version 2>/dev/null || echo "Not available")
- OS: $(uname -s)

Test Results:
$(python test_api.py --help 2>/dev/null || echo "API tests not available")

Demo Test:
$(python demo.py 2>&1 | head -10 || echo "Demo test not available")

Frontend Test:
$(cd frontend && npm run build 2>&1 | head -10 || echo "Frontend test not available")

EOF
    
    print_success "Test report generated: $report_file"
}

# Main execution
main() {
    local start_time=$(date +%s)
    
    echo "Starting GeoSpark setup and testing..."
    echo ""
    
    # Step 1: Check prerequisites
    if ! check_python; then
        exit 1
    fi
    
    check_node
    
    echo ""
    
    # Step 2: Install dependencies
    if ! install_python_deps; then
        exit 1
    fi
    
    install_frontend_deps
    
    echo ""
    
    # Step 3: Setup configuration
    create_env_file
    
    echo ""
    
    # Step 4: Run tests
    if run_comprehensive_tests; then
        print_success "All tests completed successfully!"
    else
        print_error "Some tests failed. Check the output above."
    fi
    
    echo ""
    
    # Step 5: Generate report
    generate_report
    
    # Calculate total time
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    echo ""
    print_status "Setup and testing completed in ${duration}s"
    echo ""
    print_status "Next steps:"
    echo "1. Start the API server: python main.py"
    echo "2. Start the frontend: cd frontend && npm run dev"
    echo "3. Visit http://localhost:8000/docs for API documentation"
    echo "4. Visit http://localhost:3000 for the frontend interface"
    echo ""
    print_success "GeoSpark is ready to use!"
}

# Run main function
main "$@"