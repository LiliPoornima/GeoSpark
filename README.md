# GeoSpark: Renewable Energy Site Selection AI System

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Features](#features)
4. [Responsible AI](#responsible-ai)
5. [Installation](#installation)
6. [Usage](#usage)
7. [Repository Structure](#repository-structure)
8. [Commercialization](#commercialization)
9. [Contributors](#contributors)


## Overview

GeoSpark is a cutting-edge multi-agent AI system designed for renewable energy site selection, location analysis, resource estimation, and cost evaluation. The system integrates Large Language Models (LLMs), Natural Language Processing (NLP), Information Retrieval (IR), and comprehensive security features to provide intelligent decision support for renewable energy projects.

### Key Capabilities
- **Intelligent Site Selection**: AI-powered analysis of geographical locations for renewable energy potential
- **Resource Assessment**: Comprehensive evaluation of solar, wind, and hydroelectric resources
- **Cost Analysis**: Advanced financial modeling and ROI calculations
- **Risk Assessment**: Environmental, regulatory, and technical risk evaluation
- **Report Generation**: Automated report creation with insights and recommendations

### Technology Stack
- **Backend**: FastAPI, Python 3.11+
- **AI/ML**: OpenAI GPT-4, Anthropic Claude, spaCy, NLTK
- **Database**: PostgreSQL with PostGIS for geospatial data
- **Vector Database**: ChromaDB for semantic search
- **Security**: JWT authentication, AES encryption, input sanitization
- **Communication**: Model Context Protocol (MCP), HTTP APIs, WebSocket connections

## System Architecture

### Multi-Agent Components

#### 1. Site Selection Agent
- **Purpose**: Analyzes geographical locations for renewable energy potential
- **Capabilities**: 
  - Geospatial analysis
  - Environmental assessment
  - Regulatory compliance checking
  - Accessibility evaluation
- **Input**: Latitude, longitude, area specifications
- **Output**: Site suitability scores, recommendations, risk assessments

#### 2. Resource Estimation Agent
- **Purpose**: Evaluates renewable energy resources (solar, wind, hydro)
- **Capabilities**:
  - Weather data analysis
  - Resource yield modeling
  - Seasonal variation analysis
  - Uncertainty quantification
- **Input**: Location data, system configuration
- **Output**: Annual generation estimates, capacity factors, resource quality scores

#### 3. Cost Evaluation Agent
- **Purpose**: Calculates project costs and financial viability
- **Capabilities**:
  - CAPEX/OPEX estimation
  - Financial metrics calculation
  - Sensitivity analysis
  - Risk assessment
- **Input**: Project specifications, financial parameters
- **Output**: Cost breakdowns, NPV, IRR, payback periods

#### 4. Security Agent
- **Purpose**: Manages system security and threat detection
- **Capabilities**:
  - Authentication and authorization
  - Input validation and sanitization
  - Threat detection and response
  - Security monitoring
- **Input**: User credentials, system requests
- **Output**: Security assessments, access control decisions

#### 5. Communication Coordinator
- **Purpose**: Facilitates inter-agent communication
- **Capabilities**:
  - Message routing
  - Protocol management
  - Error handling
  - Performance monitoring
- **Protocol**: Model Context Protocol (MCP)

### Data Flow Architecture

```
User Request → API Gateway → Security Agent → Agent Coordinator
                                                      ↓
Site Selection Agent ←→ Resource Estimation Agent ←→ Cost Evaluation Agent
                                                      ↓
LLM Service ←→ NLP Service ←→ IR Service ←→ Database
                                                      ↓
Response Generation → Security Validation → User Response
```

## Features

### Core Functionality

#### Site Analysis
- **Geospatial Analysis**: Comprehensive evaluation of site characteristics
- **Resource Potential**: Solar, wind, and hydro resource assessment
- **Environmental Factors**: Impact assessment and compliance checking
- **Regulatory Analysis**: Permitting requirements and compliance evaluation
- **Accessibility Assessment**: Infrastructure and connectivity analysis

#### Resource Estimation
- **Solar Resource**: Irradiance analysis, capacity factor calculation
- **Wind Resource**: Wind speed analysis, turbine performance modeling
- **Hydro Resource**: Flow analysis, head calculation, generation potential
- **Weather Integration**: Historical and forecast weather data
- **Uncertainty Quantification**: Confidence intervals and risk factors

#### Financial Analysis
- **Cost Modeling**: CAPEX and OPEX estimation
- **Financial Metrics**: NPV, IRR, payback period, LCOE
- **Sensitivity Analysis**: Parameter variation impact assessment
- **Risk Assessment**: Financial and technical risk evaluation
- **Scenario Planning**: Multiple project scenarios comparison

#### AI-Powered Insights
- **Natural Language Processing**: Text analysis and document processing
- **LLM Integration**: Advanced reasoning and decision support
- **Pattern Recognition**: Historical data analysis and trend identification
- **Predictive Modeling**: Future performance and risk prediction
- **Automated Reporting**: Comprehensive report generation

### Security Features

#### Authentication & Authorization
- **JWT Token Authentication**: Secure user authentication
- **Role-Based Access Control**: Granular permission management
- **Multi-Factor Authentication**: Enhanced security options
- **Session Management**: Secure session handling

#### Data Protection
- **Encryption**: AES encryption for sensitive data
- **Input Sanitization**: XSS and injection attack prevention
- **Data Anonymization**: Privacy-preserving data handling
- **Audit Logging**: Comprehensive activity tracking

#### Threat Detection
- **Real-time Monitoring**: Continuous security monitoring
- **Anomaly Detection**: Unusual activity identification
- **Rate Limiting**: API abuse prevention
- **Incident Response**: Automated threat response

### Responsible AI Implementation

#### Fairness & Bias Detection
- **Geographical Bias Detection**: Regional representation analysis
- **Socioeconomic Fairness**: Community impact assessment
- **Demographic Parity**: Equal opportunity evaluation
- **Bias Mitigation**: Automated bias correction strategies

#### Transparency & Explainability
- **Decision Explanations**: Clear reasoning for AI decisions
- **Feature Importance**: Input factor weighting
- **Confidence Scores**: Uncertainty quantification
- **Alternative Scenarios**: Multiple outcome analysis

#### Accountability & Compliance
- **Audit Trails**: Complete decision history tracking
- **Compliance Monitoring**: Regulatory requirement checking
- **Human Oversight**: Human-in-the-loop validation
- **Ethical Guidelines**: AI ethics compliance

## Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ with PostGIS extension
- Redis (for caching)
- Elasticsearch (optional, for advanced search)

### Setup Instructions

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/GeoSpark.git
cd GeoSpark
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

4. **Install Node.js dependencies** (if using frontend):
```bash
cd frontend
npm install
cd ..
```

5. **Set up environment variables**:
```bash
cp env.example .env
# Edit .env with your configuration
```

6. **Initialize the database**:
```bash
python scripts/init_db.py
```

7. **Run database migrations**:
```bash
alembic upgrade head
```

8. **Start the application**:
```bash
# Start backend
python main.py

# Start frontend (in another terminal)
cd frontend
npm start
```

---

## Usage

Once the application is running locally, you can interact with the API endpoints or the web frontend to perform site selection, resource estimation, and cost evaluation.

### Example: Site Selection API Request
```bash
curl -X POST http://localhost:8000/api/v1/site-selection \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 7.8731,
    "longitude": 80.7718,
    "energy_type": "solar"
  }'


```
 ## Repository Structure
GeoSpark/
├── main.py                  # FastAPI entry point
├── app/
│   ├── agents/              # AI agents (site selection, cost, resource)
│   ├── routes/              # API endpoints
│   ├── services/            # Core logic and AI integration
│   ├── database/            # Database models, queries, and setup
│   ├── security/            # JWT, AES, and input sanitization
│   └── utils/               # Helper functions and constants
├── scripts/
│   └── init_db.py           # Database initialization script
├── frontend/                # React/Next.js frontend app
├── requirements.txt         # Python dependencies
├── alembic/                 # Database migrations
├── .env.example             # Environment variable template
└── README.md                # Documentation file


This structure ensures clear separation between backend logic, AI agents, and frontend components for maintainability and scalability.

``
## Commercialization

GeoSpark can be deployed as a commercial SaaS platform for:

Government renewable energy planning

Private-sector site feasibility analysis

Academic research and environmental modeling

**Potential Revenue Streams**

Subscription-based data analysis access

On-demand report generation

Integration with third-party GIS and energy platforms

``
## Contributors
- Lahiruni Ariyawansha – Project Leader /Backend /Agents / Chatbot AI Systems
- Poornima Liyanage – Backend /Agents / API connection
- Durangi Abeykoon – Frontend / Visualization / Agents
- Theekshana Ranasinghe– Frontend / Testing /Agents