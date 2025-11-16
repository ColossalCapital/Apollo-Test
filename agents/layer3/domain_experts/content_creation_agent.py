"""
Content Creation Agent - LLM-Powered Content Generation

Layer 3 Domain Expert agent that generates marketing content, blog posts,
and social media content.
"""

from typing import Dict, Any
from ...base import Layer3Agent, AgentResult, AgentMetadata, AgentLayer
import httpx
import json


class ContentCreationAgent(Layer3Agent):
    """
    Content Creation Agent - LLM-powered content generation
    
    Provides:
    - Blog post generation
    - Social media content
    - Email campaigns
    - Product descriptions
    - SEO optimization
    """
    
    def __init__(self, kg_client=None):
        super().__init__(kg_client)
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _get_metadata(self) -> AgentMetadata:
        return AgentMetadata(
            name="content_creation",
            layer=AgentLayer.LAYER_3_DOMAIN_EXPERT,
            version="1.0.0",
            description="LLM-powered content creation for marketing and social media",
            capabilities=[
                "blog_post_generation",
                "social_media_content",
                "email_campaigns",
                "product_descriptions",
                "seo_optimization"
            ],
            dependencies=["knowledge_graph"]
        )
    
    async def analyze(self, domain_data: Dict[str, Any]) -> AgentResult:
        """Generate content based on requirements"""
        
        content_type = domain_data.get('content_type', 'blog_post')
        topic = domain_data.get('topic', '')
        tone = domain_data.get('tone', 'professional')
        length = domain_data.get('length', 'medium')
        
        prompt = f"""You are an expert content creator. Generate {content_type} content.

REQUIREMENTS:
Topic: {topic}
Tone: {tone}
Length: {length}
Target Audience: {domain_data.get('audience', 'general')}
Keywords: {domain_data.get('keywords', [])}

GENERATE:
1. Compelling headline/title
2. Main content (optimized for {content_type})
3. Call-to-action
4. SEO metadata (title, description, keywords)
5. Social media snippets (Twitter, LinkedIn, Facebook)
6. Hashtag suggestions

Return as JSON with complete content package.
"""
        
        try:
            response = await self.client.post(
                f"{self.llm_url}/v1/chat/completions",
                json={
                    "model": "phi-3-medium",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 3000
                }
            )
            
            llm_response = response.json()
            content = json.loads(llm_response['choices'][0]['message']['content'])
            
            if self.kg_client:
                await self._store_content_in_kg(content)
            
            return AgentResult(
                success=True,
                data=content,
                metadata={'agent': self.metadata.name, 'content_type': content_type}
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data={},
                metadata={'agent': self.metadata.name, 'error': str(e)}
            )
    
    async def _store_content_in_kg(self, content: Dict[str, Any]):
        """Store generated content in knowledge graph"""
        if not self.kg_client:
            return
        
        await self.kg_client.create_entity(
            entity_type="generated_content",
            data=content,
            graph_type="business"
        )
