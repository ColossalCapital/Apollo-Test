"""
Workflow Templates Gallery

Pre-built workflow templates that users can load and customize.
"""

import React from 'react';

interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  icon: string;
  nodes: number;
  preview: string;
}

const templates: WorkflowTemplate[] = [
  {
    id: 'meeting_scheduling',
    name: 'Meeting Scheduling',
    description: 'Automatically schedule meetings from email requests',
    category: 'Communication',
    icon: '📅',
    nodes: 7,
    preview: 'Email → Parse → Calendar → Schedule → Send → Tasks',
  },
  {
    id: 'invoice_processing',
    name: 'Invoice Processing',
    description: 'Parse invoices and record in QuickBooks',
    category: 'Finance',
    icon: '💰',
    nodes: 5,
    preview: 'Invoice → Parse → Validate → Record → Notify',
  },
  {
    id: 'contact_update',
    name: 'Contact Update',
    description: 'Propagate contact changes across all systems',
    category: 'Business',
    icon: '📱',
    nodes: 6,
    preview: 'Change → Update → Find Systems → Update All → Notify',
  },
  {
    id: 'document_processing',
    name: 'Document Processing',
    description: 'Extract text, images, and metadata from documents',
    category: 'Documents',
    icon: '📄',
    nodes: 6,
    preview: 'Upload → Parse → [Text|Images|Metadata] → Merge → Store',
  },
  {
    id: 'entity_setup',
    name: 'Business Entity Setup',
    description: 'Create compliance roadmap for new entities',
    category: 'Business',
    icon: '🏢',
    nodes: 7,
    preview: 'Entity → Parse → Compliance → Tax → Schedule → Tasks',
  },
  {
    id: 'email_automation',
    name: 'Email Automation',
    description: 'Auto-respond to common email patterns',
    category: 'Communication',
    icon: '📧',
    nodes: 5,
    preview: 'Email → Classify → [Support|Sales|Info] → Respond',
  },
  {
    id: 'data_pipeline',
    name: 'Data Pipeline',
    description: 'ETL pipeline for data processing',
    category: 'Analytics',
    icon: '📊',
    nodes: 8,
    preview: 'Extract → Transform → Validate → Load → Index → Report',
  },
  {
    id: 'trading_strategy',
    name: 'Trading Strategy',
    description: 'Automated trading with risk management',
    category: 'Finance',
    icon: '📈',
    nodes: 9,
    preview: 'Signal → Validate → Risk Check → Execute → Monitor',
  },
  {
    id: 'content_generation',
    name: 'Content Generation',
    description: 'Generate and publish content automatically',
    category: 'Marketing',
    icon: '✍️',
    nodes: 6,
    preview: 'Topic → Research → Generate → Review → Publish → Share',
  },
  {
    id: 'customer_onboarding',
    name: 'Customer Onboarding',
    description: 'Automated customer onboarding workflow',
    category: 'Business',
    icon: '👋',
    nodes: 8,
    preview: 'Signup → Verify → Setup → Welcome → Train → Follow-up',
  },
];

interface WorkflowTemplatesProps {
  onLoadTemplate: (templateId: string) => void;
  onClose: () => void;
}

export const WorkflowTemplates: React.FC<WorkflowTemplatesProps> = ({ onLoadTemplate, onClose }) => {
  const [selectedCategory, setSelectedCategory] = React.useState<string>('All');

  const categories = ['All', ...Array.from(new Set(templates.map((t) => t.category)))];

  const filteredTemplates =
    selectedCategory === 'All'
      ? templates
      : templates.filter((t) => t.category === selectedCategory);

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0,0,0,0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 2000,
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: 'white',
          borderRadius: '12px',
          padding: '32px',
          maxWidth: '1200px',
          maxHeight: '80vh',
          overflowY: 'auto',
          width: '90%',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
          <div>
            <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '8px' }}>
              Workflow Templates
            </h2>
            <p style={{ fontSize: '14px', color: '#6b7280' }}>
              Choose a template to get started quickly
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              fontSize: '28px',
              cursor: 'pointer',
              color: '#6b7280',
            }}
          >
            ✕
          </button>
        </div>

        {/* Category Filter */}
        <div style={{ display: 'flex', gap: '8px', marginBottom: '24px', flexWrap: 'wrap' }}>
          {categories.map((category) => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              style={{
                padding: '8px 16px',
                background: selectedCategory === category ? '#3b82f6' : '#f3f4f6',
                color: selectedCategory === category ? 'white' : '#374151',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: '500',
                fontSize: '14px',
              }}
            >
              {category}
            </button>
          ))}
        </div>

        {/* Templates Grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
            gap: '20px',
          }}
        >
          {filteredTemplates.map((template) => (
            <div
              key={template.id}
              style={{
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                padding: '20px',
                cursor: 'pointer',
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
                e.currentTarget.style.borderColor = '#3b82f6';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.boxShadow = 'none';
                e.currentTarget.style.borderColor = '#e5e7eb';
              }}
              onClick={() => {
                onLoadTemplate(template.id);
                onClose();
              }}
            >
              {/* Icon and Category */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '12px' }}>
                <span style={{ fontSize: '32px' }}>{template.icon}</span>
                <span
                  style={{
                    fontSize: '11px',
                    padding: '4px 8px',
                    background: '#f3f4f6',
                    borderRadius: '4px',
                    color: '#6b7280',
                    fontWeight: '500',
                  }}
                >
                  {template.category}
                </span>
              </div>

              {/* Name and Description */}
              <h3 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '8px' }}>
                {template.name}
              </h3>
              <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '12px', lineHeight: '1.5' }}>
                {template.description}
              </p>

              {/* Preview */}
              <div
                style={{
                  fontSize: '12px',
                  color: '#9ca3af',
                  background: '#f9fafb',
                  padding: '8px',
                  borderRadius: '4px',
                  marginBottom: '12px',
                  fontFamily: 'monospace',
                }}
              >
                {template.preview}
              </div>

              {/* Stats */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '13px', color: '#6b7280' }}>
                  {template.nodes} nodes
                </span>
                <button
                  style={{
                    padding: '6px 12px',
                    background: '#3b82f6',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    fontSize: '13px',
                    fontWeight: '500',
                    cursor: 'pointer',
                  }}
                >
                  Use Template
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {filteredTemplates.length === 0 && (
          <div style={{ textAlign: 'center', padding: '60px 20px', color: '#9ca3af' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔍</div>
            <div style={{ fontSize: '16px' }}>No templates found in this category</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WorkflowTemplates;
