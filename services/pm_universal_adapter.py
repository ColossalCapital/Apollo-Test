"""
Universal PM Tool Adapter
Maps between different PM tools (Linear, Jira, GitHub, Bitbucket)
Provides bidirectional sync and ticket creation from documentation
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime
import json


class PMTool(Enum):
    """Supported PM tools"""
    LINEAR = "linear"
    JIRA = "jira"
    GITHUB = "github"
    BITBUCKET = "bitbucket"


class TicketType(Enum):
    """Universal ticket types"""
    EPIC = "epic"
    STORY = "story"
    TASK = "task"
    BUG = "bug"
    SUBTASK = "subtask"
    SPIKE = "spike"


class TicketStatus(Enum):
    """Universal ticket statuses"""
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    BLOCKED = "blocked"
    DONE = "done"
    CANCELLED = "cancelled"


class TicketPriority(Enum):
    """Universal ticket priorities"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


@dataclass
class UniversalTicket:
    """Universal ticket format that maps to all PM tools"""
    
    id: str
    title: str
    description: str
    type: TicketType
    status: TicketStatus
    priority: TicketPriority
    parent_id: Optional[str] = None
    epic_id: Optional[str] = None
    assignee: Optional[str] = None
    team: Optional[str] = None
    labels: List[str] = field(default_factory=list)
    affected_files: List[str] = field(default_factory=list)
    story_points: Optional[int] = None
    suggested_agent: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    source_tool: Optional[PMTool] = None
    source_id: Optional[str] = None
    synced_to: Dict[PMTool, str] = field(default_factory=dict)


class PMToolMapping:
    """Mapping between universal format and PM tool-specific formats"""
    
    LINEAR_MAPPING = {
        "type": {
            TicketType.EPIC: "initiative",
            TicketType.STORY: "feature",
            TicketType.TASK: "task",
            TicketType.BUG: "bug",
            TicketType.SUBTASK: "sub-issue",
            TicketType.SPIKE: "task"
        },
        "status": {
            TicketStatus.BACKLOG: "Backlog",
            TicketStatus.TODO: "Todo",
            TicketStatus.IN_PROGRESS: "In Progress",
            TicketStatus.IN_REVIEW: "In Review",
            TicketStatus.BLOCKED: "Blocked",
            TicketStatus.DONE: "Done",
            TicketStatus.CANCELLED: "Canceled"
        },
        "priority": {
            TicketPriority.CRITICAL: 1,
            TicketPriority.HIGH: 2,
            TicketPriority.MEDIUM: 3,
            TicketPriority.LOW: 4,
            TicketPriority.NONE: 0
        }
    }
    
    JIRA_MAPPING = {
        "type": {
            TicketType.EPIC: "Epic",
            TicketType.STORY: "Story",
            TicketType.TASK: "Task",
            TicketType.BUG: "Bug",
            TicketType.SUBTASK: "Sub-task",
            TicketType.SPIKE: "Spike"
        },
        "status": {
            TicketStatus.BACKLOG: "Backlog",
            TicketStatus.TODO: "To Do",
            TicketStatus.IN_PROGRESS: "In Progress",
            TicketStatus.IN_REVIEW: "In Review",
            TicketStatus.BLOCKED: "Blocked",
            TicketStatus.DONE: "Done",
            TicketStatus.CANCELLED: "Cancelled"
        },
        "priority": {
            TicketPriority.CRITICAL: "Highest",
            TicketPriority.HIGH: "High",
            TicketPriority.MEDIUM: "Medium",
            TicketPriority.LOW: "Low",
            TicketPriority.NONE: "Lowest"
        }
    }
    
    GITHUB_MAPPING = {
        "type": {
            TicketType.EPIC: "epic",
            TicketType.STORY: "enhancement",
            TicketType.TASK: "task",
            TicketType.BUG: "bug",
            TicketType.SUBTASK: "task",
            TicketType.SPIKE: "research"
        },
        "priority": {
            TicketPriority.CRITICAL: "priority: critical",
            TicketPriority.HIGH: "priority: high",
            TicketPriority.MEDIUM: "priority: medium",
            TicketPriority.LOW: "priority: low",
            TicketPriority.NONE: ""
        }
    }
    
    @classmethod
    def to_tool_format(cls, ticket: UniversalTicket, tool: PMTool) -> Dict:
        """Convert universal ticket to tool-specific format"""
        if tool == PMTool.LINEAR:
            return cls._to_linear(ticket)
        elif tool == PMTool.JIRA:
            return cls._to_jira(ticket)
        elif tool == PMTool.GITHUB:
            return cls._to_github(ticket)
        else:
            raise ValueError(f"Unsupported PM tool: {tool}")
    
    @classmethod
    def from_tool_format(cls, data: Dict, tool: PMTool) -> UniversalTicket:
        """Convert tool-specific format to universal ticket"""
        if tool == PMTool.LINEAR:
            return cls._from_linear(data)
        elif tool == PMTool.JIRA:
            return cls._from_jira(data)
        elif tool == PMTool.GITHUB:
            return cls._from_github(data)
        else:
            raise ValueError(f"Unsupported PM tool: {tool}")
    
    @classmethod
    def _to_linear(cls, ticket: UniversalTicket) -> Dict:
        """Convert to Linear format"""
        return {
            "title": ticket.title,
            "description": ticket.description,
            "teamId": ticket.team,
            "assigneeId": ticket.assignee,
            "priority": cls.LINEAR_MAPPING["priority"][ticket.priority],
            "labelIds": ticket.labels,
            "parentId": ticket.parent_id,
            "projectId": ticket.epic_id,
            "estimate": ticket.story_points,
        }
    
    @classmethod
    def _from_linear(cls, data: Dict) -> UniversalTicket:
        """Convert from Linear format"""
        type_map = {v: k for k, v in cls.LINEAR_MAPPING["type"].items()}
        status_map = {v: k for k, v in cls.LINEAR_MAPPING["status"].items()}
        priority_map = {v: k for k, v in cls.LINEAR_MAPPING["priority"].items()}
        
        return UniversalTicket(
            id=data.get("id"),
            title=data.get("title"),
            description=data.get("description", ""),
            type=type_map.get(data.get("type"), TicketType.TASK),
            status=status_map.get(data.get("state", {}).get("name"), TicketStatus.TODO),
            priority=priority_map.get(data.get("priority"), TicketPriority.NONE),
            source_tool=PMTool.LINEAR,
            source_id=data.get("id")
        )
    
    @classmethod
    def _to_jira(cls, ticket: UniversalTicket) -> Dict:
        """Convert to Jira format"""
        fields = {
            "project": {"key": ticket.team},
            "summary": ticket.title,
            "description": ticket.description,
            "issuetype": {"name": cls.JIRA_MAPPING["type"][ticket.type]},
            "priority": {"name": cls.JIRA_MAPPING["priority"][ticket.priority]},
            "labels": ticket.labels,
        }
        
        if ticket.assignee:
            fields["assignee"] = {"name": ticket.assignee}
        if ticket.parent_id:
            fields["parent"] = {"key": ticket.parent_id}
        if ticket.epic_id:
            fields["customfield_10014"] = ticket.epic_id
        if ticket.story_points:
            fields["customfield_10016"] = ticket.story_points
        
        return {"fields": fields}
    
    @classmethod
    def _from_jira(cls, data: Dict) -> UniversalTicket:
        """Convert from Jira format"""
        fields = data.get("fields", {})
        type_map = {v: k for k, v in cls.JIRA_MAPPING["type"].items()}
        status_map = {v: k for k, v in cls.JIRA_MAPPING["status"].items()}
        priority_map = {v: k for k, v in cls.JIRA_MAPPING["priority"].items()}
        
        return UniversalTicket(
            id=data.get("key"),
            title=fields.get("summary"),
            description=fields.get("description", ""),
            type=type_map.get(fields.get("issuetype", {}).get("name"), TicketType.TASK),
            status=status_map.get(fields.get("status", {}).get("name"), TicketStatus.TODO),
            priority=priority_map.get(fields.get("priority", {}).get("name"), TicketPriority.NONE),
            source_tool=PMTool.JIRA,
            source_id=data.get("key")
        )
    
    @classmethod
    def _to_github(cls, ticket: UniversalTicket) -> Dict:
        """Convert to GitHub Issues format"""
        labels = ticket.labels.copy()
        labels.append(cls.GITHUB_MAPPING["type"][ticket.type])
        
        priority_label = cls.GITHUB_MAPPING["priority"][ticket.priority]
        if priority_label:
            labels.append(priority_label)
        
        body = ticket.description
        if ticket.story_points:
            body += f"\n\n**Story Points:** {ticket.story_points}"
        if ticket.affected_files:
            body += f"\n\n**Affected Files:**\n" + "\n".join([f"- {f}" for f in ticket.affected_files])
        if ticket.suggested_agent:
            body += f"\n\n**Suggested Agent:** {ticket.suggested_agent}"
        
        return {
            "title": ticket.title,
            "body": body,
            "labels": labels,
            "assignees": [ticket.assignee] if ticket.assignee else [],
        }
    
    @classmethod
    def _from_github(cls, data: Dict) -> UniversalTicket:
        """Convert from GitHub Issues format"""
        labels = [label.get("name") for label in data.get("labels", [])]
        
        ticket_type = TicketType.TASK
        for label in labels:
            for t, github_type in cls.GITHUB_MAPPING["type"].items():
                if label == github_type:
                    ticket_type = t
                    break
        
        priority = TicketPriority.NONE
        for label in labels:
            for p, github_priority in cls.GITHUB_MAPPING["priority"].items():
                if label == github_priority:
                    priority = p
                    break
        
        status = TicketStatus.DONE if data.get("state") == "closed" else TicketStatus.TODO
        
        return UniversalTicket(
            id=str(data.get("number")),
            title=data.get("title"),
            description=data.get("body", ""),
            type=ticket_type,
            status=status,
            priority=priority,
            labels=[l for l in labels if not l.startswith("priority:")],
            source_tool=PMTool.GITHUB,
            source_id=str(data.get("number"))
        )


class DocumentationToTicketConverter:
    """Convert documentation to tickets"""
    
    def convert_feature_docs_to_tickets(self, doc_path: str) -> List[UniversalTicket]:
        """Convert feature documentation to Epic + Stories + Tasks"""
        doc_content = self._read_documentation(doc_path)
        structure = self._parse_doc_structure(doc_content)
        
        tickets = []
        epic = self._create_epic(structure)
        tickets.append(epic)
        
        for story_section in structure.get("stories", []):
            story = self._create_story(story_section, epic.id)
            tickets.append(story)
            
            for task_section in story_section.get("tasks", []):
                task = self._create_task(task_section, story.id, epic.id)
                tickets.append(task)
        
        return tickets
    
    def _read_documentation(self, doc_path: str) -> str:
        with open(doc_path, 'r') as f:
            return f.read()
    
    def _parse_doc_structure(self, content: str) -> Dict:
        """Parse markdown documentation into structure"""
        lines = content.split('\n')
        structure = {"title": "", "description": "", "stories": []}
        
        current_story = None
        current_task = None
        
        for line in lines:
            if line.startswith('# '):
                structure["title"] = line.replace('# ', '').strip()
            elif line.startswith('## '):
                if current_story:
                    structure["stories"].append(current_story)
                current_story = {"title": line.replace('## ', '').strip(), "tasks": []}
            elif line.startswith('### '):
                if current_task and current_story:
                    current_story["tasks"].append(current_task)
                current_task = {"title": line.replace('### ', '').strip()}
        
        if current_task and current_story:
            current_story["tasks"].append(current_task)
        if current_story:
            structure["stories"].append(current_story)
        
        return structure
    
    def _create_epic(self, structure: Dict) -> UniversalTicket:
        return UniversalTicket(
            id=f"epic-{hash(structure['title'])}",
            title=structure["title"],
            description=structure.get("description", ""),
            type=TicketType.EPIC,
            status=TicketStatus.BACKLOG,
            priority=TicketPriority.MEDIUM
        )
    
    def _create_story(self, story_section: Dict, epic_id: str) -> UniversalTicket:
        return UniversalTicket(
            id=f"story-{hash(story_section['title'])}",
            title=story_section["title"],
            description="",
            type=TicketType.STORY,
            status=TicketStatus.BACKLOG,
            priority=TicketPriority.MEDIUM,
            epic_id=epic_id
        )
    
    def _create_task(self, task_section: Dict, parent_id: str, epic_id: str) -> UniversalTicket:
        return UniversalTicket(
            id=f"task-{hash(task_section['title'])}",
            title=task_section["title"],
            description="",
            type=TicketType.TASK,
            status=TicketStatus.BACKLOG,
            priority=TicketPriority.MEDIUM,
            parent_id=parent_id,
            epic_id=epic_id
        )
