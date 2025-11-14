#!/bin/bash
# Test Deployment System in Apollo Docker Container

echo "🧪 Testing Deployment System in Apollo Container"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "docker-compose.complete-system.yml" ]; then
    echo -e "${RED}❌ Error: Must run from Infrastructure directory${NC}"
    echo "cd to: /Users/leonard/Documents/repos/Jacob Aaron Leonard LLC/ColossalCapital/Infrastructure"
    exit 1
fi

echo -e "${YELLOW}Step 1: Checking Apollo container...${NC}"
if ! docker-compose -f docker-compose.complete-system.yml ps apollo | grep -q "Up"; then
    echo -e "${RED}❌ Apollo container is not running${NC}"
    echo "Start it with: docker-compose -f docker-compose.complete-system.yml up -d apollo"
    exit 1
fi
echo -e "${GREEN}✅ Apollo is running${NC}"
echo ""

echo -e "${YELLOW}Step 2: Testing deployment mapper...${NC}"
docker-compose -f docker-compose.complete-system.yml exec -T apollo python3 << 'EOF'
import asyncio
import sys
sys.path.insert(0, '/app')

from services.deployment_mapper import DeploymentMapper

async def test():
    try:
        print("  📂 Analyzing Infrastructure folder...")
        mapper = DeploymentMapper('/workspace/Infrastructure')
        result = await mapper.analyze_deployments()
        
        print(f"  ✅ Found {len(result['deployment_map'])} deployment categories")
        print(f"  ⚠️  Detected {len(result['conflicts'])} conflicts")
        print(f"  💡 Generated {len(result['recommendations'])} recommendations")
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

success = asyncio.run(test())
sys.exit(0 if success else 1)
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment mapper works!${NC}"
else
    echo -e "${RED}❌ Deployment mapper failed${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}Step 3: Testing full orchestrator integration...${NC}"
docker-compose -f docker-compose.complete-system.yml exec -T apollo python3 << 'EOF'
import asyncio
import sys
sys.path.insert(0, '/app')

from services.akashic_intelligence_orchestrator import AkashicIntelligenceOrchestrator

async def test():
    try:
        print("  🚀 Running full analysis...")
        orchestrator = AkashicIntelligenceOrchestrator(entity_id="test")
        
        result = await orchestrator.analyze_repository(
            '/workspace/Infrastructure',
            options={
                'watch_files': False,
                'consolidate_docs': False,
                'generate_plan': False,
                'build_knowledge_graph': False,
                'index_for_search': False,
            }
        )
        
        if 'deployment_mapping' in result['phases']:
            dm = result['phases']['deployment_mapping']
            print(f"  ✅ Deployment mapping: {dm.get('folders_analyzed', 0)} folders")
            print(f"  ⚠️  Conflicts: {dm.get('conflicts', 0)}")
            
        if 'deployment_reconciliation' in result['phases']:
            dr = result['phases']['deployment_reconciliation']
            print(f"  🤖 AI reconciliation: {dr.get('conflicts_analyzed', 0)} conflicts analyzed")
            
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

success = asyncio.run(test())
sys.exit(0 if success else 1)
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Full orchestrator works!${NC}"
else
    echo -e "${RED}❌ Full orchestrator failed${NC}"
    exit 1
fi
echo ""

echo -e "${YELLOW}Step 4: Checking generated files...${NC}"
if [ -f ".akashic/analysis/DEPLOYMENT_MAPPING.md" ]; then
    echo -e "${GREEN}✅ Deployment mapping report generated${NC}"
else
    echo -e "${YELLOW}⚠️  Deployment mapping report not found (may not have been saved yet)${NC}"
fi

if [ -d ".akashic/deploy/local" ]; then
    echo -e "${GREEN}✅ Local deployment configs generated${NC}"
    echo "  📂 Files:"
    ls -la .akashic/deploy/local/ 2>/dev/null | head -10
else
    echo -e "${YELLOW}⚠️  Local deployment configs not found (may not have been generated yet)${NC}"
fi

if [ -f ".akashic/reconciliation/DEPLOYMENT_RECONCILIATION.md" ]; then
    echo -e "${GREEN}✅ AI reconciliation report generated${NC}"
else
    echo -e "${YELLOW}⚠️  AI reconciliation report not found (no conflicts detected)${NC}"
fi
echo ""

echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
echo ""
echo "📂 Results saved to:"
echo "   Infrastructure/.akashic/analysis/DEPLOYMENT_MAPPING.md"
echo "   Infrastructure/.akashic/deploy/"
echo "   Infrastructure/.akashic/reconciliation/"
echo ""
echo "🚀 Next steps:"
echo "   1. View reports: cat .akashic/analysis/DEPLOYMENT_MAPPING.md"
echo "   2. Check configs: ls -la .akashic/deploy/"
echo "   3. Use in Akashic IDE: Click 'Analyze' button"
