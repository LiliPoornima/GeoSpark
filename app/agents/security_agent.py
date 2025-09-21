"""
Security Agent for System Protection and Monitoring
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import hashlib
import secrets
from dataclasses import dataclass
from enum import Enum
import re

from app.agents.communication import BaseAgent, AgentMessage, MessagePriority
from app.core.logging import agent_logger, security_logger
from app.core.security import security_manager

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """Threat severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityEvent(Enum):
    """Types of security events"""
    AUTHENTICATION_FAILURE = "auth_failure"
    AUTHORIZATION_VIOLATION = "authz_violation"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DATA_BREACH_ATTEMPT = "data_breach_attempt"
    MALICIOUS_INPUT = "malicious_input"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SYSTEM_INTRUSION = "system_intrusion"

@dataclass
class SecurityAlert:
    """Security alert structure"""
    alert_id: str
    event_type: SecurityEvent
    threat_level: ThreatLevel
    description: str
    timestamp: datetime
    source_ip: str
    user_id: Optional[str]
    details: Dict[str, Any]
    resolved: bool = False

@dataclass
class SecurityPolicy:
    """Security policy definition"""
    policy_id: str
    name: str
    description: str
    rules: List[Dict[str, Any]]
    enabled: bool = True
    created_at: datetime = None

class SecurityAgent(BaseAgent):
    """Agent responsible for system security monitoring and protection"""
    
    def __init__(self, communication_manager):
        super().__init__("security", communication_manager)
        
        # Define capabilities
        self.capabilities.add_capability("threat_detection")
        self.capabilities.add_capability("access_control")
        self.capabilities.add_capability("data_protection")
        self.capabilities.add_capability("incident_response")
        self.capabilities.add_capability("security_monitoring")
        
        # Register message handlers
        self.register_handler("authenticate_user", self._handle_authenticate)
        self.register_handler("authorize_action", self._handle_authorize)
        self.register_handler("scan_input", self._handle_scan_input)
        self.register_handler("monitor_activity", self._handle_monitor_activity)
        self.register_handler("generate_alert", self._handle_generate_alert)
        self.register_handler("respond_to_threat", self._handle_threat_response)
        
        # Security state
        self.active_alerts: Dict[str, SecurityAlert] = {}
        self.security_policies: Dict[str, SecurityPolicy] = {}
        self.blocked_ips: set = set()
        self.suspicious_users: set = set()
        self.failed_attempts: Dict[str, int] = {}
        
        # Initialize default security policies
        self._initialize_default_policies()
    
    def _initialize_default_policies(self):
        """Initialize default security policies"""
        # Authentication policy
        auth_policy = SecurityPolicy(
            policy_id="auth_policy",
            name="Authentication Policy",
            description="Controls user authentication requirements",
            rules=[
                {
                    "type": "max_failed_attempts",
                    "value": 5,
                    "action": "block_user"
                },
                {
                    "type": "password_complexity",
                    "value": "strong",
                    "action": "reject"
                },
                {
                    "type": "session_timeout",
                    "value": 3600,  # 1 hour
                    "action": "logout"
                }
            ],
            created_at=datetime.utcnow()
        )
        
        # Input validation policy
        input_policy = SecurityPolicy(
            policy_id="input_policy",
            name="Input Validation Policy",
            description="Validates and sanitizes user inputs",
            rules=[
                {
                    "type": "sql_injection",
                    "value": True,
                    "action": "block"
                },
                {
                    "type": "xss_protection",
                    "value": True,
                    "action": "sanitize"
                },
                {
                    "type": "file_upload",
                    "value": "restricted",
                    "action": "scan"
                }
            ],
            created_at=datetime.utcnow()
        )
        
        # Rate limiting policy
        rate_policy = SecurityPolicy(
            policy_id="rate_policy",
            name="Rate Limiting Policy",
            description="Controls request rates and prevents abuse",
            rules=[
                {
                    "type": "requests_per_minute",
                    "value": 60,
                    "action": "throttle"
                },
                {
                    "type": "requests_per_hour",
                    "value": 1000,
                    "action": "block"
                }
            ],
            created_at=datetime.utcnow()
        )
        
        self.security_policies = {
            "auth_policy": auth_policy,
            "input_policy": input_policy,
            "rate_policy": rate_policy
        }
    
    async def authenticate_user(self, credentials: Dict[str, Any], 
                             client_ip: str) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """Authenticate user and return result with security context"""
        try:
            username = credentials.get("username")
            password = credentials.get("password")
            
            if not username or not password:
                await self._log_security_event(
                    SecurityEvent.AUTHENTICATION_FAILURE,
                    ThreatLevel.MEDIUM,
                    "Missing credentials",
                    client_ip,
                    username
                )
                return False, None, {"error": "Missing credentials"}
            
            # Check if user is blocked
            if username in self.suspicious_users:
                await self._log_security_event(
                    SecurityEvent.AUTHENTICATION_FAILURE,
                    ThreatLevel.HIGH,
                    "Authentication attempt from blocked user",
                    client_ip,
                    username
                )
                return False, None, {"error": "User account is blocked"}
            
            # Check if IP is blocked
            if client_ip in self.blocked_ips:
                await self._log_security_event(
                    SecurityEvent.AUTHENTICATION_FAILURE,
                    ThreatLevel.HIGH,
                    "Authentication attempt from blocked IP",
                    client_ip,
                    username
                )
                return False, None, {"error": "IP address is blocked"}
            
            # Simulate authentication (in real implementation, check against database)
            is_valid = await self._validate_credentials(username, password)
            
            if is_valid:
                # Reset failed attempts counter
                self.failed_attempts.pop(username, None)
                
                # Generate session token
                session_token = self._generate_session_token(username)
                
                # Log successful authentication
                security_logger.log_authentication_attempt(username, True, client_ip)
                
                return True, session_token, {
                    "user_id": username,
                    "session_token": session_token,
                    "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
                }
            else:
                # Increment failed attempts
                self.failed_attempts[username] = self.failed_attempts.get(username, 0) + 1
                
                # Check if user should be blocked
                max_attempts = self.security_policies["auth_policy"].rules[0]["value"]
                if self.failed_attempts[username] >= max_attempts:
                    self.suspicious_users.add(username)
                    await self._log_security_event(
                        SecurityEvent.AUTHENTICATION_FAILURE,
                        ThreatLevel.HIGH,
                        f"User blocked after {max_attempts} failed attempts",
                        client_ip,
                        username
                    )
                
                # Log failed authentication
                security_logger.log_authentication_attempt(username, False, client_ip)
                
                return False, None, {
                    "error": "Invalid credentials",
                    "remaining_attempts": max_attempts - self.failed_attempts[username]
                }
                
        except Exception as e:
            logger.error(f"Error in authentication: {e}")
            await self._log_security_event(
                SecurityEvent.AUTHENTICATION_FAILURE,
                ThreatLevel.MEDIUM,
                f"Authentication error: {str(e)}",
                client_ip,
                credentials.get("username")
            )
            return False, None, {"error": "Authentication failed"}
    
    async def authorize_action(self, user_id: str, action: str, resource: str,
                             client_ip: str) -> Tuple[bool, Dict[str, Any]]:
        """Authorize user action on resource"""
        try:
            # Check if user is authenticated
            if user_id in self.suspicious_users:
                await self._log_security_event(
                    SecurityEvent.AUTHORIZATION_VIOLATION,
                    ThreatLevel.HIGH,
                    "Authorization attempt from blocked user",
                    client_ip,
                    user_id
                )
                return False, {"error": "User account is blocked"}
            
            # Simulate authorization check (in real implementation, check permissions)
            is_authorized = await self._check_user_permissions(user_id, action, resource)
            
            if is_authorized:
                # Log successful authorization
                security_logger.log_data_access(user_id, resource, action)
                return True, {"authorized": True}
            else:
                # Log authorization failure
                security_logger.log_authorization_failure(user_id, resource, action)
                await self._log_security_event(
                    SecurityEvent.AUTHORIZATION_VIOLATION,
                    ThreatLevel.MEDIUM,
                    f"Unauthorized access attempt: {action} on {resource}",
                    client_ip,
                    user_id
                )
                return False, {"error": "Access denied"}
                
        except Exception as e:
            logger.error(f"Error in authorization: {e}")
            await self._log_security_event(
                SecurityEvent.AUTHORIZATION_VIOLATION,
                ThreatLevel.MEDIUM,
                f"Authorization error: {str(e)}",
                client_ip,
                user_id
            )
            return False, {"error": "Authorization failed"}
    
    async def scan_input(self, input_data: str, input_type: str, 
                        client_ip: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Scan input for malicious content"""
        try:
            # Sanitize input
            sanitized_input = security_manager.sanitize_input(input_data)
            
            # Check for SQL injection
            sql_patterns = [
                r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b)",
                r"(\b(UNION|OR|AND)\b.*\b(SELECT|INSERT|UPDATE|DELETE)\b)",
                r"(\b(EXEC|EXECUTE)\b)",
                r"(\b(SCRIPT|JAVASCRIPT)\b)",
                r"(\b(UNION.*SELECT)\b)"
            ]
            
            for pattern in sql_patterns:
                if re.search(pattern, input_data, re.IGNORECASE):
                    await self._log_security_event(
                        SecurityEvent.MALICIOUS_INPUT,
                        ThreatLevel.HIGH,
                        f"SQL injection attempt detected in {input_type}",
                        client_ip
                    )
                    return False, "", {"threat": "sql_injection", "severity": "high"}
            
            # Check for XSS
            xss_patterns = [
                r"<script.*?>.*?</script>",
                r"javascript:",
                r"on\w+\s*=",
                r"eval\s*\(",
                r"expression\s*\("
            ]
            
            for pattern in xss_patterns:
                if re.search(pattern, input_data, re.IGNORECASE):
                    await self._log_security_event(
                        SecurityEvent.MALICIOUS_INPUT,
                        ThreatLevel.HIGH,
                        f"XSS attempt detected in {input_type}",
                        client_ip
                    )
                    return False, "", {"threat": "xss", "severity": "high"}
            
            # Check for command injection
            cmd_patterns = [
                r"[;&|`$]",
                r"\b(cat|ls|pwd|whoami|id|uname)\b",
                r"\b(rm|del|format|fdisk)\b"
            ]
            
            for pattern in cmd_patterns:
                if re.search(pattern, input_data, re.IGNORECASE):
                    await self._log_security_event(
                        SecurityEvent.MALICIOUS_INPUT,
                        ThreatLevel.MEDIUM,
                        f"Command injection attempt detected in {input_type}",
                        client_ip
                    )
                    return False, "", {"threat": "command_injection", "severity": "medium"}
            
            # Check for suspicious patterns
            suspicious_patterns = [
                r"\.\./",  # Path traversal
                r"\.\.\\",  # Windows path traversal
                r"\x00",  # Null bytes
                r"%00",  # URL encoded null bytes
            ]
            
            for pattern in suspicious_patterns:
                if re.search(pattern, input_data):
                    await self._log_security_event(
                        SecurityEvent.MALICIOUS_INPUT,
                        ThreatLevel.MEDIUM,
                        f"Suspicious pattern detected in {input_type}",
                        client_ip
                    )
                    return False, "", {"threat": "suspicious_pattern", "severity": "medium"}
            
            # Input is clean
            return True, sanitized_input, {"threat": "none", "severity": "low"}
            
        except Exception as e:
            logger.error(f"Error scanning input: {e}")
            await self._log_security_event(
                SecurityEvent.MALICIOUS_INPUT,
                ThreatLevel.MEDIUM,
                f"Input scanning error: {str(e)}",
                client_ip
            )
            return False, "", {"error": "Input scanning failed"}
    
    async def monitor_activity(self, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor user activity for suspicious behavior"""
        try:
            user_id = activity_data.get("user_id")
            action = activity_data.get("action")
            resource = activity_data.get("resource")
            timestamp = datetime.utcnow()
            
            # Check for unusual activity patterns
            suspicious_score = 0
            
            # Check for rapid successive requests
            if self._is_rapid_succession(user_id, timestamp):
                suspicious_score += 30
            
            # Check for unusual access patterns
            if self._is_unusual_access_pattern(user_id, resource):
                suspicious_score += 20
            
            # Check for off-hours access
            if self._is_off_hours_access(timestamp):
                suspicious_score += 10
            
            # Check for bulk data access
            if self._is_bulk_data_access(action, resource):
                suspicious_score += 25
            
            # Determine threat level
            if suspicious_score >= 70:
                threat_level = ThreatLevel.HIGH
            elif suspicious_score >= 40:
                threat_level = ThreatLevel.MEDIUM
            else:
                threat_level = ThreatLevel.LOW
            
            # Log suspicious activity if threshold exceeded
            if suspicious_score >= 40:
                await self._log_security_event(
                    SecurityEvent.SUSPICIOUS_ACTIVITY,
                    threat_level,
                    f"Suspicious activity detected: {action} on {resource}",
                    activity_data.get("client_ip", "unknown"),
                    user_id,
                    {"suspicious_score": suspicious_score, "activity": activity_data}
                )
            
            return {
                "suspicious_score": suspicious_score,
                "threat_level": threat_level.value,
                "monitoring_active": True,
                "recommendations": self._get_monitoring_recommendations(suspicious_score)
            }
            
        except Exception as e:
            logger.error(f"Error monitoring activity: {e}")
            return {"error": "Activity monitoring failed"}
    
    async def generate_alert(self, alert_data: Dict[str, Any]) -> SecurityAlert:
        """Generate security alert"""
        try:
            alert_id = self._generate_alert_id()
            
            alert = SecurityAlert(
                alert_id=alert_id,
                event_type=SecurityEvent(alert_data["event_type"]),
                threat_level=ThreatLevel(alert_data["threat_level"]),
                description=alert_data["description"],
                timestamp=datetime.utcnow(),
                source_ip=alert_data.get("source_ip", "unknown"),
                user_id=alert_data.get("user_id"),
                details=alert_data.get("details", {})
            )
            
            # Store alert
            self.active_alerts[alert_id] = alert
            
            # Log alert generation
            agent_logger.log_agent_decision(
                self.agent_id,
                f"Security alert generated: {alert.event_type.value}",
                f"Threat level: {alert.threat_level.value}, Source: {alert.source_ip}"
            )
            
            # Notify other agents if critical
            if alert.threat_level == ThreatLevel.CRITICAL:
                await self._notify_critical_alert(alert)
            
            return alert
            
        except Exception as e:
            logger.error(f"Error generating alert: {e}")
            raise
    
    async def respond_to_threat(self, threat_data: Dict[str, Any]) -> Dict[str, Any]:
        """Respond to security threats"""
        try:
            threat_type = threat_data.get("threat_type")
            threat_level = ThreatLevel(threat_data.get("threat_level", "medium"))
            source_ip = threat_data.get("source_ip")
            user_id = threat_data.get("user_id")
            
            response_actions = []
            
            if threat_level == ThreatLevel.CRITICAL:
                # Immediate response for critical threats
                if source_ip:
                    self.blocked_ips.add(source_ip)
                    response_actions.append("block_ip")
                
                if user_id:
                    self.suspicious_users.add(user_id)
                    response_actions.append("block_user")
                
                # Generate critical alert
                await self.generate_alert({
                    "event_type": "system_intrusion",
                    "threat_level": "critical",
                    "description": f"Critical threat detected: {threat_type}",
                    "source_ip": source_ip,
                    "user_id": user_id,
                    "details": threat_data
                })
                
            elif threat_level == ThreatLevel.HIGH:
                # Enhanced monitoring for high threats
                response_actions.append("enhanced_monitoring")
                
                if user_id and self.failed_attempts.get(user_id, 0) > 3:
                    self.suspicious_users.add(user_id)
                    response_actions.append("block_user")
            
            elif threat_level == ThreatLevel.MEDIUM:
                # Standard monitoring
                response_actions.append("standard_monitoring")
            
            # Log threat response
            agent_logger.log_agent_decision(
                self.agent_id,
                f"Threat response executed: {threat_type}",
                f"Actions: {', '.join(response_actions)}"
            )
            
            return {
                "response_actions": response_actions,
                "threat_level": threat_level.value,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "responded"
            }
            
        except Exception as e:
            logger.error(f"Error responding to threat: {e}")
            return {"error": "Threat response failed"}
    
    # Helper methods
    async def _validate_credentials(self, username: str, password: str) -> bool:
        """Validate user credentials (simplified implementation)"""
        # In a real implementation, this would check against a secure database
        # For demo purposes, accept any non-empty credentials
        return len(username) > 0 and len(password) > 0
    
    async def _check_user_permissions(self, user_id: str, action: str, resource: str) -> bool:
        """Check user permissions for action on resource (simplified implementation)"""
        # In a real implementation, this would check against a permissions database
        # For demo purposes, allow all authenticated users
        return user_id not in self.suspicious_users
    
    def _generate_session_token(self, username: str) -> str:
        """Generate secure session token"""
        token_data = f"{username}:{datetime.utcnow().timestamp()}:{secrets.token_hex(16)}"
        return hashlib.sha256(token_data.encode()).hexdigest()
    
    def _generate_alert_id(self) -> str:
        """Generate unique alert ID"""
        return f"alert_{datetime.utcnow().timestamp()}_{secrets.token_hex(8)}"
    
    async def _log_security_event(self, event_type: SecurityEvent, threat_level: ThreatLevel,
                                description: str, source_ip: str, user_id: Optional[str] = None,
                                details: Optional[Dict[str, Any]] = None):
        """Log security event"""
        security_logger.log_suspicious_activity(
            event_type.value,
            {
                "threat_level": threat_level.value,
                "description": description,
                "source_ip": source_ip,
                "user_id": user_id,
                "details": details or {}
            }
        )
    
    async def _notify_critical_alert(self, alert: SecurityAlert):
        """Notify other agents of critical security alert"""
        await self.send_message(
            "system",
            "notification",
            {
                "type": "critical_security_alert",
                "alert_id": alert.alert_id,
                "threat_level": alert.threat_level.value,
                "description": alert.description,
                "source_ip": alert.source_ip,
                "timestamp": alert.timestamp.isoformat()
            },
            priority=MessagePriority.CRITICAL
        )
    
    def _is_rapid_succession(self, user_id: str, timestamp: datetime) -> bool:
        """Check if user is making rapid successive requests"""
        # Simplified implementation - in real system, would track request history
        return False
    
    def _is_unusual_access_pattern(self, user_id: str, resource: str) -> bool:
        """Check if user is accessing unusual resources"""
        # Simplified implementation - in real system, would analyze access patterns
        return False
    
    def _is_off_hours_access(self, timestamp: datetime) -> bool:
        """Check if access is during off-hours"""
        hour = timestamp.hour
        return hour < 6 or hour > 22
    
    def _is_bulk_data_access(self, action: str, resource: str) -> bool:
        """Check if action involves bulk data access"""
        bulk_actions = ["export", "download", "bulk_read", "mass_export"]
        return any(bulk_action in action.lower() for bulk_action in bulk_actions)
    
    def _get_monitoring_recommendations(self, suspicious_score: int) -> List[str]:
        """Get monitoring recommendations based on suspicious score"""
        recommendations = []
        
        if suspicious_score >= 70:
            recommendations.extend([
                "Consider immediate user account suspension",
                "Implement enhanced monitoring",
                "Review recent user activities"
            ])
        elif suspicious_score >= 40:
            recommendations.extend([
                "Increase monitoring frequency",
                "Review user access patterns",
                "Consider additional authentication"
            ])
        else:
            recommendations.append("Continue standard monitoring")
        
        return recommendations
    
    # Message handlers
    async def _handle_authenticate(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle authentication requests"""
        credentials = message.content.get("credentials", {})
        client_ip = message.content.get("client_ip", "unknown")
        
        success, token, result = await self.authenticate_user(credentials, client_ip)
        
        return {
            "authentication_result": {
                "success": success,
                "token": token,
                "details": result
            }
        }
    
    async def _handle_authorize(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle authorization requests"""
        user_id = message.content.get("user_id")
        action = message.content.get("action")
        resource = message.content.get("resource")
        client_ip = message.content.get("client_ip", "unknown")
        
        authorized, result = await self.authorize_action(user_id, action, resource, client_ip)
        
        return {
            "authorization_result": {
                "authorized": authorized,
                "details": result
            }
        }
    
    async def _handle_scan_input(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle input scanning requests"""
        input_data = message.content.get("input_data", "")
        input_type = message.content.get("input_type", "text")
        client_ip = message.content.get("client_ip", "unknown")
        
        clean, sanitized_input, result = await self.scan_input(input_data, input_type, client_ip)
        
        return {
            "input_scan_result": {
                "clean": clean,
                "sanitized_input": sanitized_input,
                "scan_details": result
            }
        }
    
    async def _handle_monitor_activity(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle activity monitoring requests"""
        activity_data = message.content
        
        result = await self.monitor_activity(activity_data)
        
        return {"monitoring_result": result}
    
    async def _handle_generate_alert(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle alert generation requests"""
        alert_data = message.content
        
        alert = await self.generate_alert(alert_data)
        
        return {
            "alert": {
                "alert_id": alert.alert_id,
                "event_type": alert.event_type.value,
                "threat_level": alert.threat_level.value,
                "description": alert.description,
                "timestamp": alert.timestamp.isoformat(),
                "source_ip": alert.source_ip,
                "user_id": alert.user_id,
                "details": alert.details,
                "resolved": alert.resolved
            }
        }
    
    async def _handle_threat_response(self, message: AgentMessage) -> Dict[str, Any]:
        """Handle threat response requests"""
        threat_data = message.content
        
        result = await self.respond_to_threat(threat_data)
        
        return {"threat_response": result}