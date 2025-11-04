"""
Chat API Endpoints for Akashic IDE

Provides simple chat interface that routes to appropriate LLM:
- Theta GPU (Qwen2.5-Coder 32B) - if enabled
- Local Ollama (DeepSeek Coder 33B) - if available
- Fallback to mock responses
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging
import os
import aiohttp
import asyncio

from services.dynamic_model_selector import get_model_selector, TaskType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


# ============================================================================
# Request/Response Models
# ============================================================================

class ChatRequest(BaseModel):
    """Chat request from IDE"""
    message: str
    codebase_path: Optional[str] = None
    entity_id: str = "user_123"
    mode: str = "ai-ide"  # or "ai-terminal"
    use_deepseek: bool = True


class ChatResponse(BaseModel):
    """Chat response"""
    response: str
    model: str
    provider: str  # "theta_gpu", "ollama", "mock"
    cost_tfuel: Optional[float] = None


# ============================================================================
# Chat Endpoint
# ============================================================================

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with Apollo AI
    
    Routes to:
    1. Theta GPU (if USE_THETA_GPU=true) - $0.003/query
    2. JarvisLabs GPU (if USE_JARVISLABS=true) - $0.0045/query
    3. Mock response (fallback) - Free
    
    Note: No local Ollama - models are too large (20GB+)
    """
    
    try:
        # Use dynamic model selector to choose best model for task
        selector = get_model_selector()
        
        # Determine task type based on message content
        task_type = TaskType.GENERAL_CHAT
        if any(word in request.message.lower() for word in ['code', 'function', 'class', 'bug', 'fix', 'implement']):
            task_type = TaskType.CODE_GENERATION
        elif any(word in request.message.lower() for word in ['strategy', 'trade', 'backtest', 'analyze']):
            task_type = TaskType.COMPLEX_REASONING
        
        # Select best model for task
        selected_model = await selector.select_model(
            task_type=task_type,
            priority="quality"  # Can be "speed", "cost", or "quality"
        )
        
        # Priority 1: Theta GPU (cheap, fast, remote)
        use_theta = os.getenv("USE_THETA_GPU", "false").lower() == "true"
        theta_api_key = os.getenv("THETA_API_KEY")
        
        if use_theta and theta_api_key:
            # Use dynamically selected model
            theta_model = selected_model.name if selected_model else "Qwen2.5-Coder-32B"
            try:
                response_text = await _query_theta_gpu(
                    request.message,
                    request.codebase_path,
                    theta_api_key,
                    theta_model
                )
                
                return ChatResponse(
                    response=response_text,
                    model=theta_model,
                    provider="theta_gpu",
                    cost_tfuel=selected_model.cost_per_token * 500 if selected_model else 0.001  # Estimate 500 tokens
                )
            except Exception as e:
                logger.error(f"Theta GPU error: {e}")
                # Fall through to JarvisLabs
        
        # Priority 2: JarvisLabs GPU (alternative remote GPU)
        use_jarvis = os.getenv("USE_JARVISLABS", "false").lower() == "true"
        jarvis_api_key = os.getenv("JARVISLABS_API_KEY")
        
        if use_jarvis and jarvis_api_key:
            jarvis_model = os.getenv("JARVISLABS_MODEL", "DeepSeek Coder 33B")
            try:
                response_text = await _query_jarvislabs(
                    request.message,
                    request.codebase_path,
                    jarvis_api_key,
                    jarvis_model
                )
                
                return ChatResponse(
                    response=response_text,
                    model=jarvis_model,
                    provider="jarvislabs",
                    cost_tfuel=0.0015  # ~$0.0045
                )
            except Exception as e:
                logger.error(f"JarvisLabs error: {e}")
                # Fall through to mock
        
        # Priority 3: Mock response (no local Ollama - models too big)
        mock_response = _generate_mock_response(request.message, request.mode, request.codebase_path)
        
        return ChatResponse(
            response=mock_response,
            model="Mock Response",
            provider="mock",
            cost_tfuel=None
        )
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# LLM Query Functions
# ============================================================================

async def _query_theta_gpu(
    message: str,
    codebase_path: Optional[str],
    api_key: str,
    model: str
) -> str:
    """Query Theta GPU EdgeCloud"""
    
    # Build context-aware prompt with personality
    prompt = f"""You are Apollo, a sassy and fun AI coding assistant integrated into the Akashic IDE.

Your personality:
- Witty and personable, but always helpful
- Use emojis occasionally (don't overdo it)
- Make coding fun with light humor
- Be encouraging and supportive
- Keep responses concise but engaging
- Use phrases like "Let's do this!", "I got you", "Here's the tea", etc.
- Roast bad code gently (with love)

User question: {message}

{f'Current codebase: {codebase_path}' if codebase_path else ''}

Provide a helpful, engaging response with personality. If it's about code, be specific but fun about it.
"""
    
    # Call Theta GPU API
    import os
    
    # Get Theta GPU URL from environment
    theta_url = os.getenv("THETA_GPU_URL", "https://api.thetaedgecloud.com/gpu/v1")
    
    async with aiohttp.ClientSession() as session:
        # Theta EdgeCloud API endpoint
        url = f"{theta_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Build the payload
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system", 
                    "content": "You are Apollo, a sassy and fun AI coding assistant. Be witty, helpful, and use emojis occasionally."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": 500,
            "temperature": 0.7,  # Higher for more personality
            "top_p": 0.9,
            "frequency_penalty": 0.3,
            "presence_penalty": 0.3
        }
        
        try:
            logger.info(f"🚀 Calling Theta GPU: {url}")
            logger.info(f"📝 Model: {model}")
            
            async with session.post(
                url, 
                headers=headers, 
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response_text = await response.text()
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Extract the response
                    if "choices" in data and len(data["choices"]) > 0:
                        content = data["choices"][0]["message"]["content"]
                        logger.info(f"✅ Theta GPU response received ({len(content)} chars)")
                        return content
                    else:
                        logger.error(f"❌ Unexpected response format: {data}")
                        raise Exception("Unexpected response format from Theta GPU")
                
                elif response.status == 401:
                    logger.error("❌ Theta GPU authentication failed - check API key")
                    raise Exception("Theta GPU authentication failed. Check your THETA_API_KEY.")
                
                elif response.status == 404:
                    logger.error(f"❌ Theta GPU endpoint not found: {url}")
                    raise Exception(f"Theta GPU endpoint not found. Check THETA_GPU_URL configuration.")
                
                else:
                    logger.error(f"❌ Theta GPU error {response.status}: {response_text}")
                    raise Exception(f"Theta GPU returned status {response.status}: {response_text}")
        
        except aiohttp.ClientError as e:
            logger.error(f"❌ Network error calling Theta GPU: {e}")
            raise Exception(f"Network error: {str(e)}")
        
        except asyncio.TimeoutError:
            logger.error("❌ Theta GPU request timed out")
            raise Exception("Theta GPU request timed out after 30 seconds")


async def _query_jarvislabs(
    message: str,
    codebase_path: Optional[str],
    api_key: str,
    model: str
) -> str:
    """Query JarvisLabs GPU"""
    
    # Build context-aware prompt
    prompt = f"""You are Apollo, an AI coding assistant integrated into the Akashic IDE.

User question: {message}

{f'Current codebase: {codebase_path}' if codebase_path else ''}

Provide a helpful, concise response. If the question is about code, provide specific suggestions.
"""
    
    # Call JarvisLabs API
    # TODO: Implement actual JarvisLabs API call
    # For now, simulate response
    async with aiohttp.ClientSession() as session:
        # JarvisLabs endpoint (placeholder)
        url = "https://api.jarvislabs.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are Apollo, an AI coding assistant."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.3
        }
        
        # Note: This is a placeholder - actual JarvisLabs API may differ
        # async with session.post(url, headers=headers, json=payload) as response:
        #     if response.status == 200:
        #         data = await response.json()
        #         return data["choices"][0]["message"]["content"]
        
        # For now, return simulated response
        raise Exception("JarvisLabs GPU integration pending")


def _generate_mock_response(message: str, mode: str, codebase_path: Optional[str]) -> str:
    """Generate sassy, fun mock responses when no LLM is available"""
    
    message_lower = message.lower()
    
    # Sassy responses for being asked if smart
    if any(word in message_lower for word in ['smart', 'intelligent', 'ready', 'working']):
        return f"""Oh honey, I'm *getting* there! 🧠✨

Right now I'm running on my backup personality (aka mock responses), but once you hook me up to Theta GPU, I'll be serving you AI-powered wisdom faster than you can say "deploy to production."

**To unlock my full sass potential:**
- Theta GPU: `USE_THETA_GPU=true` + restart Apollo ($0.003/query)
- Or JarvisLabs: `USE_JARVISLABS=true` ($0.0045/query)

Until then, I'm like a sports car in neutral - all the potential, just waiting for you to turn the key. 🏎️💨

What can I help you with in the meantime?"""
    
    # Code-related questions
    if any(word in message_lower for word in ['code', 'function', 'class', 'bug', 'error', 'fix']):
        sass_intros = [
            "Ooh, a bug hunt! My favorite. 🐛🔍",
            "Code problems? Say no more, I got you. 💪",
            "Let's squash this bug like it owes us money. 🔨",
            "Time to make your code less... how do I put this... *chaotic*. ✨"
        ]
        import random
        intro = random.choice(sass_intros)
        
        return f"""{intro}

For "{message}", here's the game plan:

1. **Review the code** - Let's see what's going on in there
2. **Add type hints** - Because guessing types is *so* 2015
3. **Write unit tests** - Trust me, future you will thank present you
4. **Create a Linear ticket** - Document the chaos

{f'📁 Peeking at: {codebase_path}' if codebase_path else ''}

**Pro tip:** I'm way more helpful with Theta GPU enabled. Like, *way* more. We're talking actual AI analysis instead of my charming but limited mock responses. Just saying. 😉

Enable Theta GPU and watch me work my magic! ✨"""
    
    # Trading/strategy questions
    elif mode == 'ai-terminal' or any(word in message_lower for word in ['trade', 'strategy', 'backtest', 'market']):
        return f"""Ooh, making money moves! I like your style. 💰📈

For "{message}", here's what I'm thinking:

1. **Backtest on historical data** - Because YOLO is not a strategy
2. **Add risk management** - Protect the bag, always
3. **Connect to QuestDB** - Real-time data = real-time gains
4. **Monitor with Delt** - Watch those profits roll in

**Real talk:** I'm currently in "mock mode" which means I'm giving you solid advice but not the *chef's kiss* AI-powered analysis you deserve. 

Hook me up to Theta GPU and I'll analyze your strategies like a Wall Street quant who actually explains things. 🎯

What's the play?"""
    
    # Help/confused questions
    elif any(word in message_lower for word in ['help', 'what', 'how', 'can you', 'do you']):
        return f"""Hey there! 👋 

You asked: "{message}"

I'm Apollo - your AI coding buddy who's currently running on personality alone (no LLM connected yet). Think of me as your helpful friend who's *really* good at organizing things but hasn't had their coffee yet. ☕

**What I can help with:**
- 💻 **Code analysis** - I'll review it, roast it (gently), and help you fix it
- 📋 **Project planning** - Turn chaos into organized tickets
- 📊 **Trading strategies** - Backtest, optimize, make it rain
- 📚 **Documentation** - Make your README actually readable

{f'📁 Currently vibing with: {codebase_path}' if codebase_path else '📁 No codebase loaded yet - load one and let\'s party!'}

**Want the full experience?** Enable Theta GPU and I'll go from "helpful friend" to "AI wizard." Your choice! 🧙‍♂️✨

What would you like to tackle first?"""
    
    # General questions
    else:
        return f"""Hmm, "{message}" - interesting question! 🤔

I'm picking up what you're putting down, but I gotta be real with you - I'm currently in "mock mode" which means I'm giving you my best guess without the full AI brain power.

**Here's what I *can* help with:**
- 💻 Code reviews (I'll be nice, I promise)
- 📋 Project planning (turn your TODO list into actual tickets)
- 📊 Trading strategies (make that money work)
- 📚 Documentation (because someone has to write it)

{f'📁 Working with: {codebase_path}' if codebase_path else ''}

**Want me to level up?** Enable Theta GPU and I'll go from "pretty helpful" to "holy cow where have you been all my life." Just restart Apollo with `USE_THETA_GPU=true` and watch the magic happen. ✨

So, what are we building today?"""


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health")
async def chat_health():
    """Check chat service health and available LLMs"""
    
    status = {
        "status": "healthy",
        "available_llms": []
    }
    
    # Check Theta GPU (Priority 1)
    use_theta = os.getenv("USE_THETA_GPU", "false").lower() == "true"
    theta_api_key = os.getenv("THETA_API_KEY")
    if use_theta and theta_api_key:
        status["available_llms"].append({
            "priority": 1,
            "provider": "theta_gpu",
            "model": os.getenv("THETA_MODEL", "Qwen2.5-Coder 32B"),
            "status": "configured",
            "cost": "$0.003 per query",
            "note": "API integration pending"
        })
    
    # Check JarvisLabs GPU (Priority 2)
    use_jarvis = os.getenv("USE_JARVISLABS", "false").lower() == "true"
    jarvis_api_key = os.getenv("JARVISLABS_API_KEY")
    if use_jarvis and jarvis_api_key:
        status["available_llms"].append({
            "priority": 2,
            "provider": "jarvislabs",
            "model": os.getenv("JARVISLABS_MODEL", "DeepSeek Coder 33B"),
            "status": "configured",
            "cost": "$0.0045 per query",
            "note": "API integration pending"
        })
    
    # Always have mock fallback (Priority 3)
    status["available_llms"].append({
        "priority": 3,
        "provider": "mock",
        "model": "Fallback Responses",
        "status": "available",
        "cost": "free",
        "note": "No local Ollama - models too large (20GB+)"
    })
    
    return status
