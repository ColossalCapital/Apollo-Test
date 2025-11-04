"""
Business Entity Setup Workflow Template

Automatically create compliance roadmap for new business entities.

Workflow:
1. DocumentParserAgent - Parse formation documents
2. ComplianceAgent - Identify obligations
3. TaxAgent - Calculate tax requirements
4. CalendarAgent - Schedule deadlines
5. TaskAgent - Create action items
6. DocumentAgent - Prepare templates
"""

from workflows.workflow_engine import Workflow, WorkflowStep


def create_entity_setup_workflow() -> Workflow:
    """
    Create business entity setup workflow
    
    Trigger: New entity connected with formation documents
    
    Example:
        Entity: AckwardRoots Inc
        Type: S-Corp
        State: Delaware
        Formed: 2024-01-15
    
    Result:
        - Compliance roadmap created
        - Tax deadlines scheduled
        - Tasks created
        - Templates prepared
    """
    
    return Workflow(
        id="entity_setup",
        name="Business Entity Setup & Compliance",
        description="Create compliance roadmap for new business entities",
        
        trigger={
            "type": "entity_connected",
            "entity_type": "business"
        },
        
        steps=[
            # Step 1: Parse formation documents
            WorkflowStep(
                agent_name="DocumentParserAgent",
                input_mapping={
                    "documents": "trigger.formation_documents",
                    "entity_id": "trigger.entity_id"
                },
                output_mapping={
                    "entity_type": "entity_type",
                    "state": "state",
                    "formed_date": "formed_date",
                    "members": "members",
                    "fiscal_year": "fiscal_year"
                }
            ),
            
            # Step 2: Identify compliance requirements
            WorkflowStep(
                agent_name="ComplianceAgent",
                input_mapping={
                    "entity_type": "entity_type",
                    "state": "state",
                    "formed_date": "formed_date"
                },
                output_mapping={
                    "federal_requirements": "federal_reqs",
                    "state_requirements": "state_reqs",
                    "corporate_requirements": "corporate_reqs"
                }
            ),
            
            # Step 3: Calculate tax obligations
            WorkflowStep(
                agent_name="TaxAgent",
                input_mapping={
                    "entity_type": "entity_type",
                    "state": "state",
                    "fiscal_year": "fiscal_year"
                },
                output_mapping={
                    "tax_deadlines": "tax_deadlines",
                    "estimated_amounts": "tax_estimates"
                }
            ),
            
            # Step 4: Schedule all deadlines
            WorkflowStep(
                agent_name="CalendarAgent",
                input_mapping={
                    "user_id": "user_id",
                    "entity_id": "trigger.entity_id",
                    "federal_reqs": "federal_reqs",
                    "state_reqs": "state_reqs",
                    "corporate_reqs": "corporate_reqs",
                    "tax_deadlines": "tax_deadlines"
                },
                output_mapping={
                    "calendar_events": "scheduled_deadlines",
                    "event_count": "deadline_count"
                }
            ),
            
            # Step 5: Create action items
            WorkflowStep(
                agent_name="TaskAgent",
                input_mapping={
                    "user_id": "user_id",
                    "entity_id": "trigger.entity_id",
                    "deadlines": "scheduled_deadlines",
                    "requirements": "federal_reqs"
                },
                output_mapping={
                    "tasks": "created_tasks",
                    "task_count": "task_count"
                }
            ),
            
            # Step 6: Prepare document templates
            WorkflowStep(
                agent_name="DocumentAgent",
                input_mapping={
                    "entity_type": "entity_type",
                    "state": "state",
                    "entity_id": "trigger.entity_id"
                },
                output_mapping={
                    "templates": "document_templates"
                }
            ),
            
            # Step 7: Detect missing items
            WorkflowStep(
                agent_name="ComplianceAgent",
                input_mapping={
                    "entity_id": "trigger.entity_id",
                    "entity_type": "entity_type",
                    "connected_services": "trigger.connected_services"
                },
                output_mapping={
                    "missing_items": "missing_items",
                    "recommendations": "recommendations"
                }
            )
        ],
        
        variables={
            "prep_time_weeks": 2  # weeks before deadline
        },
        
        max_retries=3,
        enable_rollback=True
    )
