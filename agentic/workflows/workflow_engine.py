"""
Workflow Engine - n8n-like automation system

Enables building complex workflows with:
- Triggers (schedule, webhook, event)
- Conditional logic (if/else, switch)
- Agent chaining
- Error handling
- Memory/context retention
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class TriggerType(Enum):
    """Types of workflow triggers"""
    SCHEDULE = "schedule"  # Cron-based
    WEBHOOK = "webhook"    # HTTP webhook
    EVENT = "event"        # Internal event
    MANUAL = "manual"      # User-initiated


class NodeType(Enum):
    """Types of workflow nodes"""
    TRIGGER = "trigger"
    AGENT = "agent"
    SWITCH = "switch"
    IF = "if"
    MERGE = "merge"
    DELAY = "delay"
    HTTP = "http"
    TRANSFORM = "transform"


class WorkflowNode:
    """A single node in a workflow"""
    
    def __init__(
        self,
        node_id: str,
        node_type: NodeType,
        config: Dict[str, Any],
        next_nodes: Optional[List[str]] = None
    ):
        self.node_id = node_id
        self.node_type = node_type
        self.config = config
        self.next_nodes = next_nodes or []
    
    async def execute(self, input_data: Any, context: Dict[str, Any]) -> Any:
        """Execute this node"""
        logger.info(f"  🔹 Executing node: {self.node_id} ({self.node_type.value})")
        
        if self.node_type == NodeType.AGENT:
            return await self._execute_agent(input_data, context)
        elif self.node_type == NodeType.SWITCH:
            return await self._execute_switch(input_data, context)
        elif self.node_type == NodeType.IF:
            return await self._execute_if(input_data, context)
        elif self.node_type == NodeType.TRANSFORM:
            return await self._execute_transform(input_data, context)
        else:
            return input_data
    
    async def _execute_agent(self, input_data: Any, context: Dict[str, Any]) -> Any:
        """Execute an agent node"""
        agent_name = self.config.get("agent")
        
        # Get agent from registry
        from agents import get_agent
        agent = get_agent(agent_name)
        
        # Execute agent
        result = await agent.analyze(input_data)
        
        return result
    
    async def _execute_switch(self, input_data: Any, context: Dict[str, Any]) -> Any:
        """Execute a switch node (route based on conditions)"""
        conditions = self.config.get("conditions", [])
        
        for condition in conditions:
            field = condition.get("field")
            operator = condition.get("operator")
            value = condition.get("value")
            
            # Evaluate condition
            if self._evaluate_condition(input_data, field, operator, value):
                return {
                    "route": condition.get("route"),
                    "data": input_data
                }
        
        # Default route
        return {
            "route": "default",
            "data": input_data
        }
    
    async def _execute_if(self, input_data: Any, context: Dict[str, Any]) -> Any:
        """Execute an if node"""
        condition = self.config.get("condition")
        
        if self._evaluate_condition(
            input_data,
            condition.get("field"),
            condition.get("operator"),
            condition.get("value")
        ):
            return {
                "branch": "true",
                "data": input_data
            }
        else:
            return {
                "branch": "false",
                "data": input_data
            }
    
    async def _execute_transform(self, input_data: Any, context: Dict[str, Any]) -> Any:
        """Execute a transform node (modify data)"""
        transformations = self.config.get("transformations", [])
        
        result = input_data.copy() if isinstance(input_data, dict) else input_data
        
        for transform in transformations:
            operation = transform.get("operation")
            field = transform.get("field")
            value = transform.get("value")
            
            if operation == "set":
                result[field] = value
            elif operation == "append":
                if field in result:
                    result[field] += value
            elif operation == "remove":
                result.pop(field, None)
        
        return result
    
    def _evaluate_condition(
        self,
        data: Any,
        field: str,
        operator: str,
        value: Any
    ) -> bool:
        """Evaluate a condition"""
        if not isinstance(data, dict):
            return False
        
        field_value = data.get(field)
        
        if operator == "equals":
            return field_value == value
        elif operator == "not_equals":
            return field_value != value
        elif operator == "contains":
            return value in str(field_value)
        elif operator == "greater_than":
            return field_value > value
        elif operator == "less_than":
            return field_value < value
        else:
            return False


class Workflow:
    """A complete workflow definition"""
    
    def __init__(
        self,
        workflow_id: str,
        name: str,
        trigger: WorkflowNode,
        nodes: Dict[str, WorkflowNode]
    ):
        self.workflow_id = workflow_id
        self.name = name
        self.trigger = trigger
        self.nodes = nodes
        self.execution_history = []
    
    async def execute(self, trigger_data: Any = None) -> Dict[str, Any]:
        """Execute the workflow"""
        logger.info(f"🚀 Executing workflow: {self.name}")
        
        start_time = datetime.utcnow()
        context = {
            "workflow_id": self.workflow_id,
            "start_time": start_time.isoformat(),
            "memory": {}
        }
        
        try:
            # Execute trigger node
            current_data = await self.trigger.execute(trigger_data, context)
            
            # Execute subsequent nodes
            current_nodes = self.trigger.next_nodes
            
            while current_nodes:
                next_nodes = []
                
                for node_id in current_nodes:
                    node = self.nodes.get(node_id)
                    if not node:
                        logger.warning(f"Node not found: {node_id}")
                        continue
                    
                    # Execute node
                    result = await node.execute(current_data, context)
                    
                    # Handle routing
                    if isinstance(result, dict) and "route" in result:
                        # Switch node - route to specific branch
                        route = result["route"]
                        current_data = result["data"]
                        # Find next node based on route
                        for next_node_id in node.next_nodes:
                            if route in next_node_id:
                                next_nodes.append(next_node_id)
                    elif isinstance(result, dict) and "branch" in result:
                        # If node - route based on condition
                        branch = result["branch"]
                        current_data = result["data"]
                        # Find next node based on branch
                        for next_node_id in node.next_nodes:
                            if branch in next_node_id:
                                next_nodes.append(next_node_id)
                    else:
                        # Regular node - continue to all next nodes
                        current_data = result
                        next_nodes.extend(node.next_nodes)
                
                current_nodes = next_nodes
            
            # Record execution
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            execution_record = {
                "workflow_id": self.workflow_id,
                "status": "success",
                "execution_time": execution_time,
                "result": current_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.execution_history.append(execution_record)
            
            logger.info(f"  ✅ Workflow completed in {execution_time:.2f}s")
            
            return execution_record
            
        except Exception as e:
            logger.error(f"  ❌ Workflow failed: {e}")
            
            execution_record = {
                "workflow_id": self.workflow_id,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.execution_history.append(execution_record)
            
            return execution_record


class WorkflowEngine:
    """Manages and executes workflows"""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.triggers: Dict[str, Callable] = {}
        
        logger.info("⚙️  Workflow Engine initialized")
    
    def register_workflow(self, workflow: Workflow):
        """Register a workflow"""
        self.workflows[workflow.workflow_id] = workflow
        logger.info(f"  📋 Registered workflow: {workflow.name}")
    
    async def execute_workflow(
        self,
        workflow_id: str,
        trigger_data: Any = None
    ) -> Dict[str, Any]:
        """Execute a workflow by ID"""
        workflow = self.workflows.get(workflow_id)
        
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        return await workflow.execute(trigger_data)
    
    def create_workflow_from_config(self, config: Dict[str, Any]) -> Workflow:
        """Create a workflow from configuration"""
        workflow_id = config.get("id")
        name = config.get("name")
        
        # Create nodes
        nodes = {}
        trigger_node = None
        
        for node_config in config.get("nodes", []):
            node = WorkflowNode(
                node_id=node_config["id"],
                node_type=NodeType(node_config["type"]),
                config=node_config.get("config", {}),
                next_nodes=node_config.get("next", [])
            )
            
            if node.node_type == NodeType.TRIGGER:
                trigger_node = node
            else:
                nodes[node.node_id] = node
        
        if not trigger_node:
            raise ValueError("Workflow must have a trigger node")
        
        return Workflow(workflow_id, name, trigger_node, nodes)
    
    def get_workflow_stats(self, workflow_id: str) -> Dict[str, Any]:
        """Get statistics for a workflow"""
        workflow = self.workflows.get(workflow_id)
        
        if not workflow:
            return {}
        
        history = workflow.execution_history
        
        successful = [e for e in history if e["status"] == "success"]
        failed = [e for e in history if e["status"] == "failed"]
        
        return {
            "workflow_id": workflow_id,
            "name": workflow.name,
            "total_executions": len(history),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(history) if history else 0.0,
            "avg_execution_time": sum(
                e.get("execution_time", 0) for e in successful
            ) / len(successful) if successful else 0.0
        }


# Example workflow configurations
EXAMPLE_WORKFLOWS = {
    "email_processing": {
        "id": "email_processing",
        "name": "Email Processing Workflow",
        "nodes": [
            {
                "id": "trigger",
                "type": "trigger",
                "config": {"type": "event", "event": "new_email"},
                "next": ["email_agent"]
            },
            {
                "id": "email_agent",
                "type": "agent",
                "config": {"agent": "email"},
                "next": ["urgency_switch"]
            },
            {
                "id": "urgency_switch",
                "type": "switch",
                "config": {
                    "conditions": [
                        {"field": "urgency", "operator": "equals", "value": "high", "route": "high_urgency"},
                        {"field": "urgency", "operator": "equals", "value": "medium", "route": "medium_urgency"},
                    ]
                },
                "next": ["high_urgency_notify", "medium_urgency_calendar", "low_urgency_archive"]
            },
            {
                "id": "high_urgency_notify",
                "type": "agent",
                "config": {"agent": "slack"},
                "next": []
            },
            {
                "id": "medium_urgency_calendar",
                "type": "agent",
                "config": {"agent": "calendar"},
                "next": []
            },
            {
                "id": "low_urgency_archive",
                "type": "agent",
                "config": {"agent": "knowledge"},
                "next": []
            }
        ]
    }
}
