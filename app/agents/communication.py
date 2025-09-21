"""
Agent Communication Manager using Model Context Protocol (MCP)
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

from app.core.logging import agent_logger

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Types of messages in the agent communication protocol"""
    REQUEST = "request"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    ERROR = "error"
    HEARTBEAT = "heartbeat"

class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class AgentMessage:
    """Standard message format for agent communication"""
    id: str
    from_agent: str
    to_agent: str
    message_type: MessageType
    priority: MessagePriority
    content: Dict[str, Any]
    timestamp: datetime
    correlation_id: Optional[str] = None
    requires_response: bool = False
    timeout: Optional[float] = None

class AgentCapabilities:
    """Define agent capabilities"""
    
    def __init__(self, capabilities: List[str]):
        self.capabilities = set(capabilities)
    
    def has_capability(self, capability: str) -> bool:
        return capability in self.capabilities
    
    def add_capability(self, capability: str):
        self.capabilities.add(capability)
    
    def remove_capability(self, capability: str):
        self.capabilities.discard(capability)

class BaseAgent:
    """Base class for all agents in the system"""
    
    def __init__(self, agent_id: str, communication_manager: 'AgentCommunicationManager'):
        self.agent_id = agent_id
        self.communication_manager = communication_manager
        self.capabilities = AgentCapabilities([])
        self.status = "initializing"
        self.last_activity = datetime.utcnow()
        self.message_handlers: Dict[str, Callable] = {}
        self.pending_responses: Dict[str, asyncio.Future] = {}
        
        # Register default handlers
        self.register_handler("heartbeat", self._handle_heartbeat)
        self.register_handler("error", self._handle_error)
    
    async def initialize(self):
        """Initialize the agent"""
        self.status = "active"
        self.last_activity = datetime.utcnow()
        logger.info(f"Agent {self.agent_id} initialized")
    
    async def shutdown(self):
        """Shutdown the agent"""
        self.status = "shutdown"
        logger.info(f"Agent {self.agent_id} shutdown")
    
    def register_handler(self, message_type: str, handler: Callable):
        """Register a message handler"""
        self.message_handlers[message_type] = handler
    
    async def send_message(self, to_agent: str, message_type: str, content: Dict[str, Any], 
                          priority: MessagePriority = MessagePriority.NORMAL,
                          requires_response: bool = False,
                          timeout: Optional[float] = None) -> Optional[AgentMessage]:
        """Send a message to another agent"""
        message = AgentMessage(
            id=str(uuid.uuid4()),
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type=MessageType(message_type),
            priority=priority,
            content=content,
            timestamp=datetime.utcnow(),
            requires_response=requires_response,
            timeout=timeout
        )
        
        return await self.communication_manager.send_message(message)
    
    async def handle_message(self, message: AgentMessage):
        """Handle incoming messages"""
        self.last_activity = datetime.utcnow()
        
        # Log communication
        agent_logger.log_agent_communication(
            message.from_agent,
            message.to_agent,
            message.message_type.value
        )
        
        # Find appropriate handler
        handler = self.message_handlers.get(message.message_type.value)
        if handler:
            try:
                response = await handler(message)
                if message.requires_response and response:
                    await self.send_message(
                        message.from_agent,
                        "response",
                        response,
                        correlation_id=message.id
                    )
            except Exception as e:
                logger.error(f"Error handling message in {self.agent_id}: {e}")
                await self.send_message(
                    message.from_agent,
                    "error",
                    {"error": str(e), "original_message_id": message.id}
                )
        else:
            logger.warning(f"No handler for message type {message.message_type.value} in {self.agent_id}")
    
    async def _handle_heartbeat(self, message: AgentMessage):
        """Handle heartbeat messages"""
        return {"status": self.status, "timestamp": datetime.utcnow().isoformat()}
    
    async def _handle_error(self, message: AgentMessage):
        """Handle error messages"""
        logger.error(f"Received error from {message.from_agent}: {message.content}")
        return None

class AgentCommunicationManager:
    """Manages communication between agents using MCP"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        self.message_processor_task: Optional[asyncio.Task] = None
    
    async def initialize(self):
        """Initialize the communication manager"""
        self.running = True
        self.message_processor_task = asyncio.create_task(self._process_messages())
        logger.info("Agent Communication Manager initialized")
    
    async def shutdown(self):
        """Shutdown the communication manager"""
        self.running = False
        if self.message_processor_task:
            self.message_processor_task.cancel()
            try:
                await self.message_processor_task
            except asyncio.CancelledError:
                pass
        
        # Shutdown all agents
        for agent in self.agents.values():
            await agent.shutdown()
        
        logger.info("Agent Communication Manager shutdown")
    
    async def register_agent(self, agent_id: str, agent: BaseAgent):
        """Register an agent with the communication manager"""
        self.agents[agent_id] = agent
        await agent.initialize()
        logger.info(f"Agent {agent_id} registered")
    
    async def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        if agent_id in self.agents:
            await self.agents[agent_id].shutdown()
            del self.agents[agent_id]
            logger.info(f"Agent {agent_id} unregistered")
    
    async def send_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Send a message between agents"""
        if message.to_agent not in self.agents:
            logger.error(f"Target agent {message.to_agent} not found")
            return None
        
        # Add to message queue
        await self.message_queue.put(message)
        
        # If response required, wait for it
        if message.requires_response:
            future = asyncio.Future()
            self.agents[message.from_agent].pending_responses[message.id] = future
            
            try:
                if message.timeout:
                    response = await asyncio.wait_for(future, timeout=message.timeout)
                else:
                    response = await future
                return response
            except asyncio.TimeoutError:
                logger.error(f"Message {message.id} timed out")
                return None
            finally:
                self.agents[message.from_agent].pending_responses.pop(message.id, None)
        
        return None
    
    async def _process_messages(self):
        """Process messages from the queue"""
        while self.running:
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                
                # Deliver message to target agent
                target_agent = self.agents.get(message.to_agent)
                if target_agent:
                    await target_agent.handle_message(message)
                else:
                    logger.error(f"Target agent {message.to_agent} not found for message {message.id}")
                
                self.message_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    def get_agent_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all registered agents"""
        return {
            agent_id: {
                "status": agent.status,
                "last_activity": agent.last_activity.isoformat(),
                "capabilities": list(agent.capabilities.capabilities)
            }
            for agent_id, agent in self.agents.items()
        }
    
    async def broadcast_message(self, from_agent: str, message_type: str, 
                               content: Dict[str, Any], exclude_self: bool = True):
        """Broadcast a message to all agents"""
        for agent_id in self.agents:
            if exclude_self and agent_id == from_agent:
                continue
            
            await self.send_message(AgentMessage(
                id=str(uuid.uuid4()),
                from_agent=from_agent,
                to_agent=agent_id,
                message_type=MessageType(message_type),
                priority=MessagePriority.NORMAL,
                content=content,
                timestamp=datetime.utcnow()
            ))
    
    async def send_heartbeat(self):
        """Send heartbeat to all agents"""
        await self.broadcast_message(
            "system",
            "heartbeat",
            {"timestamp": datetime.utcnow().isoformat()},
            exclude_self=False
        )