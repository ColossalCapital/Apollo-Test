"""
Node Configuration Panel

Panel for configuring node settings, input/output mappings, and conditions.
"""

import React, { useState } from 'react';
import { Node } from 'reactflow';

interface NodeConfigPanelProps {
  node: Node | null;
  onUpdate: (nodeId: string, config: any) => void;
  onClose: () => void;
}

export const NodeConfigPanel: React.FC<NodeConfigPanelProps> = ({ node, onUpdate, onClose }) => {
  const [config, setConfig] = useState(node?.data?.config || {});

  if (!node) return null;

  const handleSave = () => {
    onUpdate(node.id, config);
    onClose();
  };

  return (
    <div
      style={{
        position: 'fixed',
        right: 0,
        top: 0,
        bottom: 0,
        width: '400px',
        background: 'white',
        boxShadow: '-4px 0 12px rgba(0,0,0,0.1)',
        padding: '24px',
        overflowY: 'auto',
        zIndex: 1000,
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h2 style={{ fontSize: '20px', fontWeight: 'bold' }}>Configure Node</h2>
        <button
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            fontSize: '24px',
            cursor: 'pointer',
            color: '#6b7280',
          }}
        >
          ✕
        </button>
      </div>

      {/* Node Info */}
      <div style={{ marginBottom: '24px', padding: '12px', background: '#f9fafb', borderRadius: '8px' }}>
        <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '4px' }}>Node Type</div>
        <div style={{ fontSize: '16px', fontWeight: '600' }}>{node.data.type}</div>
        <div style={{ fontSize: '14px', color: '#6b7280', marginTop: '8px', marginBottom: '4px' }}>Node Name</div>
        <div style={{ fontSize: '16px', fontWeight: '600' }}>{node.data.label}</div>
      </div>

      {/* Agent-specific config */}
      {node.data.type === 'agent' && (
        <>
          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', marginBottom: '8px' }}>
              Agent Name
            </label>
            <input
              type="text"
              value={node.data.agentName || ''}
              disabled
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
                background: '#f9fafb',
              }}
            />
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', marginBottom: '8px' }}>
              Input Mapping
            </label>
            <textarea
              value={JSON.stringify(config.input_mapping || {}, null, 2)}
              onChange={(e) => {
                try {
                  const parsed = JSON.parse(e.target.value);
                  setConfig({ ...config, input_mapping: parsed });
                } catch (err) {
                  // Invalid JSON, ignore
                }
              }}
              placeholder='{"email": "trigger.email"}'
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
                fontFamily: 'monospace',
                fontSize: '12px',
                minHeight: '100px',
              }}
            />
            <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
              Map inputs from previous steps
            </div>
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', marginBottom: '8px' }}>
              Output Mapping
            </label>
            <textarea
              value={JSON.stringify(config.output_mapping || {}, null, 2)}
              onChange={(e) => {
                try {
                  const parsed = JSON.parse(e.target.value);
                  setConfig({ ...config, output_mapping: parsed });
                } catch (err) {
                  // Invalid JSON, ignore
                }
              }}
              placeholder='{"parsed": "email_data"}'
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
                fontFamily: 'monospace',
                fontSize: '12px',
                minHeight: '100px',
              }}
            />
            <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
              Map outputs to workflow state
            </div>
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', marginBottom: '8px' }}>
              Timeout (seconds)
            </label>
            <input
              type="number"
              value={config.timeout_seconds || 30}
              onChange={(e) => setConfig({ ...config, timeout_seconds: parseInt(e.target.value) })}
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
              }}
            />
          </div>
        </>
      )}

      {/* Condition-specific config */}
      {node.data.type === 'condition' && (
        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', marginBottom: '8px' }}>
            Condition Expression
          </label>
          <textarea
            value={config.condition || ''}
            onChange={(e) => setConfig({ ...config, condition: e.target.value })}
            placeholder="state['availability'] == true"
            style={{
              width: '100%',
              padding: '8px 12px',
              border: '1px solid #e5e7eb',
              borderRadius: '6px',
              fontFamily: 'monospace',
              fontSize: '12px',
              minHeight: '80px',
            }}
          />
          <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>
            Python expression to evaluate
          </div>
        </div>
      )}

      {/* Loop-specific config */}
      {node.data.type === 'loop' && (
        <>
          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', marginBottom: '8px' }}>
              Items Path
            </label>
            <input
              type="text"
              value={config.items || ''}
              onChange={(e) => setConfig({ ...config, items: e.target.value })}
              placeholder="nodes.node_1.items"
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
              }}
            />
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', marginBottom: '8px' }}>
              Loop Condition
            </label>
            <input
              type="text"
              value={config.loop_condition || ''}
              onChange={(e) => setConfig({ ...config, loop_condition: e.target.value })}
              placeholder="state['loop_index'] < len(state['items'])"
              style={{
                width: '100%',
                padding: '8px 12px',
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
                fontFamily: 'monospace',
                fontSize: '12px',
              }}
            />
          </div>
        </>
      )}

      {/* Delay-specific config */}
      {node.data.type === 'delay' && (
        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', marginBottom: '8px' }}>
            Delay (seconds)
          </label>
          <input
            type="number"
            value={config.delay_seconds || 0}
            onChange={(e) => setConfig({ ...config, delay_seconds: parseInt(e.target.value) })}
            style={{
              width: '100%',
              padding: '8px 12px',
              border: '1px solid #e5e7eb',
              borderRadius: '6px',
            }}
          />
        </div>
      )}

      {/* Transform-specific config */}
      {node.data.type === 'transform' && (
        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', marginBottom: '8px' }}>
            Transform Mapping
          </label>
          <textarea
            value={JSON.stringify(config.transform || {}, null, 2)}
            onChange={(e) => {
              try {
                const parsed = JSON.parse(e.target.value);
                setConfig({ ...config, transform: parsed });
              } catch (err) {
                // Invalid JSON, ignore
              }
            }}
            placeholder='{"output_key": "input_path"}'
            style={{
              width: '100%',
              padding: '8px 12px',
              border: '1px solid #e5e7eb',
              borderRadius: '6px',
              fontFamily: 'monospace',
              fontSize: '12px',
              minHeight: '100px',
            }}
          />
        </div>
      )}

      {/* Save Button */}
      <div style={{ display: 'flex', gap: '8px' }}>
        <button
          onClick={handleSave}
          style={{
            flex: 1,
            padding: '12px',
            background: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            fontWeight: '600',
            cursor: 'pointer',
          }}
        >
          Save Configuration
        </button>
        <button
          onClick={onClose}
          style={{
            padding: '12px 20px',
            background: '#f3f4f6',
            color: '#374151',
            border: 'none',
            borderRadius: '6px',
            fontWeight: '600',
            cursor: 'pointer',
          }}
        >
          Cancel
        </button>
      </div>

      {/* Examples */}
      <div style={{ marginTop: '32px', padding: '16px', background: '#f0f9ff', borderRadius: '8px' }}>
        <div style={{ fontSize: '14px', fontWeight: '600', marginBottom: '8px', color: '#1e40af' }}>
          💡 Examples
        </div>
        <div style={{ fontSize: '12px', color: '#1e40af', lineHeight: '1.6' }}>
          <strong>Input Mapping:</strong>
          <pre style={{ background: 'white', padding: '8px', borderRadius: '4px', marginTop: '4px' }}>
            {`{
  "email": "trigger.email",
  "user_id": "user_id"
}`}
          </pre>
          <strong style={{ marginTop: '8px', display: 'block' }}>Output Mapping:</strong>
          <pre style={{ background: 'white', padding: '8px', borderRadius: '4px', marginTop: '4px' }}>
            {`{
  "parsed": "email_data",
  "from": "sender"
}`}
          </pre>
        </div>
      </div>
    </div>
  );
};

export default NodeConfigPanel;
