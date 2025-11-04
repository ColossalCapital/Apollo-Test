"""
Test Agent Alias Mapping
Verifies that frontend agent IDs correctly route to backend agents
"""

from agents import get_agent, AGENT_ALIASES, AGENT_REGISTRY


def test_alias_resolution():
    """Test that aliases resolve to correct backend agents"""
    print("Testing Agent Alias Resolution...\n")
    
    test_cases = [
        # (frontend_id, expected_backend_agent_name)
        ('broker_ib', 'Broker Agent'),
        ('broker_td', 'Broker Agent'),
        ('exchange_binance', 'Exchange Agent'),
        ('exchange_coinbase', 'Exchange Agent'),
        ('code', 'Code Review Agent'),
        ('devops', 'Deployment Agent'),
        ('pdf', 'Document Agent'),
        ('crm', 'Sales Agent'),
        ('image', 'Vision Agent'),
        ('blockchain', 'Crypto Agent'),
        ('teams', 'Slack Agent'),
    ]
    
    passed = 0
    failed = 0
    
    for frontend_id, expected_name in test_cases:
        try:
            agent = get_agent(frontend_id)
            if agent.name == expected_name:
                print(f"✅ {frontend_id} -> {agent.name}")
                passed += 1
            else:
                print(f"❌ {frontend_id} -> Expected '{expected_name}', got '{agent.name}'")
                failed += 1
        except Exception as e:
            print(f"❌ {frontend_id} -> Error: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*50}\n")
    
    return failed == 0


def test_direct_agents():
    """Test that direct agent IDs still work"""
    print("Testing Direct Agent Access...\n")
    
    test_cases = [
        ('ledger', 'Ledger Agent'),
        ('email', 'Email Agent'),
        ('github', 'GitHub Agent'),
        ('legal', 'Legal Agent'),
        ('health', 'Health Agent'),
    ]
    
    passed = 0
    failed = 0
    
    for agent_id, expected_name in test_cases:
        try:
            agent = get_agent(agent_id)
            if agent.name == expected_name:
                print(f"✅ {agent_id} -> {agent.name}")
                passed += 1
            else:
                print(f"❌ {agent_id} -> Expected '{expected_name}', got '{agent.name}'")
                failed += 1
        except Exception as e:
            print(f"❌ {agent_id} -> Error: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*50}\n")
    
    return failed == 0


def test_connector_agents():
    """Test that connector agents work"""
    print("Testing Connector Agents...\n")
    
    test_cases = [
        ('ib_connector', 'IB Connector'),
        ('connection_monitor', 'Connection Monitor'),
        ('rate_limit_manager', 'Rate Limit Manager'),
    ]
    
    passed = 0
    failed = 0
    
    for agent_id, expected_name in test_cases:
        try:
            agent = get_agent(agent_id)
            if agent.name == expected_name:
                print(f"✅ {agent_id} -> {agent.name}")
                passed += 1
            else:
                print(f"❌ {agent_id} -> Expected '{expected_name}', got '{agent.name}'")
                failed += 1
        except Exception as e:
            print(f"❌ {agent_id} -> Error: {e}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*50}\n")
    
    return failed == 0


def print_summary():
    """Print summary of alias mappings"""
    print("\n" + "="*70)
    print("AGENT ALIAS SUMMARY")
    print("="*70)
    print(f"\nTotal Backend Agents: {len(AGENT_REGISTRY)}")
    print(f"Total Aliases: {len(AGENT_ALIASES)}")
    print(f"Total Accessible Agents: {len(AGENT_REGISTRY) + len(AGENT_ALIASES)}")
    
    print("\n" + "-"*70)
    print("Alias Mappings:")
    print("-"*70)
    for alias, target in sorted(AGENT_ALIASES.items()):
        print(f"  {alias:25} -> {target}")
    print("="*70 + "\n")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("APOLLO AGENT ALIAS MAPPING TEST")
    print("="*70 + "\n")
    
    # Run tests
    test1 = test_alias_resolution()
    test2 = test_direct_agents()
    test3 = test_connector_agents()
    
    # Print summary
    print_summary()
    
    # Final result
    if test1 and test2 and test3:
        print("🎉 All tests passed! Agent routing is working correctly.\n")
        exit(0)
    else:
        print("❌ Some tests failed. Please review the errors above.\n")
        exit(1)
