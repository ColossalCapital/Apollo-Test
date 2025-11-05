"""
Contact Update Workflow Template

Automatically propagate contact changes across all systems.

Workflow:
1. EntityExtractorAgent - Extract contact change
2. EntityUpdateAgent - Update in knowledge graph
3. PropagationAgent - Find all systems with contact
4. UpdateAgent - Update each system
5. NotificationAgent - Confirm changes
"""

from workflows.workflow_engine import Workflow, WorkflowStep


def create_contact_update_workflow() -> Workflow:
    """
    Create contact update workflow
    
    Trigger: Email or message with contact change
    
    Example email:
        "Hey, my new number is 555-0123"
    
    Result:
        - Contact updated in knowledge graph
        - Updated in QuickBooks
        - Updated in CRM
        - Updated in phone contacts
        - Updated in calendar events
        - Confirmation sent
    """
    
    return Workflow(
        id="contact_update",
        name="Propagate Contact Changes",
        description="Automatically update contacts across all systems",
        
        trigger={
            "type": "email",
            "intent": "contact_change"
        },
        
        steps=[
            # Step 1: Extract contact change
            WorkflowStep(
                agent_name="EntityExtractorAgent",
                input_mapping={
                    "email": "trigger.email"
                },
                output_mapping={
                    "person_id": "person_id",
                    "person_name": "person_name",
                    "change_type": "change_type",  # phone, email, address
                    "old_value": "old_value",
                    "new_value": "new_value",
                    "confidence": "confidence"
                }
            ),
            
            # Step 2: Verify change (if confidence < 0.9)
            WorkflowStep(
                agent_name="VerificationAgent",
                input_mapping={
                    "person_id": "person_id",
                    "change_type": "change_type",
                    "new_value": "new_value",
                    "confidence": "confidence"
                },
                output_mapping={
                    "verified": "verified"
                },
                condition=lambda state: state.get("confidence", 1.0) < 0.9
            ),
            
            # Step 3: Update knowledge graph
            WorkflowStep(
                agent_name="EntityUpdateAgent",
                input_mapping={
                    "entity_id": "person_id",
                    "entity_type": "person",
                    "field": "change_type",
                    "old_value": "old_value",
                    "new_value": "new_value"
                },
                output_mapping={
                    "updated": "graph_updated",
                    "history_id": "change_history_id"
                }
            ),
            
            # Step 4: Find all systems with this contact
            WorkflowStep(
                agent_name="PropagationAgent",
                input_mapping={
                    "person_id": "person_id",
                    "user_id": "user_id"
                },
                output_mapping={
                    "systems": "systems_to_update"
                }
            ),
            
            # Step 5: Update each system
            WorkflowStep(
                agent_name="SystemUpdateAgent",
                input_mapping={
                    "systems": "systems_to_update",
                    "person_id": "person_id",
                    "change_type": "change_type",
                    "new_value": "new_value"
                },
                output_mapping={
                    "updated_systems": "updated_systems",
                    "failed_systems": "failed_systems"
                }
            ),
            
            # Step 6: Send confirmation
            WorkflowStep(
                agent_name="NotificationAgent",
                input_mapping={
                    "user_id": "user_id",
                    "person_name": "person_name",
                    "change_type": "change_type",
                    "new_value": "new_value",
                    "updated_systems": "updated_systems",
                    "failed_systems": "failed_systems"
                },
                output_mapping={
                    "notification_sent": "notification_sent"
                }
            )
        ],
        
        variables={
            "verification_threshold": 0.9
        },
        
        max_retries=3,
        enable_rollback=True
    )
