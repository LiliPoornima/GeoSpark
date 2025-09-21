"""
Database Models for GeoSpark System
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    organization = Column(String(100))
    role = Column(String(20), default="user")  # user, admin, analyst
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    projects = relationship("Project", back_populates="owner")
    analyses = relationship("Analysis", back_populates="user")
    reports = relationship("Report", back_populates="user")

class Project(Base):
    """Project model"""
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    project_type = Column(String(50), nullable=False)  # solar, wind, hydro, hybrid
    status = Column(String(20), default="draft")  # draft, active, completed, cancelled
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Project metadata
    metadata = Column(JSON)
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    sites = relationship("Site", back_populates="project")
    analyses = relationship("Analysis", back_populates="project")
    reports = relationship("Report", back_populates="project")

class Site(Base):
    """Site model for renewable energy locations"""
    __tablename__ = "sites"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    name = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    area_km2 = Column(Float, nullable=False)
    elevation_m = Column(Float)
    
    # Site characteristics
    land_use = Column(String(50))  # agricultural, industrial, residential, etc.
    zoning_status = Column(String(50))
    environmental_sensitivity = Column(String(20))  # low, medium, high
    accessibility_score = Column(Float)
    
    # Site metadata
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="sites")
    analyses = relationship("Analysis", back_populates="site")

class Analysis(Base):
    """Analysis model for storing analysis results"""
    __tablename__ = "analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    analysis_type = Column(String(50), nullable=False)  # site_selection, resource_estimation, cost_evaluation
    analysis_depth = Column(String(20), default="standard")  # basic, standard, comprehensive
    
    # Analysis results
    results = Column(JSON, nullable=False)
    confidence_score = Column(Float)
    processing_time_ms = Column(Integer)
    
    # Analysis metadata
    input_parameters = Column(JSON)
    model_version = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="analyses")
    site = relationship("Site", back_populates="analyses")
    user = relationship("User", back_populates="analyses")

class Report(Base):
    """Report model for storing generated reports"""
    __tablename__ = "reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    report_type = Column(String(50), nullable=False)  # site_analysis, financial_analysis, environmental_impact
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    
    # Report metadata
    format = Column(String(20), default="html")  # html, pdf, markdown
    language = Column(String(10), default="en")
    version = Column(String(20), default="1.0")
    
    # Generation metadata
    generated_at = Column(DateTime, default=datetime.utcnow)
    model_used = Column(String(50))
    processing_time_ms = Column(Integer)
    
    # Relationships
    project = relationship("Project", back_populates="reports")
    user = relationship("User", back_populates="reports")

class DataPoint(Base):
    """Data point model for storing external data"""
    __tablename__ = "data_points"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String(50), nullable=False)  # solar_api, wind_api, weather_api, etc.
    data_type = Column(String(50), nullable=False)  # solar_resource, wind_resource, weather_data, etc.
    
    # Location data
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Data content
    data = Column(JSON, nullable=False)
    metadata = Column(JSON)
    quality_score = Column(Float, default=1.0)
    
    # Timestamps
    data_timestamp = Column(DateTime, nullable=False)  # When the data was collected
    created_at = Column(DateTime, default=datetime.utcnow)  # When it was stored in our system
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SecurityEvent(Base):
    """Security event model for logging security events"""
    __tablename__ = "security_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(50), nullable=False)  # auth_failure, authz_violation, suspicious_activity, etc.
    threat_level = Column(String(20), nullable=False)  # low, medium, high, critical
    description = Column(Text, nullable=False)
    
    # Event details
    source_ip = Column(String(45))  # IPv4 or IPv6
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    user_agent = Column(String(500))
    
    # Event data
    details = Column(JSON)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    resolver = relationship("User", foreign_keys=[resolved_by])

class SystemLog(Base):
    """System log model for application logging"""
    __tablename__ = "system_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    level = Column(String(20), nullable=False)  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    logger_name = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    
    # Log context
    module = Column(String(100))
    function = Column(String(100))
    line_number = Column(Integer)
    
    # Additional data
    extra_data = Column(JSON)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    session_id = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")

class AgentCommunication(Base):
    """Agent communication log model"""
    __tablename__ = "agent_communications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(String(100), nullable=False, unique=True)
    from_agent = Column(String(50), nullable=False)
    to_agent = Column(String(50), nullable=False)
    message_type = Column(String(50), nullable=False)  # request, response, notification, error, heartbeat
    priority = Column(String(20), default="normal")  # low, normal, high, critical
    
    # Message content
    content = Column(JSON, nullable=False)
    correlation_id = Column(String(100))
    requires_response = Column(Boolean, default=False)
    
    # Response tracking
    response_received = Column(Boolean, default=False)
    response_time_ms = Column(Integer)
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    responded_at = Column(DateTime)

class Configuration(Base):
    """System configuration model"""
    __tablename__ = "configurations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(100), nullable=False, unique=True, index=True)
    value = Column(Text, nullable=False)
    value_type = Column(String(20), default="string")  # string, integer, float, boolean, json
    description = Column(Text)
    category = Column(String(50))  # system, security, llm, nlp, ir, etc.
    
    # Configuration metadata
    is_sensitive = Column(Boolean, default=False)
    is_readonly = Column(Boolean, default=False)
    default_value = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    updater = relationship("User")

class APILog(Base):
    """API request/response log model"""
    __tablename__ = "api_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(String(100), nullable=False, unique=True)
    method = Column(String(10), nullable=False)  # GET, POST, PUT, DELETE
    endpoint = Column(String(200), nullable=False)
    query_params = Column(JSON)
    request_body = Column(JSON)
    response_status = Column(Integer, nullable=False)
    response_body = Column(JSON)
    
    # Request context
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    client_ip = Column(String(45))
    user_agent = Column(String(500))
    session_id = Column(String(100))
    
    # Performance metrics
    processing_time_ms = Column(Integer)
    request_size_bytes = Column(Integer)
    response_size_bytes = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")