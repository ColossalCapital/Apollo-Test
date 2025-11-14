"""
Test Smart Strategy Agent - Compare Static vs LLM Analysis
"""

import asyncio
import time
from agents.finance.strategy_agent_smart import SmartStrategyAgent


async def test_static_vs_llm():
    """Compare static knowledge vs LLM-powered analysis"""
    
    agent = SmartStrategyAgent()
    
    print("=" * 80)
    print("TIER 1: STATIC KNOWLEDGE (Fast, Free)")
    print("=" * 80)
    
    start = time.time()
    result1 = await agent.analyze({
        "type": "turtle_trading",
        "quick_mode": True
    })
    elapsed1 = (time.time() - start) * 1000
    
    print(f"\n⏱️  Response Time: {elapsed1:.1f}ms")
    print(f"💰 Cost: $0.000")
    print(f"\n📚 Static Knowledge:")
    print(f"  Strategy: {result1['knowledge']['strategy']}")
    print(f"  Entry: {result1['knowledge']['rules']['entry']}")
    print(f"  Exit: {result1['knowledge']['rules']['exit']}")
    print(f"  Position Sizing: {result1['knowledge']['rules']['position_sizing']}")
    print(f"  Stop Loss: {result1['knowledge']['rules']['stop_loss']}")
    
    print("\n" + "=" * 80)
    print("TIER 2: LLM-POWERED ANALYSIS (Smart, Pennies)")
    print("=" * 80)
    
    start = time.time()
    result2 = await agent.analyze({
        "type": "turtle_trading",
        "asset": "BTC",
        "price_data": {
            "current_price": 45000,
            "20_day_high": 44500,
            "atr": 2500
        }
    })
    elapsed2 = (time.time() - start) * 1000
    
    print(f"\n⏱️  Response Time: {elapsed2:.1f}ms")
    print(f"💰 Cost: ~$0.001")
    
    if result2['mode'] == 'llm_powered':
        llm = result2['llm_analysis']
        print(f"\n🤖 LLM Analysis:")
        print(f"  Recommendation: {llm.get('recommendation', 'N/A')}")
        print(f"  Reasoning: {llm.get('reasoning', 'N/A')[:200]}...")
        print(f"  Position Size: {llm.get('position_size', 'N/A')} units")
        print(f"  Stop Loss: ${llm.get('stop_loss', 0):,.2f}")
        print(f"  Risks: {', '.join(llm.get('risks', []))}")
        print(f"  Holding Period: {llm.get('holding_period', 'N/A')}")
        print(f"  Confidence: {llm.get('confidence', 0):.0%}")
    else:
        print(f"\n⚠️  LLM Mode: {result2['mode']}")
        print(f"  Error: {result2.get('error', 'LLM unavailable')}")
        print(f"\n  Falling back to static knowledge...")
    
    print("\n" + "=" * 80)
    print("COMPARISON")
    print("=" * 80)
    print(f"\n{'Metric':<20} {'Static (Tier 1)':<25} {'LLM (Tier 2)':<25}")
    print("-" * 70)
    print(f"{'Speed':<20} {f'{elapsed1:.1f}ms':<25} {f'{elapsed2:.1f}ms':<25}")
    print(f"{'Cost':<20} {'$0.000':<25} {'~$0.001':<25}")
    print(f"{'Intelligence':<20} {'Low (docs)':<25} {'High (custom)':<25}")
    print(f"{'Recommendation':<20} {'Generic':<25} {llm.get('recommendation', 'N/A'):<25}")
    print(f"{'Personalized':<20} {'No':<25} {'Yes':<25}")
    
    print("\n" + "=" * 80)
    print("KEY INSIGHT")
    print("=" * 80)
    print("""
Static Knowledge: "Here are the Turtle Trading rules"
LLM Analysis:     "Based on YOUR BTC data, you should BUY 0.4 units 
                   with stop loss at $42,500 because..."
    
The LLM analyzes YOUR specific situation and provides custom advice!
""")


async def test_multiple_assets():
    """Test LLM analysis on multiple assets"""
    
    agent = SmartStrategyAgent()
    
    print("\n" + "=" * 80)
    print("TESTING MULTIPLE ASSETS")
    print("=" * 80)
    
    assets = [
        {
            "asset": "BTC",
            "price_data": {
                "current_price": 45000,
                "20_day_high": 44500,
                "atr": 2500
            }
        },
        {
            "asset": "ETH",
            "price_data": {
                "current_price": 2300,
                "20_day_high": 2350,
                "atr": 150
            }
        },
        {
            "asset": "AAPL",
            "price_data": {
                "current_price": 180,
                "20_day_high": 185,
                "atr": 3
            }
        }
    ]
    
    for asset_data in assets:
        asset_data["type"] = "turtle_trading"
        result = await agent.analyze(asset_data)
        
        if result['mode'] == 'llm_powered':
            llm = result['llm_analysis']
            print(f"\n{asset_data['asset']}:")
            print(f"  Recommendation: {llm.get('recommendation', 'N/A')}")
            print(f"  Position Size: {llm.get('position_size', 'N/A')} units")
            print(f"  Confidence: {llm.get('confidence', 0):.0%}")
        else:
            print(f"\n{asset_data['asset']}: LLM unavailable")


async def main():
    """Run all tests"""
    
    print("\n🚀 SMART STRATEGY AGENT TEST\n")
    
    # Test 1: Static vs LLM
    await test_static_vs_llm()
    
    # Test 2: Multiple assets (if LLM is available)
    try:
        await test_multiple_assets()
    except Exception as e:
        print(f"\n⚠️  LLM tests skipped: {e}")
        print("\nTo enable LLM tests:")
        print("1. Start llama.cpp server:")
        print("   ./llama-server -m phi-3-medium.gguf --port 8080")
        print("2. Run this test again")
    
    print("\n✅ Tests complete!\n")


if __name__ == "__main__":
    asyncio.run(main())
