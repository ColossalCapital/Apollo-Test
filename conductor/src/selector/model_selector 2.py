"""
Model Selector - Choose the right AI model for each job

The Conductor's first decision: Which instrument plays this part?
"""

from typing import Optional, Dict, Any, List
from enum import Enum

class ModelType(Enum):
    DEEPSEEK_CODER = "deepseek_coder_v2"
    DEEPSEEK_CHAT = "deepseek_chat_v2"
    GPT4_TURBO = "gpt4_turbo"
    GPT35_TURBO = "gpt35_turbo"
    CLAUDE_SONNET = "claude_sonnet_3.5"
    CUSTOM_USER_MODEL = "custom"

class ModelSelector:
    """
    Intelligently selects which AI model to use
    Based on: query type, user tier, cost, accuracy, speed
    """
    
    def __init__(self):
        self.models = self._load_available_models()
    
    async def select(
        self,
        query: str,
        user_id: str,
        user_tier: str,
        context: str = "delt",  # delt, akashic, atlas
        max_cost_wtf: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Select the optimal model for this query
        
        Returns decision with explanation
        """
        
        # Check if user has custom trained model
        custom_model = await self._get_user_custom_model(user_id)
        
        # Analyze query type
        query_type = self._analyze_query_type(query)
        
        # Score all available models
        candidates = self._get_available_models_for_tier(user_tier)
        if custom_model:
            candidates.append(custom_model)
        
        scored_models = [
            {
                'model': model,
                'score': self._score_model(model, query_type, context, max_cost_wtf)
            }
            for model in candidates
        ]
        
        # Sort by score
        scored_models.sort(key=lambda x: x['score'], reverse=True)
        
        selected = scored_models[0]['model']
        
        return {
            'model': selected,
            'model_name': selected['name'],
            'reasoning': self._explain_selection(selected, query_type),
            'alternatives': [s['model'] for s in scored_models[1:3]],
            'estimated_cost_wtf': selected['cost_per_query'],
            'estimated_response_time': selected['avg_response_time']
        }
    
    def _analyze_query_type(self, query: str) -> str:
        """
        Determine what kind of query this is
        """
        
        query_lower = query.lower()
        
        # Code-related keywords
        if any(kw in query_lower for kw in ['write', 'code', 'function', 'class', 'def', 'strategy']):
            return 'code_generation'
        
        # Analysis keywords
        elif any(kw in query_lower for kw in ['analyze', 'what', 'why', 'explain', 'compare']):
            return 'analysis'
        
        # Quick question keywords
        elif any(kw in query_lower for kw in ['is', 'are', 'should', 'can', 'simple']):
            return 'quick_question'
        
        # Market/trading keywords
        elif any(kw in query_lower for kw in ['trade', 'buy', 'sell', 'market', 'price']):
            return 'trading_advice'
        
        else:
            return 'general_chat'
    
    def _score_model(
        self,
        model: Dict,
        query_type: str,
        context: str,
        max_cost: Optional[float]
    ) -> float:
        """
        Score a model for this specific query
        Higher score = better fit
        """
        
        score = 0.0
        
        # Accuracy weight (40%)
        score += model['accuracy'] * 0.4
        
        # Speed weight (30%)
        max_time = 10.0  # 10 seconds max
        speed_score = max(0, 1 - (model['avg_response_time'] / max_time))
        score += speed_score * 0.3
        
        # Cost weight (20%)
        if max_cost:
            if model['cost_per_query'] <= max_cost:
                cost_score = 1 - (model['cost_per_query'] / max_cost)
                score += cost_score * 0.2
        
        # Specialization bonus (10%)
        if self._is_specialized(model, query_type):
            score += 0.5  # Big bonus for specialization!
        
        return score
    
    def _is_specialized(self, model: Dict, query_type: str) -> bool:
        """
        Check if model is specialized for this query type
        """
        
        specializations = {
            'code_generation': ['deepseek_coder_v2'],
            'trading_advice': ['custom'],  # User's trained models
            'analysis': ['gpt4_turbo', 'claude_sonnet_3.5'],
            'quick_question': ['gpt35_turbo'],
        }
        
        return model['id'] in specializations.get(query_type, [])
    
    def _explain_selection(self, model: Dict, query_type: str) -> str:
        """
        Explain why this model was chosen
        Transparency for users!
        """
        
        if model['id'] == 'custom':
            return f"Using your custom model (trained on your data, {model['accuracy']*100:.1f}% accuracy)"
        
        elif query_type == 'code_generation':
            return f"DeepSeek Coder selected (best for coding tasks)"
        
        elif query_type == 'quick_question':
            return f"GPT-3.5 Turbo selected (fast & cost-effective for simple queries)"
        
        else:
            return f"{model['name']} selected (balanced performance)"
    
    def _load_available_models(self) -> List[Dict]:
        """
        Load model registry
        TODO: Load from database/config
        """
        return [
            {
                'id': 'deepseek_coder_v2',
                'name': 'DeepSeek Coder v2',
                'accuracy': 0.85,
                'avg_response_time': 2.3,
                'cost_per_query': 0.02,
                'specialization': 'code'
            },
            {
                'id': 'gpt4_turbo',
                'name': 'GPT-4 Turbo',
                'accuracy': 0.82,
                'avg_response_time': 3.1,
                'cost_per_query': 0.05,
                'specialization': 'general'
            },
            {
                'id': 'gpt35_turbo',
                'name': 'GPT-3.5 Turbo',
                'accuracy': 0.70,
                'avg_response_time': 1.2,
                'cost_per_query': 0.01,
                'specialization': 'quick'
            },
        ]
    
    def _get_available_models_for_tier(self, tier: str) -> List[Dict]:
        """
        Filter models by user tier
        """
        all_models = self._load_available_models()
        
        if tier in ['free']:
            return [m for m in all_models if m['id'] == 'gpt35_turbo']
        elif tier in ['individual']:
            return [m for m in all_models if m['cost_per_query'] <= 0.02]
        else:
            return all_models  # Team+ gets all models
    
    async def _get_user_custom_model(self, user_id: str) -> Optional[Dict]:
        """
        Check if user has custom trained model
        TODO: Query model registry
        """
        # Mock for now
        return None

