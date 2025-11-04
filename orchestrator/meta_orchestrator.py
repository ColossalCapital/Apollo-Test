"""
Apollo Meta-Orchestrator

Like n8n for AI agents - visual workflow construction and execution.

Features:
- Visual workflow builder
- Drag-and-drop agent nodes
- Conditional branching
- Parallel execution
- Loop support
- Error handling paths
- Real-time execution monitoring
- Workflow templates
- Version control
"""

import logging
from typing import List, Dict, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import json

from workflows.workflow_engine import Workflow, WorkflowStep, WorkflowEngine

logger = logging.getLogger(__name__)


class NodeType(Enum):
    """Types of nodes in workflow"""
    AGENT = "agent"              # AI agent execution
    TRIGGER = "trigger"          # Workflow trigger
    CONDITION = "condition"      # Conditional branch
    LOOP = "loop"                # Loop over items
    PARALLEL = "parallel"        # Parallel execution
    MERGE = "merge"              # Merge parallel branches
    TRANSFORM = "transform"      # Data transformation
    DELAY = "delay"              # Wait/delay
    WEBHOOK = "webhook"          # HTTP webhook
    ERROR_HANDLER = "error_handler"  # Error handling


class ExecutionStatus(Enum):
    """Node execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Connection:
    """
    Connection between nodes
    
    Example:
        connection = Connection(
            from_node="node_1",
            to_node="node_2",
            condition="output.success == true"
        )
    """
    from_node: str
    to_node: str
    condition: Optional[str] = None  # Optional condition for execution
    label: Optional[str] = None      # Label for visual display


@dataclass
class WorkflowNode:
    """
    Node in workflow graph
    
    Example:
        node = WorkflowNode(
            id="node_1",
            type=NodeType.AGENT,
            name="Parse Email",
            agent_name="EmailParserAgent",
            config={
                "input_mapping": {"email": "trigger.email"},
                "output_mapping": {"parsed": "email_data"}
            },
            position={"x": 100, "y": 100}
        )
    """
    id: str
    type: NodeType
    name: str
    
    # Agent-specific
    agent_name: Optional[str] = None
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Visual position (for UI)
    position: Dict[str, int] = field(default_factory=dict)
    
    # Execution state
    status: ExecutionStatus = ExecutionStatus.PENDING
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class VisualWorkflow:
    """
    Visual workflow definition (like n8n)
    
    Example:
        workflow = VisualWorkflow(
            id="visual_meeting_scheduling",
            name="Meeting Scheduling",
            nodes=[
                WorkflowNode(id="trigger", type=NodeType.TRIGGER, ...),
                WorkflowNode(id="parse", type=NodeType.AGENT, ...),
                WorkflowNode(id="check_calendar", type=NodeType.AGENT, ...),
                WorkflowNode(id="condition", type=NodeType.CONDITION, ...),
                WorkflowNode(id="schedule", type=NodeType.AGENT, ...),
                WorkflowNode(id="send_email", type=NodeType.AGENT, ...)
            ],
            connections=[
                Connection(from_node="trigger", to_node="parse"),
                Connection(from_node="parse", to_node="check_calendar"),
                Connection(from_node="check_calendar", to_node="condition"),
                Connection(from_node="condition", to_node="schedule", condition="available"),
                Connection(from_node="schedule", to_node="send_email")
            ]
        )
    """
    id: str
    name: str
    description: str = ""
    
    # Graph structure
    nodes: List[WorkflowNode] = field(default_factory=list)
    connections: List[Connection] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: int = 1
    
    # Settings
    settings: Dict[str, Any] = field(default_factory=dict)


class MetaOrchestrator:
    """
    Meta-Orchestrator for AI agent workflows
    
    Like n8n but for AI agents:
    - Visual workflow builder
    - Drag-and-drop nodes
    - Conditional logic
    - Parallel execution
    - Real-time monitoring
    
    Usage:
        orchestrator = MetaOrchestrator()
        
        # Create visual workflow
        workflow = orchestrator.create_workflow("Meeting Scheduling")
        
        # Add nodes
        trigger = orchestrator.add_node(workflow, NodeType.TRIGGER, "Email Trigger")
        parse = orchestrator.add_node(workflow, NodeType.AGENT, "Parse Email", 
                                      agent_name="EmailParserAgent")
        calendar = orchestrator.add_node(workflow, NodeType.AGENT, "Check Calendar",
                                        agent_name="CalendarAgent")
        
        # Connect nodes
        orchestrator.connect(workflow, trigger, parse)
        orchestrator.connect(workflow, parse, calendar)
        
        # Execute workflow
        result = await orchestrator.execute(workflow, trigger_data)
    """
    
    def __init__(self):
        self.workflows: Dict[str, VisualWorkflow] = {}
        self.agents: Dict[str, Any] = {}
        self.workflow_engine = WorkflowEngine()
        
    # ========================================================================
    # WORKFLOW CONSTRUCTION
    # ========================================================================
    
    def create_workflow(
        self,
        name: str,
        description: str = ""
    ) -> VisualWorkflow:
        """Create a new visual workflow"""
        
        workflow = VisualWorkflow(
            id=f"workflow_{datetime.now().timestamp()}",
            name=name,
            description=description
        )
        
        self.workflows[workflow.id] = workflow
        
        logger.info(f"✅ Created workflow: {name}")
        
        return workflow
    
    def add_node(
        self,
        workflow: VisualWorkflow,
        node_type: NodeType,
        name: str,
        agent_name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        position: Optional[Dict[str, int]] = None
    ) -> WorkflowNode:
        """Add a node to workflow"""
        
        node = WorkflowNode(
            id=f"node_{len(workflow.nodes)}",
            type=node_type,
            name=name,
            agent_name=agent_name,
            config=config or {},
            position=position or {"x": 0, "y": 0}
        )
        
        workflow.nodes.append(node)
        workflow.updated_at = datetime.now()
        
        logger.info(f"   ➕ Added node: {name} ({node_type.value})")
        
        return node
    
    def connect(
        self,
        workflow: VisualWorkflow,
        from_node: WorkflowNode,
        to_node: WorkflowNode,
        condition: Optional[str] = None,
        label: Optional[str] = None
    ):
        """Connect two nodes"""
        
        connection = Connection(
            from_node=from_node.id,
            to_node=to_node.id,
            condition=condition,
            label=label
        )
        
        workflow.connections.append(connection)
        workflow.updated_at = datetime.now()
        
        logger.info(f"   🔗 Connected: {from_node.name} → {to_node.name}")
    
    def add_conditional_branch(
        self,
        workflow: VisualWorkflow,
        condition_node: WorkflowNode,
        true_node: WorkflowNode,
        false_node: WorkflowNode,
        condition: str
    ):
        """Add conditional branching"""
        
        self.connect(workflow, condition_node, true_node, 
                    condition=condition, label="true")
        self.connect(workflow, condition_node, false_node, 
                    condition=f"!({condition})", label="false")
        
        logger.info(f"   🔀 Added conditional branch")
    
    def add_parallel_execution(
        self,
        workflow: VisualWorkflow,
        split_node: WorkflowNode,
        parallel_nodes: List[WorkflowNode],
        merge_node: WorkflowNode
    ):
        """Add parallel execution paths"""
        
        # Connect split to all parallel nodes
        for node in parallel_nodes:
            self.connect(workflow, split_node, node)
        
        # Connect all parallel nodes to merge
        for node in parallel_nodes:
            self.connect(workflow, node, merge_node)
        
        logger.info(f"   ⚡ Added parallel execution ({len(parallel_nodes)} branches)")
    
    def add_loop(
        self,
        workflow: VisualWorkflow,
        loop_start: WorkflowNode,
        loop_body: List[WorkflowNode],
        loop_end: WorkflowNode,
        condition: str
    ):
        """Add loop structure"""
        
        # Connect start to first body node
        self.connect(workflow, loop_start, loop_body[0])
        
        # Connect body nodes
        for i in range(len(loop_body) - 1):
            self.connect(workflow, loop_body[i], loop_body[i+1])
        
        # Connect last body node back to start (loop)
        self.connect(workflow, loop_body[-1], loop_start, 
                    condition=condition, label="continue")
        
        # Connect start to end (exit loop)
        self.connect(workflow, loop_start, loop_end, 
                    condition=f"!({condition})", label="exit")
        
        logger.info(f"   🔁 Added loop structure")
    
    # ========================================================================
    # WORKFLOW EXECUTION
    # ========================================================================
    
    async def execute(
        self,
        workflow: VisualWorkflow,
        trigger_data: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """
        Execute visual workflow
        
        Returns:
            {
                'success': bool,
                'execution_id': str,
                'results': Dict[node_id, result],
                'execution_path': List[node_id],
                'duration_seconds': float
            }
        """
        
        logger.info(f"🚀 Executing workflow: {workflow.name}")
        
        started_at = datetime.now()
        execution_id = f"exec_{started_at.timestamp()}"
        
        # Initialize state
        state = {
            "trigger": trigger_data,
            "user_id": user_id,
            "nodes": {}  # Store node outputs
        }
        
        results = {}
        execution_path = []
        
        try:
            # Find trigger node
            trigger_node = next(
                (n for n in workflow.nodes if n.type == NodeType.TRIGGER),
                None
            )
            
            if not trigger_node:
                return {
                    'success': False,
                    'error': 'No trigger node found'
                }
            
            # Execute from trigger
            await self._execute_node(
                workflow, trigger_node, state, results, execution_path
            )
            
            completed_at = datetime.now()
            duration = (completed_at - started_at).total_seconds()
            
            logger.info(f"✅ Workflow completed: {workflow.name}")
            logger.info(f"   Duration: {duration:.2f}s")
            logger.info(f"   Nodes executed: {len(execution_path)}")
            
            return {
                'success': True,
                'execution_id': execution_id,
                'workflow_id': workflow.id,
                'results': results,
                'execution_path': execution_path,
                'duration_seconds': duration,
                'final_state': state
            }
            
        except Exception as e:
            logger.error(f"❌ Workflow failed: {e}")
            
            return {
                'success': False,
                'execution_id': execution_id,
                'error': str(e),
                'results': results,
                'execution_path': execution_path
            }
    
    async def _execute_node(
        self,
        workflow: VisualWorkflow,
        node: WorkflowNode,
        state: Dict[str, Any],
        results: Dict[str, Any],
        execution_path: List[str]
    ):
        """Execute a single node and follow connections"""
        
        # Skip if already executed
        if node.id in execution_path:
            return
        
        logger.info(f"   Executing: {node.name} ({node.type.value})")
        
        node.status = ExecutionStatus.RUNNING
        node.started_at = datetime.now()
        execution_path.append(node.id)
        
        try:
            # Execute based on node type
            if node.type == NodeType.TRIGGER:
                result = state["trigger"]
                
            elif node.type == NodeType.AGENT:
                result = await self._execute_agent_node(node, state)
                
            elif node.type == NodeType.CONDITION:
                result = await self._execute_condition_node(node, state)
                
            elif node.type == NodeType.LOOP:
                result = await self._execute_loop_node(workflow, node, state, results, execution_path)
                
            elif node.type == NodeType.PARALLEL:
                result = await self._execute_parallel_node(workflow, node, state, results, execution_path)
                
            elif node.type == NodeType.TRANSFORM:
                result = await self._execute_transform_node(node, state)
                
            elif node.type == NodeType.DELAY:
                result = await self._execute_delay_node(node, state)
                
            else:
                result = {}
            
            # Store result
            node.output = result
            node.status = ExecutionStatus.COMPLETED
            node.completed_at = datetime.now()
            
            results[node.id] = result
            state["nodes"][node.id] = result
            
            # Find and execute next nodes
            next_nodes = self._get_next_nodes(workflow, node, state)
            
            for next_node in next_nodes:
                await self._execute_node(
                    workflow, next_node, state, results, execution_path
                )
                
        except Exception as e:
            logger.error(f"   ❌ Node failed: {node.name} - {e}")
            
            node.status = ExecutionStatus.FAILED
            node.error = str(e)
            node.completed_at = datetime.now()
            
            # Try error handler
            error_handler = self._find_error_handler(workflow, node)
            if error_handler:
                await self._execute_node(
                    workflow, error_handler, state, results, execution_path
                )
            else:
                raise
    
    async def _execute_agent_node(
        self,
        node: WorkflowNode,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute an AI agent node"""
        
        agent = self.agents.get(node.agent_name)
        if not agent:
            raise ValueError(f"Agent not found: {node.agent_name}")
        
        # Map inputs
        agent_input = self._map_inputs(node.config.get("input_mapping", {}), state)
        
        # Execute agent
        result = await agent.execute(agent_input)
        
        return result
    
    async def _execute_condition_node(
        self,
        node: WorkflowNode,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a condition node"""
        
        condition = node.config.get("condition", "")
        
        # Evaluate condition
        # TODO: Implement safe condition evaluation
        result = eval(condition, {"state": state})
        
        return {"condition_result": result}
    
    async def _execute_loop_node(
        self,
        workflow: VisualWorkflow,
        node: WorkflowNode,
        state: Dict[str, Any],
        results: Dict[str, Any],
        execution_path: List[str]
    ) -> Dict[str, Any]:
        """Execute a loop node"""
        
        items = node.config.get("items", [])
        loop_results = []
        
        for item in items:
            # Create loop state
            loop_state = {**state, "loop_item": item}
            
            # Execute loop body
            # TODO: Implement loop body execution
            
            loop_results.append({})
        
        return {"loop_results": loop_results}
    
    async def _execute_parallel_node(
        self,
        workflow: VisualWorkflow,
        node: WorkflowNode,
        state: Dict[str, Any],
        results: Dict[str, Any],
        execution_path: List[str]
    ) -> Dict[str, Any]:
        """Execute parallel branches"""
        
        # Get all outgoing connections
        next_nodes = self._get_next_nodes(workflow, node, state)
        
        # Execute in parallel
        tasks = [
            self._execute_node(workflow, next_node, state, results, execution_path)
            for next_node in next_nodes
        ]
        
        await asyncio.gather(*tasks)
        
        return {"parallel_completed": True}
    
    async def _execute_transform_node(
        self,
        node: WorkflowNode,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a data transformation node"""
        
        transform = node.config.get("transform", {})
        
        # Apply transformation
        result = {}
        for key, value_path in transform.items():
            result[key] = self._get_value_from_path(state, value_path)
        
        return result
    
    async def _execute_delay_node(
        self,
        node: WorkflowNode,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a delay node"""
        
        delay_seconds = node.config.get("delay_seconds", 0)
        
        await asyncio.sleep(delay_seconds)
        
        return {"delayed": delay_seconds}
    
    def _get_next_nodes(
        self,
        workflow: VisualWorkflow,
        current_node: WorkflowNode,
        state: Dict[str, Any]
    ) -> List[WorkflowNode]:
        """Get next nodes to execute"""
        
        next_nodes = []
        
        for connection in workflow.connections:
            if connection.from_node == current_node.id:
                # Check condition if present
                if connection.condition:
                    # TODO: Implement safe condition evaluation
                    if not eval(connection.condition, {"state": state}):
                        continue
                
                # Find node
                next_node = next(
                    (n for n in workflow.nodes if n.id == connection.to_node),
                    None
                )
                
                if next_node:
                    next_nodes.append(next_node)
        
        return next_nodes
    
    def _find_error_handler(
        self,
        workflow: VisualWorkflow,
        node: WorkflowNode
    ) -> Optional[WorkflowNode]:
        """Find error handler for node"""
        
        # Look for error handler connection
        for connection in workflow.connections:
            if connection.from_node == node.id and connection.label == "error":
                return next(
                    (n for n in workflow.nodes if n.id == connection.to_node),
                    None
                )
        
        return None
    
    def _map_inputs(
        self,
        mapping: Dict[str, str],
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Map inputs from state"""
        
        result = {}
        for key, path in mapping.items():
            result[key] = self._get_value_from_path(state, path)
        
        return result
    
    def _get_value_from_path(
        self,
        state: Dict[str, Any],
        path: str
    ) -> Any:
        """Get value from nested path"""
        
        value = state
        for part in path.split('.'):
            value = value.get(part, {})
        
        return value
    
    # ========================================================================
    # WORKFLOW MANAGEMENT
    # ========================================================================
    
    def save_workflow(self, workflow: VisualWorkflow) -> str:
        """Save workflow to JSON"""
        
        workflow_dict = {
            'id': workflow.id,
            'name': workflow.name,
            'description': workflow.description,
            'nodes': [
                {
                    'id': n.id,
                    'type': n.type.value,
                    'name': n.name,
                    'agent_name': n.agent_name,
                    'config': n.config,
                    'position': n.position
                }
                for n in workflow.nodes
            ],
            'connections': [
                {
                    'from_node': c.from_node,
                    'to_node': c.to_node,
                    'condition': c.condition,
                    'label': c.label
                }
                for c in workflow.connections
            ],
            'version': workflow.version
        }
        
        return json.dumps(workflow_dict, indent=2)
    
    def load_workflow(self, workflow_json: str) -> VisualWorkflow:
        """Load workflow from JSON"""
        
        data = json.loads(workflow_json)
        
        workflow = VisualWorkflow(
            id=data['id'],
            name=data['name'],
            description=data.get('description', ''),
            version=data.get('version', 1)
        )
        
        # Load nodes
        for node_data in data['nodes']:
            node = WorkflowNode(
                id=node_data['id'],
                type=NodeType(node_data['type']),
                name=node_data['name'],
                agent_name=node_data.get('agent_name'),
                config=node_data.get('config', {}),
                position=node_data.get('position', {})
            )
            workflow.nodes.append(node)
        
        # Load connections
        for conn_data in data['connections']:
            connection = Connection(
                from_node=conn_data['from_node'],
                to_node=conn_data['to_node'],
                condition=conn_data.get('condition'),
                label=conn_data.get('label')
            )
            workflow.connections.append(connection)
        
        self.workflows[workflow.id] = workflow
        
        return workflow
    
    def register_agent(self, agent_name: str, agent: Any):
        """Register an agent for use in workflows"""
        self.agents[agent_name] = agent
        logger.info(f"✅ Registered agent: {agent_name}")
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows"""
        
        return [
            {
                'id': w.id,
                'name': w.name,
                'description': w.description,
                'nodes': len(w.nodes),
                'connections': len(w.connections),
                'version': w.version,
                'updated_at': w.updated_at.isoformat()
            }
            for w in self.workflows.values()
        ]


# Global instance
_meta_orchestrator = MetaOrchestrator()


def get_meta_orchestrator() -> MetaOrchestrator:
    """Get global meta-orchestrator"""
    return _meta_orchestrator
