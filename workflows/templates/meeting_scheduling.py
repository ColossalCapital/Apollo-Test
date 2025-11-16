"""
Meeting Scheduling Workflow Template

Automatically schedule meetings from email requests.

Workflow:
1. EmailParserAgent - Parse email for meeting request
2. CalendarAgent - Check availability
3. SchedulingAgent - Find best time
4. EmailAgent - Send confirmation
5. MeetingPrepAgent - Gather context
6. TaskAgent - Create prep tasks
"""

from workflows.workflow_engine import Workflow, WorkflowStep


def create_meeting_scheduling_workflow() -> Workflow:
    """
    Create meeting scheduling workflow
    
    Trigger: Email with intent=schedule_meeting
    
    Example email:
        "Can we meet next week to discuss Q4? 
         I'm free Tuesday or Thursday afternoon."
    
    Result:
        - Meeting scheduled
        - Email confirmation sent
        - Prep document created
        - Tasks created
    """
    
    return Workflow(
        id="meeting_scheduling",
        name="Schedule Meeting from Email",
        description="Automatically schedule meetings from email requests",
        
        trigger={
            "type": "email",
            "intent": "schedule_meeting"
        },
        
        steps=[
            # Step 1: Parse email
            WorkflowStep(
                agent_name="EmailParserAgent",
                input_mapping={
                    "email": "trigger.email"
                },
                output_mapping={
                    "from": "email_from",
                    "subject": "email_subject",
                    "proposed_times": "proposed_times",
                    "topic": "meeting_topic",
                    "attendees": "attendees"
                }
            ),
            
            # Step 2: Check my availability
            WorkflowStep(
                agent_name="CalendarAgent",
                input_mapping={
                    "user_id": "user_id",
                    "date_range": "proposed_times"
                },
                output_mapping={
                    "availability": "my_availability",
                    "conflicts": "calendar_conflicts"
                }
            ),
            
            # Step 3: Find best time
            WorkflowStep(
                agent_name="SchedulingAgent",
                input_mapping={
                    "proposed_times": "proposed_times",
                    "my_availability": "my_availability",
                    "attendees": "attendees"
                },
                output_mapping={
                    "selected_time": "meeting_time",
                    "duration": "meeting_duration"
                }
            ),
            
            # Step 4: Create calendar event
            WorkflowStep(
                agent_name="CalendarAgent",
                input_mapping={
                    "user_id": "user_id",
                    "title": "email_subject",
                    "start_time": "meeting_time",
                    "duration": "meeting_duration",
                    "attendees": "attendees"
                },
                output_mapping={
                    "event_id": "calendar_event_id",
                    "event_link": "calendar_link"
                }
            ),
            
            # Step 5: Send confirmation email
            WorkflowStep(
                agent_name="EmailAgent",
                input_mapping={
                    "to": "email_from",
                    "subject": "email_subject",
                    "meeting_time": "meeting_time",
                    "calendar_link": "calendar_link"
                },
                output_mapping={
                    "sent": "email_sent",
                    "message_id": "confirmation_email_id"
                },
                error_handler="EmailErrorAgent"
            ),
            
            # Step 6: Gather meeting prep context
            WorkflowStep(
                agent_name="MeetingPrepAgent",
                input_mapping={
                    "contact": "email_from",
                    "topic": "meeting_topic",
                    "meeting_time": "meeting_time",
                    "user_id": "user_id"
                },
                output_mapping={
                    "prep_doc": "prep_document",
                    "context": "meeting_context"
                }
            ),
            
            # Step 7: Create prep tasks
            WorkflowStep(
                agent_name="TaskAgent",
                input_mapping={
                    "meeting_time": "meeting_time",
                    "prep_doc": "prep_document",
                    "topic": "meeting_topic",
                    "user_id": "user_id"
                },
                output_mapping={
                    "tasks": "created_tasks"
                }
            )
        ],
        
        variables={
            "default_duration": 60,  # minutes
            "prep_time_hours": 24  # hours before meeting
        },
        
        max_retries=3,
        enable_rollback=True
    )


# Rollback handlers
async def rollback_calendar_event(state):
    """Delete calendar event if workflow fails"""
    if "calendar_event_id" in state:
        # TODO: Call CalendarAgent to delete event
        pass


async def rollback_email(state):
    """Send cancellation email if workflow fails"""
    if "email_sent" in state:
        # TODO: Call EmailAgent to send cancellation
        pass
