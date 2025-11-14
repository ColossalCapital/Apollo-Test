#!/usr/bin/env python3
"""
Sync Atlas frontend agent IDs with Apollo backend agent files.
Creates missing agents to ensure 1:1 mapping.
"""

# Atlas frontend agent IDs (from apolloAgents.ts)
atlas_agents = [
    # Finance (20)
    'ledger', 'tax', 'invoice', 'budget', 'trading', 'forex', 'stocks', 'options',
    'futures', 'arbitrage', 'sentiment', 'backtest', 'broker_ib', 'broker_td',
    'broker_schwab', 'broker_alpaca', 'exchange_binance', 'exchange_coinbase',
    'exchange_kraken', 'portfolio', 'strategy',
    # Communication (5)
    'email', 'calendar', 'slack', 'teams', 'contact',
    # Development (4)
    'code', 'github', 'devops', 'api',
    # Documents (9)
    'document', 'pdf', 'ocr', 'notion', 'drive', 'knowledge', 'wiki', 'research', 'translation',
    # Legal (4)
    'legal', 'contract', 'compliance', 'ip',
    # Business (9)
    'grant', 'sales', 'marketing', 'hr', 'crm', 'analytics', 'business_strategy',
    'operations', 'project', 'travel', 'charity',
    # Health (2)
    'health', 'nutrition',
    # Insurance (3)
    'insurance', 'claims', 'risk',
    # Media (6)
    'image', 'video', 'audio', 'content', 'vision', 'music',
    # Analytics (9)
    'data', 'metrics', 'forecast', 'report', 'ml', 'text', 'schema', 'router', 'materialize',
    # Modern (3)
    'slang', 'meme', 'social',
    # Web (4)
    'web', 'seo', 'scraper', 'integration',
    # Web3 (5)
    'blockchain', 'nft', 'defi', 'crypto', 'auction',
]

# Apollo backend agents (actual files)
apollo_agents = [
    # Finance
    'ledger', 'tax', 'invoice', 'budget', 'trading', 'forex', 'stocks',
    'broker', 'exchange', 'strategy', 'portfolio', 'options', 'futures',
    'arbitrage', 'sentiment', 'backtest',
    # Communication
    'email', 'calendar', 'contact', 'slack',
    # Development
    'github', 'codereview', 'deployment', 'api',
    # Documents
    'document', 'knowledge', 'wiki', 'research', 'translation',
    # Legal
    'legal', 'contract', 'compliance', 'ip',
    # Business
    'grant', 'sales', 'marketing', 'hr', 'project', 'strategy', 'travel', 'charity',
    # Health
    'health', 'nutrition',
    # Insurance
    'insurance', 'risk',
    # Media
    'vision', 'audio', 'video', 'music',
    # Analytics
    'data', 'text', 'schema', 'router', 'materialize',
    # Modern
    'slang', 'meme', 'social',
    # Web
    'scraper', 'integration',
    # Web3
    'crypto', 'nft', 'auction',
]

# Recently created
recently_created = [
    'teams', 'pdf', 'ocr', 'crm', 'analytics', 'operations', 'claims', 'image',
]

print("=" * 80)
print("ATLAS → APOLLO AGENT SYNC ANALYSIS")
print("=" * 80)
print(f"\nAtlas Frontend: {len(atlas_agents)} agents")
print(f"Apollo Backend: {len(apollo_agents)} agents")
print(f"Recently Created: {len(recently_created)} agents")

# Find missing agents
missing = []
for agent in atlas_agents:
    if agent not in apollo_agents and agent not in recently_created:
        missing.append(agent)

print(f"\n{'='*80}")
print(f"MISSING AGENTS IN APOLLO: {len(missing)}")
print(f"{'='*80}")

if missing:
    for agent in sorted(missing):
        print(f"  ❌ {agent}")
else:
    print("  ✅ All agents present!")

# Find agents to rename/consolidate
print(f"\n{'='*80}")
print("AGENTS TO RENAME/CONSOLIDATE:")
print(f"{'='*80}")

renames = {
    'codereview': 'code',
    'deployment': 'devops',
    'broker': ['broker_ib', 'broker_td', 'broker_schwab', 'broker_alpaca'],
    'exchange': ['exchange_binance', 'exchange_coinbase', 'exchange_kraken'],
}

for old_name, new_names in renames.items():
    if isinstance(new_names, list):
        print(f"  🔄 {old_name} → {', '.join(new_names)} (split into specific agents)")
    else:
        print(f"  🔄 {old_name} → {new_names}")

print(f"\n{'='*80}")
print("ACTION PLAN:")
print(f"{'='*80}")
print(f"1. Create {len(missing)} missing agents")
print(f"2. Rename 2 agents (codereview→code, deployment→devops)")
print(f"3. Split broker into 4 specific agents")
print(f"4. Split exchange into 3 specific agents")
print(f"5. Remove AGENT_ALIASES (no longer needed)")
print(f"6. Update AGENT_REGISTRY with 1:1 mapping")
