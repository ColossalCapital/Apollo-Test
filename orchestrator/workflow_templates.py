"""
Visual Workflow Templates for Meta-Orchestrator

Pre-built n8n-style workflows that can be customized.
"""

from orchestrator.meta_orchestrator import (
    MetaOrchestrator, VisualWorkflow, WorkflowNode, NodeType
)


def create_meeting_scheduling_visual_workflow(orchestrator: MetaOrchestrator) -> VisualWorkflow:
    """
    Create visual meeting scheduling workflow
    
    Visual Flow:
    
    [Email Trigger] → [Parse Email] → [Check Calendar] → [Condition: Available?]
                                                              ├─ Yes → [Schedule Meeting] → [Send Confirmation] → [Create Tasks]
                                                              └─ No → [Send Unavailable Email]
    """
    
    # Create workflow
    workflow = orchestrator.create_workflow(
        name="Meeting Scheduling (Visual)",
        description="Visual workflow for scheduling meetings from emails"
    )
    
    # Add nodes
    trigger = orchestrator.add_node(
        workflow,
        NodeType.TRIGGER,
        "Email Trigger",
        config={"trigger_type": "email", "intent": "schedule_meeting"},
        position={"x": 100, "y": 100}
    )
    
    parse = orchestrator.add_node(
        workflow,
        NodeType.AGENT,
        "Parse Email",
        agent_name="EmailParserAgent",
        config={
            "input_mapping": {"email": "trigger.email"},
            "output_mapping": {"parsed": "email_data"}
        },
        position={"x": 300, "y": 100}
    )
    
    check_calendar = orchestrator.add_node(
        workflow,
        NodeType.AGENT,
        "Check Calendar",
        agent_name="CalendarAgent",
        config={
            "input_mapping": {
                "user_id": "user_id",
                "proposed_times": "nodes.node_1.parsed.proposed_times"
            },
            "output_mapping": {"availability": "my_availability"}
        },
        position={"x": 500, "y": 100}
    )
    
    condition = orchestrator.add_node(
        workflow,
        NodeType.CONDITION,
        "Available?",
        config={"condition": "state['nodes']['node_2']['availability']"},
        position={"x": 700, "y": 100}
    )
    
    schedule = orchestrator.add_node(
        workflow,
        NodeType.AGENT,
        "Schedule Meeting",
        agent_name="SchedulingAgent",
        config={
            "input_mapping": {
                "proposed_times": "nodes.node_1.parsed.proposed_times",
                "availability": "nodes.node_2.availability"
            },
            "output_mapping": {"meeting_time": "selected_time"}
        },
        position={"x": 900, "y": 50}
    )
    
    send_confirmation = orchestrator.add_node(
        workflow,
        NodeType.AGENT,
        "Send Confirmation",
        agent_name="EmailAgent",
        config={
            "input_mapping": {
                "to": "nodes.node_1.parsed.from",
                "meeting_time": "nodes.node_4.meeting_time"
            }
        },
        position={"x": 1100, "y": 50}
    )
    
    create_tasks = orchestrator.add_node(
        workflow,
        NodeType.AGENT,
        "Create Tasks",
        agent_name="TaskAgent",
        config={
            "input_mapping": {
                "meeting_time": "nodes.node_4.meeting_time"
            }
        },
        position={"x": 1300, "y": 50}
    )
    
    send_unavailable = orchestrator.add_node(
        workflow,
        NodeType.AGENT,
        "Send Unavailable Email",
        agent_name="EmailAgent",
        config={
            "input_mapping": {
                "to": "nodes.node_1.parsed.from",
                "message": "Sorry, not available at those times"
            }
        },
        position={"x": 900, "y": 150}
    )
    
    # Connect nodes
    orchestrator.connect(workflow, trigger, parse)
    orchestrator.connect(workflow, parse, check_calendar)
    orchestrator.connect(workflow, check_calendar, condition)
    
    # Conditional branching
    orchestrator.add_conditional_branch(
        workflow,
        condition,
        schedule,
        send_unavailable,
        "state['nodes']['node_2']['availability']"
    )
    
    orchestrator.connect(workflow, schedule, send_confirmation)
    orchestrator.connect(workflow, send_confirmation, create_tasks)
    
    return workflow


def create_parallel_processing_workflow(orchestrator: MetaOrchestrator) -> VisualWorkflow:
    """
    Create workflow with parallel processing
    
    Visual Flow:
    
    [Trigger] → [Parse Document] → [Parallel Split]
                                        ├─ [Extract Text] ─┐
                                        ├─ [Extract Images] ─┤→ [Merge] → [Store Results]
                                        └─ [Extract Metadata] ─┘
    """
    
    workflow = orchestrator.create_workflow(
        name="Parallel Document Processing",
        description="Process document with parallel extraction"
    )
    
    # Add nodes
    trigger = orchestrator.add_node(
        workflow, NodeType.TRIGGER, "Document Upload",
        position={"x": 100, "y": 200}
    )
    
    parse = orchestrator.add_node(
        workflow, NodeType.AGENT, "Parse Document",
        agent_name="DocumentParserAgent",
        position={"x": 300, "y": 200}
    )
    
    split = orchestrator.add_node(
        workflow, NodeType.PARALLEL, "Parallel Split",
        position={"x": 500, "y": 200}
    )
    
    extract_text = orchestrator.add_node(
        workflow, NodeType.AGENT, "Extract Text",
        agent_name="TextExtractorAgent",
        position={"x": 700, "y": 100}
    )
    
    extract_images = orchestrator.add_node(
        workflow, NodeType.AGENT, "Extract Images",
        agent_name="ImageExtractorAgent",
        position={"x": 700, "y": 200}
    )
    
    extract_metadata = orchestrator.add_node(
        workflow, NodeType.AGENT, "Extract Metadata",
        agent_name="MetadataExtractorAgent",
        position={"x": 700, "y": 300}
    )
    
    merge = orchestrator.add_node(
        workflow, NodeType.MERGE, "Merge Results",
        position={"x": 900, "y": 200}
    )
    
    store = orchestrator.add_node(
        workflow, NodeType.AGENT, "Store Results",
        agent_name="StorageAgent",
        position={"x": 1100, "y": 200}
    )
    
    # Connect nodes
    orchestrator.connect(workflow, trigger, parse)
    orchestrator.connect(workflow, parse, split)
    
    # Parallel execution
    orchestrator.add_parallel_execution(
        workflow,
        split,
        [extract_text, extract_images, extract_metadata],
        merge
    )
    
    orchestrator.connect(workflow, merge, store)
    
    return workflow


def create_loop_workflow(orchestrator: MetaOrchestrator) -> VisualWorkflow:
    """
    Create workflow with loop
    
    Visual Flow:
    
    [Trigger] → [Get Items] → [Loop Start] → [Process Item] → [Store Result]
                                    ↑                               ↓
                                    └───────── [More Items?] ←──────┘
                                                    ↓ No
                                              [Complete]
    """
    
    workflow = orchestrator.create_workflow(
        name="Batch Processing Loop",
        description="Process items in a loop"
    )
    
    # Add nodes
    trigger = orchestrator.add_node(
        workflow, NodeType.TRIGGER, "Batch Trigger",
        position={"x": 100, "y": 200}
    )
    
    get_items = orchestrator.add_node(
        workflow, NodeType.AGENT, "Get Items",
        agent_name="DataFetchAgent",
        position={"x": 300, "y": 200}
    )
    
    loop_start = orchestrator.add_node(
        workflow, NodeType.LOOP, "Loop Start",
        config={"items": "nodes.node_1.items"},
        position={"x": 500, "y": 200}
    )
    
    process = orchestrator.add_node(
        workflow, NodeType.AGENT, "Process Item",
        agent_name="ProcessorAgent",
        position={"x": 700, "y": 200}
    )
    
    store = orchestrator.add_node(
        workflow, NodeType.AGENT, "Store Result",
        agent_name="StorageAgent",
        position={"x": 900, "y": 200}
    )
    
    complete = orchestrator.add_node(
        workflow, NodeType.AGENT, "Complete",
        agent_name="NotificationAgent",
        position={"x": 700, "y": 300}
    )
    
    # Connect nodes
    orchestrator.connect(workflow, trigger, get_items)
    orchestrator.connect(workflow, get_items, loop_start)
    
    # Loop structure
    orchestrator.add_loop(
        workflow,
        loop_start,
        [process, store],
        complete,
        "state['loop_index'] < len(state['items'])"
    )
    
    return workflow


def create_error_handling_workflow(orchestrator: MetaOrchestrator) -> VisualWorkflow:
    """
    Create workflow with error handling
    
    Visual Flow:
    
    [Trigger] → [Risky Operation] ─┬─ Success → [Continue]
                                    └─ Error → [Error Handler] → [Notify] → [Retry?]
                                                                                ├─ Yes → [Risky Operation]
                                                                                └─ No → [Fail]
    """
    
    workflow = orchestrator.create_workflow(
        name="Error Handling Example",
        description="Workflow with comprehensive error handling"
    )
    
    # Add nodes
    trigger = orchestrator.add_node(
        workflow, NodeType.TRIGGER, "Start",
        position={"x": 100, "y": 200}
    )
    
    risky = orchestrator.add_node(
        workflow, NodeType.AGENT, "Risky Operation",
        agent_name="ExternalAPIAgent",
        position={"x": 300, "y": 200}
    )
    
    continue_node = orchestrator.add_node(
        workflow, NodeType.AGENT, "Continue",
        agent_name="NextStepAgent",
        position={"x": 500, "y": 150}
    )
    
    error_handler = orchestrator.add_node(
        workflow, NodeType.ERROR_HANDLER, "Error Handler",
        position={"x": 500, "y": 250}
    )
    
    notify = orchestrator.add_node(
        workflow, NodeType.AGENT, "Notify Error",
        agent_name="NotificationAgent",
        position={"x": 700, "y": 250}
    )
    
    # Connect nodes
    orchestrator.connect(workflow, trigger, risky)
    orchestrator.connect(workflow, risky, continue_node, label="success")
    orchestrator.connect(workflow, risky, error_handler, label="error")
    orchestrator.connect(workflow, error_handler, notify)
    
    return workflow


def load_all_templates(orchestrator: MetaOrchestrator):
    """Load all workflow templates"""
    
    templates = [
        create_meeting_scheduling_visual_workflow(orchestrator),
        create_parallel_processing_workflow(orchestrator),
        create_loop_workflow(orchestrator),
        create_error_handling_workflow(orchestrator)
    ]
    
    return templates
