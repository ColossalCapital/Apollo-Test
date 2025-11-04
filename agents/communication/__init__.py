"""
Communication Agents
"""

from .calendar_agent import CalendarAgent
from .contact_agent import ContactAgent
from .slack_agent import SlackAgent

__all__ = [
    "CalendarAgent",
    "ContactAgent",
    "SlackAgent",
]
