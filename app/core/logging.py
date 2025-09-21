"""
Logging configuration for GeoSpark
"""

import logging
import sys
from typing import Any, Dict
import structlog
from app.core.config import settings

def setup_logging():
    """Setup structured logging"""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.LOG_FORMAT == "json" 
            else structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

class SecurityLogger:
    """Specialized logger for security events"""
    
    def __init__(self):
        self.logger = structlog.get_logger("security")
    
    def log_authentication_attempt(self, user_id: str, success: bool, ip_address: str):
        """Log authentication attempts"""
        self.logger.info(
            "Authentication attempt",
            user_id=user_id,
            success=success,
            ip_address=ip_address
        )
    
    def log_authorization_failure(self, user_id: str, resource: str, action: str):
        """Log authorization failures"""
        self.logger.warning(
            "Authorization failure",
            user_id=user_id,
            resource=resource,
            action=action
        )
    
    def log_data_access(self, user_id: str, data_type: str, operation: str):
        """Log data access events"""
        self.logger.info(
            "Data access",
            user_id=user_id,
            data_type=data_type,
            operation=operation
        )
    
    def log_suspicious_activity(self, activity_type: str, details: Dict[str, Any]):
        """Log suspicious activities"""
        self.logger.warning(
            "Suspicious activity",
            activity_type=activity_type,
            details=details
        )

class AgentLogger:
    """Specialized logger for agent activities"""
    
    def __init__(self):
        self.logger = structlog.get_logger("agents")
    
    def log_agent_communication(self, from_agent: str, to_agent: str, message_type: str):
        """Log inter-agent communication"""
        self.logger.info(
            "Agent communication",
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type
        )
    
    def log_agent_decision(self, agent_id: str, decision: str, reasoning: str):
        """Log agent decisions"""
        self.logger.info(
            "Agent decision",
            agent_id=agent_id,
            decision=decision,
            reasoning=reasoning
        )
    
    def log_agent_error(self, agent_id: str, error: str, context: Dict[str, Any]):
        """Log agent errors"""
        self.logger.error(
            "Agent error",
            agent_id=agent_id,
            error=error,
            context=context
        )

# Global logger instances
security_logger = SecurityLogger()
agent_logger = AgentLogger()