"""
Visual Workflow Builder UI for Apollo

React component using React Flow for drag-and-drop workflow construction.
"""

import React, { useState, useCallback, useEffect } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';

// ============================================================================
// NODE TYPES
// ============================================================================

const nodeTypes = [
  { type: 'trigger', label: 'Trigger', icon: '⚡', color: '#10b981' },
  { type: 'agent', label: 'AI Agent', icon: '🤖', color: '#3b82f6' },
  { type: 'condition', label: 'Condition', icon: '🔀', color: '#f59e0b' },
  { type: 'loop', label: 'Loop', icon: '🔁', color: '#8b5cf6' },
  { type: 'parallel', label: 'Parallel', icon: '⚡', color: '#ec4899' },
  { type: 'merge', label: 'Merge', icon: '🔗', color: '#06b6d4' },
  { type: 'transform', label: 'Transform', icon: '🔄', color: '#14b8a6' },
  { type: 'delay', label: 'Delay', icon: '⏱️', color: '#6366f1' },
  { type: 'webhook', label: 'Webhook', icon: '🌐', color: '#84cc16' },
  { type: 'error', label: 'Error Handler', icon: '❌', color: '#ef4444' },
];

// ============================================================================
// AVAILABLE AGENTS (133 Apollo Agents)
// ============================================================================

const availableAgents = [
  // Finance
  { name: 'TradingAgent', category: 'Finance', description: 'Execute trades' },
  { name: 'PortfolioAgent', category: 'Finance', description: 'Manage portfolio' },
  { name: 'ArbitrageAgent', category: 'Finance', description: 'Find arbitrage opportunities' },
  { name: 'SentimentAgent', category: 'Finance', description: 'Analyze market sentiment' },
  
  // Business
  { name: 'CRMAgent', category: 'Business', description: 'Manage customer relationships' },
  { name: 'SalesAgent', category: 'Business', description: 'Track sales pipeline' },
  { name: 'ProjectAgent', category: 'Business', description: 'Manage projects' },
  { name: 'HRAgent', category: 'Business', description: 'HR operations' },
  
  // Communication
  { name: 'EmailParserAgent', category: 'Communication', description: 'Parse emails' },
  { name: 'EmailAgent', category: 'Communication', description: 'Send emails' },
  { name: 'CalendarAgent', category: 'Communication', description: 'Manage calendar' },
  { name: 'SlackAgent', category: 'Communication', description: 'Slack integration' },
  
  // Documents
  { name: 'DocumentParserAgent', category: 'Documents', description: 'Parse documents' },
  { name: 'OCRAgent', category: 'Documents', description: 'Extract text from images' },
  { name: 'PDFAgent', category: 'Documents', description: 'Process PDFs' },
  { name: 'TranslationAgent', category: 'Documents', description: 'Translate text' },
  
  // Analytics
  { name: 'DataAnalysisAgent', category: 'Analytics', description: 'Analyze data' },
  { name: 'ForecastAgent', category: 'Analytics', description: 'Forecast trends' },
  { name: 'MetricsAgent', category: 'Analytics', description: 'Track metrics' },
  { name: 'ReportAgent', category: 'Analytics', description: 'Generate reports' },
  
  // More agents...
];

// ============================================================================
// CUSTOM NODE COMPONENTS
// ============================================================================

const AgentNode = ({ data }: { data: any }) => {
  return (
    <div
      style={{
        padding: '12px 16px',
        borderRadius: '8px',
        border: '2px solid #3b82f6',
        background: 'white',
        minWidth: '180px',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
        <span style={{ fontSize: '20px' }}>🤖</span>
        <strong style={{ fontSize: '14px' }}>{data.label}</strong>
      </div>
      {data.agentName && (
        <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>
          {data.agentName}
        </div>
      )}
      {data.status && (
        <div
          style={{
            fontSize: '11px',
            padding: '2px 6px',
            borderRadius: '4px',
            background: data.status === 'completed' ? '#10b981' : '#f59e0b',
            color: 'white',
            display: 'inline-block',
          }}
        >
          {data.status}
        </div>
      )}
    </div>
  );
};

const TriggerNode = ({ data }: { data: any }) => {
  return (
    <div
      style={{
        padding: '12px 16px',
        borderRadius: '8px',
        border: '2px solid #10b981',
        background: 'white',
        minWidth: '150px',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{ fontSize: '20px' }}>⚡</span>
        <strong style={{ fontSize: '14px' }}>{data.label}</strong>
      </div>
      {data.triggerType && (
        <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
          {data.triggerType}
        </div>
      )}
    </div>
  );
};

const ConditionNode = ({ data }: { data: any }) => {
  return (
    <div
      style={{
        padding: '12px 16px',
        borderRadius: '8px',
        border: '2px solid #f59e0b',
        background: 'white',
        minWidth: '150px',
        boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{ fontSize: '20px' }}>🔀</span>
        <strong style={{ fontSize: '14px' }}>{data.label}</strong>
      </div>
      {data.condition && (
        <div style={{ fontSize: '11px', color: '#6b7280', marginTop: '4px' }}>
          {data.condition}
        </div>
      )}
    </div>
  );
};

const customNodeTypes = {
  agent: AgentNode,
  trigger: TriggerNode,
  condition: ConditionNode,
};

// ============================================================================
// MAIN WORKFLOW BUILDER COMPONENT
// ============================================================================

export const WorkflowBuilder = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNodeType, setSelectedNodeType] = useState<string | null>(null);
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [workflowName, setWorkflowName] = useState('New Workflow');
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionResults, setExecutionResults] = useState<any>(null);
  const [showAgentSelector, setShowAgentSelector] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // ========================================================================
  // DRAG AND DROP
  // ========================================================================

  const onDragStart = (event: React.DragEvent, nodeType: string) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      const type = event.dataTransfer.getData('application/reactflow');
      const position = {
        x: event.clientX - 250,
        y: event.clientY - 100,
      };

      const newNode: Node = {
        id: `node_${nodes.length}`,
        type: type === 'agent' ? 'agent' : type === 'trigger' ? 'trigger' : type === 'condition' ? 'condition' : 'default',
        position,
        data: {
          label: type.charAt(0).toUpperCase() + type.slice(1),
          type: type,
        },
      };

      if (type === 'agent') {
        setSelectedNodeType(newNode.id);
        setShowAgentSelector(true);
      } else {
        setNodes((nds) => nds.concat(newNode));
      }
    },
    [nodes, setNodes]
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  // ========================================================================
  // CONNECTIONS
  // ========================================================================

  const onConnect = useCallback(
    (params: Connection) => {
      const edge = {
        ...params,
        animated: true,
        style: { stroke: '#3b82f6', strokeWidth: 2 },
      };
      setEdges((eds) => addEdge(edge, eds));
    },
    [setEdges]
  );

  // ========================================================================
  // AGENT SELECTION
  // ========================================================================

  const handleAgentSelect = (agentName: string) => {
    if (selectedNodeType) {
      setNodes((nds) =>
        nds.map((node) =>
          node.id === selectedNodeType
            ? {
                ...node,
                data: {
                  ...node.data,
                  label: agentName,
                  agentName: agentName,
                },
              }
            : node
        )
      );
      setShowAgentSelector(false);
      setSelectedNodeType(null);
    }
  };

  // ========================================================================
  // WORKFLOW EXECUTION
  // ========================================================================

  const executeWorkflow = async () => {
    setIsExecuting(true);
    setExecutionResults(null);

    try {
      // Convert React Flow nodes/edges to workflow format
      const workflow = {
        name: workflowName,
        nodes: nodes.map((node) => ({
          id: node.id,
          type: node.data.type,
          name: node.data.label,
          agent_name: node.data.agentName,
          config: node.data.config || {},
          position: node.position,
        })),
        connections: edges.map((edge) => ({
          from_node: edge.source,
          to_node: edge.target,
          condition: edge.data?.condition,
          label: edge.label,
        })),
      };

      // Create workflow
      const createResponse = await fetch('/orchestrator/workflows/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: workflowName,
          description: 'Created from visual builder',
        }),
      });

      const { id: workflowId } = await createResponse.json();

      // Add nodes
      for (const node of workflow.nodes) {
        await fetch(`/orchestrator/workflows/${workflowId}/nodes`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            workflow_id: workflowId,
            node_type: node.type,
            name: node.name,
            agent_name: node.agent_name,
            config: node.config,
            position: node.position,
          }),
        });
      }

      // Add connections
      for (const conn of workflow.connections) {
        await fetch(`/orchestrator/workflows/${workflowId}/connections`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            workflow_id: workflowId,
            from_node_id: conn.from_node,
            to_node_id: conn.to_node,
            condition: conn.condition,
            label: conn.label,
          }),
        });
      }

      // Execute workflow
      const executeResponse = await fetch(`/orchestrator/workflows/${workflowId}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workflow_id: workflowId,
          trigger_data: {},
          user_id: 'user_123',
        }),
      });

      const results = await executeResponse.json();
      setExecutionResults(results);

      // Update node statuses
      if (results.success) {
        setNodes((nds) =>
          nds.map((node) => ({
            ...node,
            data: {
              ...node.data,
              status: results.execution_path.includes(node.id) ? 'completed' : 'pending',
            },
          }))
        );
      }
    } catch (error) {
      console.error('Workflow execution failed:', error);
      setExecutionResults({ success: false, error: error.message });
    } finally {
      setIsExecuting(false);
    }
  };

  // ========================================================================
  // SAVE/LOAD WORKFLOW
  // ========================================================================

  const saveWorkflow = async () => {
    const workflow = {
      name: workflowName,
      nodes: nodes,
      edges: edges,
    };

    const blob = new Blob([JSON.stringify(workflow, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${workflowName.replace(/\s+/g, '_')}.json`;
    a.click();
  };

  const loadWorkflow = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const workflow = JSON.parse(e.target?.result as string);
        setWorkflowName(workflow.name);
        setNodes(workflow.nodes);
        setEdges(workflow.edges);
      };
      reader.readAsText(file);
    }
  };

  // ========================================================================
  // RENDER
  // ========================================================================

  const filteredAgents = availableAgents.filter(
    (agent) =>
      agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div style={{ width: '100vw', height: '100vh', display: 'flex' }}>
      {/* LEFT SIDEBAR - Node Palette */}
      <div
        style={{
          width: '250px',
          background: '#f9fafb',
          borderRight: '1px solid #e5e7eb',
          padding: '20px',
          overflowY: 'auto',
        }}
      >
        <h2 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '16px' }}>
          Node Palette
        </h2>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {nodeTypes.map((nodeType) => (
            <div
              key={nodeType.type}
              draggable
              onDragStart={(e) => onDragStart(e, nodeType.type)}
              style={{
                padding: '12px',
                background: 'white',
                border: `2px solid ${nodeType.color}`,
                borderRadius: '8px',
                cursor: 'grab',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              <span style={{ fontSize: '20px' }}>{nodeType.icon}</span>
              <span style={{ fontSize: '14px', fontWeight: '500' }}>{nodeType.label}</span>
            </div>
          ))}
        </div>

        <div style={{ marginTop: '24px' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 'bold', marginBottom: '12px' }}>
            Quick Actions
          </h3>
          <button
            onClick={executeWorkflow}
            disabled={isExecuting || nodes.length === 0}
            style={{
              width: '100%',
              padding: '10px',
              background: isExecuting ? '#9ca3af' : '#10b981',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: isExecuting ? 'not-allowed' : 'pointer',
              fontWeight: '600',
              marginBottom: '8px',
            }}
          >
            {isExecuting ? '⏳ Executing...' : '▶️ Execute Workflow'}
          </button>
          <button
            onClick={saveWorkflow}
            disabled={nodes.length === 0}
            style={{
              width: '100%',
              padding: '10px',
              background: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: '600',
              marginBottom: '8px',
            }}
          >
            💾 Save Workflow
          </button>
          <label
            style={{
              width: '100%',
              padding: '10px',
              background: '#8b5cf6',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: '600',
              display: 'block',
              textAlign: 'center',
            }}
          >
            📂 Load Workflow
            <input type="file" accept=".json" onChange={loadWorkflow} style={{ display: 'none' }} />
          </label>
        </div>
      </div>

      {/* CENTER - React Flow Canvas */}
      <div style={{ flex: 1, position: 'relative' }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onDrop={onDrop}
          onDragOver={onDragOver}
          nodeTypes={customNodeTypes}
          fitView
        >
          <Background />
          <Controls />
          <MiniMap />
          <Panel position="top-left">
            <div style={{ background: 'white', padding: '12px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
              <input
                type="text"
                value={workflowName}
                onChange={(e) => setWorkflowName(e.target.value)}
                style={{
                  fontSize: '18px',
                  fontWeight: 'bold',
                  border: 'none',
                  outline: 'none',
                  width: '300px',
                }}
                placeholder="Workflow Name"
              />
            </div>
          </Panel>
        </ReactFlow>

        {/* Execution Results Overlay */}
        {executionResults && (
          <div
            style={{
              position: 'absolute',
              bottom: '20px',
              right: '20px',
              background: 'white',
              padding: '16px',
              borderRadius: '8px',
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
              maxWidth: '400px',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 'bold' }}>
                {executionResults.success ? '✅ Success' : '❌ Failed'}
              </h3>
              <button
                onClick={() => setExecutionResults(null)}
                style={{ background: 'none', border: 'none', fontSize: '18px', cursor: 'pointer' }}
              >
                ✕
              </button>
            </div>
            <div style={{ fontSize: '14px', color: '#6b7280' }}>
              <div>Duration: {executionResults.duration_seconds?.toFixed(2)}s</div>
              <div>Nodes executed: {executionResults.execution_path?.length || 0}</div>
              {executionResults.error && (
                <div style={{ color: '#ef4444', marginTop: '8px' }}>Error: {executionResults.error}</div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* RIGHT SIDEBAR - Agent Selector */}
      {showAgentSelector && (
        <div
          style={{
            width: '300px',
            background: 'white',
            borderLeft: '1px solid #e5e7eb',
            padding: '20px',
            overflowY: 'auto',
          }}
        >
          <h2 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '16px' }}>
            Select Agent
          </h2>

          <input
            type="text"
            placeholder="Search agents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '8px 12px',
              border: '1px solid #e5e7eb',
              borderRadius: '6px',
              marginBottom: '16px',
            }}
          />

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {filteredAgents.map((agent) => (
              <div
                key={agent.name}
                onClick={() => handleAgentSelect(agent.name)}
                style={{
                  padding: '12px',
                  background: '#f9fafb',
                  border: '1px solid #e5e7eb',
                  borderRadius: '6px',
                  cursor: 'pointer',
                }}
              >
                <div style={{ fontWeight: '600', fontSize: '14px', marginBottom: '4px' }}>
                  {agent.name}
                </div>
                <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px' }}>
                  {agent.category}
                </div>
                <div style={{ fontSize: '11px', color: '#9ca3af' }}>{agent.description}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkflowBuilder;
