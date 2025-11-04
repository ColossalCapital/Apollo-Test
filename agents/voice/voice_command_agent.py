"""
Voice Command Agent

Processes voice commands with full context awareness.

Features:
- Whisper speech-to-text
- Intent recognition
- Context-aware responses
- Clarifying questions
- Action execution
- Text-to-speech responses
"""

import logging
from typing import Dict, List, Optional
import openai
from datetime import datetime

logger = logging.getLogger(__name__)


class VoiceCommandAgent:
    """
    Process voice commands with context
    
    Supports:
    - Ticket creation
    - Code generation
    - Review & approval
    - Deployment
    - Self-iteration
    """
    
    def __init__(self):
        # Use Whisper for speech-to-text
        self.whisper_model = "whisper-1"
        
    async def process_voice_command(
        self,
        audio_file: str,
        context: Dict
    ) -> Dict:
        """
        Process voice command with context
        
        Args:
            audio_file: Path to audio file
            context: Current context (screen, entity, project)
            
        Returns:
            {
                'transcript': str,
                'intent': str,
                'action': Dict,
                'response': str,
                'speak': str,
                'clarifying_questions': List[str]
            }
        """
        
        logger.info(f"🎤 Processing voice command")
        
        # 1. Speech to text (Whisper)
        transcript = await self._transcribe_audio(audio_file)
        logger.info(f"📝 Transcript: {transcript}")
        
        # 2. Recognize intent
        intent = await self._recognize_intent(transcript, context)
        logger.info(f"🎯 Intent: {intent['type']}")
        
        # 3. Generate response
        response = await self._generate_response(intent, context)
        
        return response
        
    async def _transcribe_audio(self, audio_file: str) -> str:
        """Transcribe audio using Whisper"""
        try:
            with open(audio_file, 'rb') as f:
                transcript = openai.Audio.transcribe(
                    model=self.whisper_model,
                    file=f
                )
            return transcript['text']
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return ""
            
    async def _recognize_intent(
        self,
        transcript: str,
        context: Dict
    ) -> Dict:
        """Recognize user intent from transcript"""
        
        # Use GPT to understand intent
        prompt = f"""Analyze this voice command and determine the intent.

Transcript: "{transcript}"

Context:
- Screen: {context.get('screen', 'unknown')}
- Entity: {context.get('entity', 'none')}
- Project: {context.get('project', 'none')}

Possible intents:
1. create_ticket - User wants to create a new ticket
2. generate_code - User wants to generate code
3. review_changes - User wants to review code changes
4. approve_changes - User wants to approve changes
5. deploy - User wants to deploy
6. modify_current_screen - User wants to modify what they're looking at
7. ask_question - User has a question
8. other - Something else

Return JSON:
{{
    "type": "intent_type",
    "confidence": 0.95,
    "entities": {{
        "project": "atlas",
        "action": "add dashboard",
        "target": "entity screen"
    }},
    "needs_clarification": false,
    "clarifying_questions": []
}}
"""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a voice command analyzer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            import json
            intent = json.loads(response.choices[0].message.content)
            return intent
            
        except Exception as e:
            logger.error(f"Intent recognition failed: {e}")
            return {
                'type': 'other',
                'confidence': 0.0,
                'entities': {},
                'needs_clarification': True,
                'clarifying_questions': ["I didn't understand that. Could you rephrase?"]
            }
            
    async def _generate_response(
        self,
        intent: Dict,
        context: Dict
    ) -> Dict:
        """Generate response based on intent"""
        
        intent_type = intent['type']
        
        if intent_type == 'create_ticket':
            return await self._handle_create_ticket(intent, context)
        elif intent_type == 'generate_code':
            return await self._handle_generate_code(intent, context)
        elif intent_type == 'review_changes':
            return await self._handle_review_changes(intent, context)
        elif intent_type == 'approve_changes':
            return await self._handle_approve_changes(intent, context)
        elif intent_type == 'deploy':
            return await self._handle_deploy(intent, context)
        elif intent_type == 'modify_current_screen':
            return await self._handle_modify_screen(intent, context)
        else:
            return {
                'intent': intent_type,
                'action': None,
                'response': "I'm not sure what you want me to do.",
                'speak': "I'm not sure what you want me to do. Could you rephrase?",
                'clarifying_questions': intent.get('clarifying_questions', [])
            }
            
    async def _handle_create_ticket(
        self,
        intent: Dict,
        context: Dict
    ) -> Dict:
        """Handle ticket creation"""
        
        entities = intent['entities']
        project = entities.get('project', context.get('project'))
        action = entities.get('action', 'unknown')
        
        # Check if we need more info
        if not project or intent.get('needs_clarification'):
            return {
                'intent': 'create_ticket',
                'action': {
                    'type': 'ask_clarification',
                    'questions': [
                        f"Which project? {', '.join(['Atlas', 'Delt', 'Akashic'])}",
                        "What should the feature do?",
                        "Any specific requirements?"
                    ]
                },
                'response': "I'll create a ticket. I have some questions first.",
                'speak': "I'll create a ticket. Which project is this for?",
                'clarifying_questions': [
                    "Which project?",
                    "What should it do?",
                    "Any specific requirements?"
                ]
            }
            
        # We have enough info
        return {
            'intent': 'create_ticket',
            'action': {
                'type': 'create_ticket',
                'project': project,
                'title': action,
                'auto_refine': True
            },
            'response': f"Creating ticket for {project}: {action}",
            'speak': f"Creating ticket for {project}. Should I generate code now or create the ticket first?",
            'clarifying_questions': []
        }
        
    async def _handle_generate_code(
        self,
        intent: Dict,
        context: Dict
    ) -> Dict:
        """Handle code generation"""
        
        return {
            'intent': 'generate_code',
            'action': {
                'type': 'generate_code',
                'ticket_id': context.get('ticket_id')
            },
            'response': "Generating code...",
            'speak': "Generating code. This will take about 30 seconds.",
            'clarifying_questions': []
        }
        
    async def _handle_review_changes(
        self,
        intent: Dict,
        context: Dict
    ) -> Dict:
        """Handle code review"""
        
        return {
            'intent': 'review_changes',
            'action': {
                'type': 'show_review',
                'pr_id': context.get('pr_id')
            },
            'response': "Opening code review...",
            'speak': "Opening code review. Swipe to see changes. Say approve when ready.",
            'clarifying_questions': []
        }
        
    async def _handle_approve_changes(
        self,
        intent: Dict,
        context: Dict
    ) -> Dict:
        """Handle approval"""
        
        return {
            'intent': 'approve_changes',
            'action': {
                'type': 'approve',
                'pr_id': context.get('pr_id')
            },
            'response': "Approving changes...",
            'speak': "Approved. Deploying to QA. This will take about 2 minutes.",
            'clarifying_questions': []
        }
        
    async def _handle_deploy(
        self,
        intent: Dict,
        context: Dict
    ) -> Dict:
        """Handle deployment"""
        
        entities = intent['entities']
        environment = entities.get('environment', 'production')
        
        return {
            'intent': 'deploy',
            'action': {
                'type': 'deploy',
                'environment': environment,
                'pr_id': context.get('pr_id')
            },
            'response': f"Deploying to {environment}...",
            'speak': f"Deploying to {environment}. This will take about 2 minutes.",
            'clarifying_questions': []
        }
        
    async def _handle_modify_screen(
        self,
        intent: Dict,
        context: Dict
    ) -> Dict:
        """Handle modifying current screen (self-iteration)"""
        
        entities = intent['entities']
        modification = entities.get('action', 'unknown')
        current_screen = context.get('screen', 'unknown')
        current_project = context.get('project', 'unknown')
        
        # Check if modifying the app we're currently using
        is_self_iteration = (
            current_project.lower() == 'atlas' and
            context.get('current_app') == 'atlas'
        )
        
        if is_self_iteration:
            return {
                'intent': 'modify_current_screen',
                'action': {
                    'type': 'self_iteration',
                    'screen': current_screen,
                    'modification': modification,
                    'create_qa_preview': True
                },
                'response': f"Modifying {current_screen}...",
                'speak': f"I'll modify {current_screen}. Since you're using Atlas, I'll create a QA preview for you to test. This will take about 2 minutes.",
                'clarifying_questions': []
            }
        else:
            return {
                'intent': 'modify_current_screen',
                'action': {
                    'type': 'modify_screen',
                    'screen': current_screen,
                    'modification': modification
                },
                'response': f"Modifying {current_screen}...",
                'speak': f"I'll modify {current_screen}. Should I generate code now?",
                'clarifying_questions': []
            }


# Global instance
_voice_command_agent = VoiceCommandAgent()


def get_voice_command_agent() -> VoiceCommandAgent:
    """Get global voice command agent"""
    return _voice_command_agent
