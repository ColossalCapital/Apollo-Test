"""
Test Apollo Smart API - Test all smart agent endpoints
"""

import asyncio
import httpx
import json


BASE_URL = "http://localhost:8002"


async def test_health():
    """Test health check"""
    print("\n" + "=" * 80)
    print("HEALTH CHECK")
    print("=" * 80)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        data = response.json()
        
        print(f"\n✅ Status: {data['status']}")
        print(f"📦 Version: {data['version']}")
        print(f"🤖 Total Agents: {data['agents']['total']}")
        print(f"  - Regular: {data['agents']['regular']}")
        print(f"  - Smart (LLM): {data['agents']['smart']}")
        print(f"🧠 Tier 2 Enabled: {data['tier2_enabled']}")


async def test_strategy_agent():
    """Test Smart Strategy Agent"""
    print("\n" + "=" * 80)
    print("SMART STRATEGY AGENT")
    print("=" * 80)
    
    # Test 1: Static mode (quick)
    print("\n📚 Test 1: Static Knowledge (quick_mode=True)")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/analyze/strategy_smart",
            json={
                "data": {
                    "type": "turtle_trading",
                    "quick_mode": True
                }
            }
        )
        data = response.json()
        print(f"  Mode: {data['mode']}")
        print(f"  Strategy: {data['knowledge']['strategy']}")
    
    # Test 2: LLM mode (smart)
    print("\n🧠 Test 2: LLM Analysis (with price data)")
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/analyze/strategy_smart",
            json={
                "data": {
                    "type": "turtle_trading",
                    "asset": "BTC",
                    "price_data": {
                        "current_price": 45000,
                        "20_day_high": 44500,
                        "atr": 2500
                    }
                }
            }
        )
        data = response.json()
        print(f"  Mode: {data['mode']}")
        
        if data['mode'] == 'llm_powered':
            llm = data['llm_analysis']
            print(f"  Recommendation: {llm.get('recommendation', 'N/A')}")
            print(f"  Position Size: {llm.get('position_size', 'N/A')} units")
            print(f"  Stop Loss: ${llm.get('stop_loss', 0):,.2f}")
            print(f"  Confidence: {llm.get('confidence', 0):.0%}")
        else:
            print(f"  ⚠️  LLM unavailable: {data.get('error', 'Unknown')}")


async def test_portfolio_agent():
    """Test Smart Portfolio Agent"""
    print("\n" + "=" * 80)
    print("SMART PORTFOLIO AGENT")
    print("=" * 80)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/analyze/portfolio_smart",
            json={
                "data": {
                    "type": "optimize",
                    "portfolio": {
                        "BTC": 0.4,
                        "ETH": 0.3,
                        "STOCKS": 0.2,
                        "BONDS": 0.1
                    },
                    "user_profile": {
                        "risk_tolerance": "moderate",
                        "investment_horizon": "medium",
                        "goals": ["growth", "preservation"]
                    }
                }
            }
        )
        data = response.json()
        print(f"\n  Mode: {data['mode']}")
        
        if data['mode'] == 'llm_powered':
            llm = data['llm_analysis']
            print(f"\n  Optimized Allocation:")
            for asset, weight in llm.get('optimized_allocation', {}).items():
                print(f"    {asset}: {weight*100:.1f}%")
            print(f"\n  Expected Return: {llm.get('expected_return', 0)*100:.1f}%")
            print(f"  Sharpe Ratio: {llm.get('sharpe_ratio', 0):.2f}")
            print(f"  Confidence: {llm.get('confidence', 0):.0%}")


async def test_sentiment_agent():
    """Test Smart Sentiment Agent"""
    print("\n" + "=" * 80)
    print("SMART SENTIMENT AGENT")
    print("=" * 80)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/analyze/sentiment_smart",
            json={
                "data": {
                    "asset": "BTC",
                    "news_headlines": [
                        "Bitcoin breaks $45,000 resistance level",
                        "Institutional adoption continues to grow",
                        "Major exchange reports record trading volume"
                    ],
                    "social_data": {
                        "twitter_sentiment": 0.75,
                        "reddit_mentions": 2500
                    }
                }
            }
        )
        data = response.json()
        print(f"\n  Mode: {data['mode']}")
        
        if data['mode'] == 'llm_powered':
            llm = data['llm_analysis']
            print(f"  Overall Sentiment: {llm.get('overall_sentiment', 'N/A')}")
            print(f"  Trading Signal: {llm.get('trading_signal', 'N/A')}")
            print(f"  Confidence: {llm.get('confidence', 0):.0%}")


async def test_backtest_agent():
    """Test Smart Backtest Agent"""
    print("\n" + "=" * 80)
    print("SMART BACKTEST AGENT")
    print("=" * 80)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/analyze/backtest_smart",
            json={
                "data": {
                    "backtest_results": {
                        "total_return": 0.45,
                        "sharpe_ratio": 1.2,
                        "max_drawdown": 0.18,
                        "win_rate": 0.58,
                        "profit_factor": 2.1
                    },
                    "strategy_params": {
                        "entry": "20-day high breakout",
                        "exit": "10-day low",
                        "stop_loss": "2 ATR"
                    }
                }
            }
        )
        data = response.json()
        print(f"\n  Mode: {data['mode']}")
        
        if data['mode'] == 'llm_powered':
            llm = data['llm_analysis']
            print(f"  Assessment: {llm.get('overall_assessment', 'N/A')}")
            print(f"  Grade: {llm.get('grade', 'N/A')}")
            
            if 'strengths' in llm:
                print(f"\n  Strengths:")
                for strength in llm['strengths'][:3]:
                    print(f"    ✓ {strength}")
            
            if 'improvement_suggestions' in llm:
                print(f"\n  Suggestions:")
                for suggestion in llm['improvement_suggestions'][:3]:
                    print(f"    → {suggestion}")


async def main():
    """Run all tests"""
    
    print("\n🚀 APOLLO SMART API TESTS\n")
    print("Make sure Apollo API is running:")
    print("  python api/main_smart.py")
    print("\nAnd llama.cpp server is running:")
    print("  ./llama-server -m phi-3-medium.gguf --port 8080")
    
    try:
        # Test health
        await test_health()
        
        # Test smart agents
        await test_strategy_agent()
        await test_portfolio_agent()
        await test_sentiment_agent()
        await test_backtest_agent()
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETE!")
        print("=" * 80)
        
    except httpx.ConnectError:
        print("\n❌ ERROR: Cannot connect to Apollo API")
        print("\nStart the API server:")
        print("  cd Apollo")
        print("  python api/main_smart.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")


if __name__ == "__main__":
    asyncio.run(main())
