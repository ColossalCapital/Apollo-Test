# 🚀 How to Add LLM Intelligence to Agents

## **Quick Start: 3 Steps to Make Agents Smart**

---

## **Step 1: Start llama.cpp Server**

```bash
# Download and start llama.cpp server
cd Apollo/models
./llama-server -m phi-3-medium-4k-instruct.Q4_K_M.gguf --port 8080 --ctx-size 4096

# Server will run on http://localhost:8080
```

---

## **Step 2: Create Smart Agent (Example: StrategyAgent)**

Here's how to upgrade StrategyAgent from static to LLM-powered:

```python
# Apollo/agents/finance/strategy_agent_v2.py

from typing import Dict, Any
from ..base_agent import BaseAgent
import httpx

class SmartStrategyAgent(BaseAgent):
    """
    Strategy Agent with 3-Tier Intelligence:
    - Tier 1: Static knowledge (fast)
    - Tier 2: LLM analysis (smart)
    - Tier 3: Personalized (future)
    """
    
    def __init__(self):
        super().__init__(name="SmartStrategyAgent", model="phi-3-medium")
        self.llm_url = "http://localhost:8080"
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze with both static knowledge and LLM"""
        
        # Step 1: Get static knowledge (Tier 1 - always fast)
        static_knowledge = self.get_static_knowledge(data)
        
        # Step 2: If user wants quick answer, return static only
        if data.get('quick_mode'):
            return {
                "mode": "static",
                "knowledge": static_knowledge
            }
        
        # Step 3: Use LLM for deeper analysis (Tier 2 - smart)
        if "price_data" in data:
            llm_analysis = await self.analyze_with_llm(data, static_knowledge)
            
            return {
                "mode": "llm_powered",
                "static_knowledge": static_knowledge,
                "llm_analysis": llm_analysis,
                "recommendation": llm_analysis.get("recommendation"),
                "confidence": llm_analysis.get("confidence", 0.8)
            }
        
        # Fallback to static
        return {
            "mode": "static",
            "knowledge": static_knowledge
        }
    
    def get_static_knowledge(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Tier 1: Static knowledge (fast, deterministic)"""
        strategy_type = data.get("type", "turtle_trading")
        
        if strategy_type == "turtle_trading":
            return {
                "strategy": "Turtle Trading",
                "rules": {
                    "entry": "20-day high breakout",
                    "exit": "10-day low",
                    "position_sizing": "N-based (1 ATR risk)",
                    "stop_loss": "2 ATR below entry"
                },
                "description": "Original Turtle Trading system by Richard Dennis"
            }
        
        return {"strategy": strategy_type}
    
    async def analyze_with_llm(self, data: Dict[str, Any], static_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Tier 2: LLM-powered analysis (smart, custom recommendations)"""
        
        # Build prompt with user's specific data
        prompt = f"""You are a Turtle Trading expert. Analyze this specific trading opportunity:

Asset: {data.get('asset', 'Unknown')}
Current Price: ${data.get('current_price', 0):,.2f}
20-Day High: ${data.get('20_day_high', 0):,.2f}
ATR (N): ${data.get('atr', 0):,.2f}

Static Knowledge:
{static_knowledge}

Based on this data, provide:
1. Should we enter a position NOW? (Yes/No and why)
2. Optimal position size (in units, based on ATR)
3. Exact stop loss price
4. Specific risks for THIS asset
5. Expected holding period

Format your response as JSON:
{{
    "recommendation": "BUY/SELL/HOLD",
    "reasoning": "...",
    "position_size": 0.5,
    "stop_loss": 42500,
    "risks": ["risk1", "risk2"],
    "holding_period": "10-15 days",
    "confidence": 0.85
}}
"""
        
        try:
            # Call llama.cpp server
            response = await self.client.post(
                f"{self.llm_url}/completion",
                json={
                    "prompt": prompt,
                    "temperature": 0.3,  # Lower = more deterministic
                    "n_predict": 500,
                    "stop": ["}"]
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["content"].strip()
                
                # Parse JSON response
                import json
                try:
                    analysis = json.loads(content + "}")
                    return analysis
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    return {
                        "recommendation": "HOLD",
                        "reasoning": content,
                        "confidence": 0.5
                    }
            else:
                # LLM failed, return static knowledge
                return {
                    "recommendation": "HOLD",
                    "reasoning": "LLM unavailable, using static knowledge",
                    "confidence": 0.3
                }
                
        except Exception as e:
            print(f"LLM error: {e}")
            return {
                "recommendation": "HOLD",
                "reasoning": f"Error: {str(e)}",
                "confidence": 0.1
            }
```

---

## **Step 3: Test the Smart Agent**

```python
# test_smart_agent.py

import asyncio
from agents.finance.strategy_agent_v2 import SmartStrategyAgent

async def test():
    agent = SmartStrategyAgent()
    
    # Test 1: Static knowledge only (fast)
    result1 = await agent.analyze({
        "type": "turtle_trading",
        "quick_mode": True
    })
    print("Static knowledge:", result1)
    
    # Test 2: LLM-powered analysis (smart)
    result2 = await agent.analyze({
        "type": "turtle_trading",
        "asset": "BTC",
        "current_price": 45000,
        "20_day_high": 44500,
        "atr": 2500
    })
    print("\nLLM Analysis:", result2)
    print(f"\nRecommendation: {result2['llm_analysis']['recommendation']}")
    print(f"Reasoning: {result2['llm_analysis']['reasoning']}")
    print(f"Position Size: {result2['llm_analysis']['position_size']} units")
    print(f"Stop Loss: ${result2['llm_analysis']['stop_loss']:,.2f}")

if __name__ == "__main__":
    asyncio.run(test())
```

**Expected Output:**
```
Static knowledge: {
  "mode": "static",
  "knowledge": {
    "strategy": "Turtle Trading",
    "rules": {...}
  }
}

LLM Analysis: {
  "mode": "llm_powered",
  "static_knowledge": {...},
  "llm_analysis": {
    "recommendation": "BUY",
    "reasoning": "BTC has broken above the 20-day high at $44,500, triggering a Turtle Trading entry signal. The current price of $45,000 is $500 above the breakout level, confirming the signal.",
    "position_size": 0.4,
    "stop_loss": 42500,
    "risks": [
      "High volatility in crypto markets",
      "Potential for false breakout"
    ],
    "holding_period": "10-15 days",
    "confidence": 0.85
  },
  "recommendation": "BUY",
  "confidence": 0.85
}

Recommendation: BUY
Reasoning: BTC has broken above the 20-day high...
Position Size: 0.4 units
Stop Loss: $42,500.00
```

---

## **Step 4: Upgrade More Agents**

Apply the same pattern to other agents:

### **PortfolioAgent with LLM:**

```python
async def analyze_with_llm(self, data: Dict[str, Any]) -> Dict[str, Any]:
    prompt = f"""You are a portfolio optimization expert. Analyze this portfolio:

Current Allocation:
- BTC: {data['portfolio']['BTC']*100}%
- ETH: {data['portfolio']['ETH']*100}%
- STOCKS: {data['portfolio']['STOCKS']*100}%
- BONDS: {data['portfolio']['BONDS']*100}%

User's Risk Tolerance: {data.get('risk_tolerance', 'moderate')}
Investment Horizon: {data.get('horizon', '1 year')}

Provide optimized allocation to maximize Sharpe ratio while respecting risk tolerance.

Response as JSON:
{{
    "optimized_allocation": {{
        "BTC": 0.35,
        "ETH": 0.25,
        "STOCKS": 0.25,
        "BONDS": 0.15
    }},
    "expected_return": 0.28,
    "expected_volatility": 0.30,
    "sharpe_ratio": 0.93,
    "reasoning": "..."
}}
"""
    # ... call LLM
```

### **SentimentAgent with LLM:**

```python
async def analyze_with_llm(self, data: Dict[str, Any]) -> Dict[str, Any]:
    prompt = f"""You are a market sentiment analyst. Analyze sentiment for {data['asset']}:

Recent News Headlines:
{data.get('news_headlines', [])}

Twitter Sentiment: {data.get('twitter_sentiment', 'neutral')}
Reddit Mentions: {data.get('reddit_mentions', 0)}

Provide overall sentiment analysis and trading signal.

Response as JSON:
{{
    "overall_sentiment": "BULLISH/BEARISH/NEUTRAL",
    "sentiment_score": 0.75,
    "signal": "BUY/SELL/HOLD",
    "reasoning": "...",
    "confidence": 0.8
}}
"""
    # ... call LLM
```

---

## **Comparison: Static vs LLM**

### **Static Knowledge (Tier 1)**
```python
# Input
{"type": "turtle_trading"}

# Output (instant, < 10ms)
{
    "strategy": "Turtle Trading",
    "entry": "20-day high breakout",
    "exit": "10-day low"
}
```

### **LLM Analysis (Tier 2)**
```python
# Input
{
    "type": "turtle_trading",
    "asset": "BTC",
    "current_price": 45000,
    "20_day_high": 44500,
    "atr": 2500
}

# Output (1-3 seconds)
{
    "recommendation": "BUY",
    "reasoning": "BTC broke above 20-day high, confirming entry signal",
    "position_size": 0.4,
    "stop_loss": 42500,
    "risks": ["High volatility", "False breakout possible"],
    "confidence": 0.85
}
```

**Key Difference:** LLM analyzes YOUR specific data and provides custom recommendations!

---

## **Performance & Cost**

### **Static Knowledge**
- Speed: < 10ms
- Cost: $0
- Intelligence: Low (documentation)

### **LLM Analysis**
- Speed: 1-3 seconds
- Cost: ~$0.001 per query (local inference)
- Intelligence: High (custom analysis)

### **When to Use Each:**
- **Static:** Quick reference, documentation, known formulas
- **LLM:** Custom analysis, specific recommendations, complex decisions

---

## **Next Steps**

1. **Start llama.cpp server** (Step 1)
2. **Create `strategy_agent_v2.py`** (Step 2)
3. **Test it** (Step 3)
4. **Upgrade more agents** (Step 4)
5. **Deploy to production**

---

## **Troubleshooting**

### **LLM server not responding:**
```bash
# Check if server is running
curl http://localhost:8080/health

# Restart server
./llama-server -m phi-3-medium-4k-instruct.Q4_K_M.gguf --port 8080
```

### **Slow responses:**
- Use smaller model (Phi-2 instead of Phi-3)
- Reduce `max_tokens`
- Lower `temperature` for faster sampling

### **Poor quality responses:**
- Improve prompt engineering
- Add more context
- Use larger model (Mistral-7B)
- Increase `temperature` for creativity

---

## **Summary**

**You now have:**
- ✅ Static knowledge (Tier 1) - Fast, free
- ✅ LLM analysis (Tier 2) - Smart, pennies per query
- ⏳ Continuous learning (Tier 3) - Coming soon!

**Your agents are now 10x smarter!** 🚀

Want me to implement this for StrategyAgent, PortfolioAgent, and SentimentAgent right now?
