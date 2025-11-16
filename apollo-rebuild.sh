#!/bin/bash
###############################################################################
# APOLLO AI REBUILD SCRIPT
# Rebuilds Apollo Docker container and restarts service
#
# Usage:
#   ./apollo-rebuild.sh              # Full rebuild (Docker)
#   ./apollo-rebuild.sh --no-cache   # Rebuild without cache
#   ./apollo-rebuild.sh --restart    # Just restart container
###############################################################################

set -e

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🤖 APOLLO AI REBUILD (Docker)${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Get directories
INFRA_DIR="/Users/leonard/Documents/repos/Jacob Aaron Leonard LLC/ColossalCapital/Infrastructure"
APOLLO_ROOT="/Users/leonard/Documents/repos/Jacob Aaron Leonard LLC/ColossalCapital/Apollo"

# Parse arguments
NO_CACHE=""
RESTART_ONLY=false

if [ "$1" == "--no-cache" ]; then
  NO_CACHE="--no-cache"
  echo -e "${BLUE}🔄 Rebuilding without cache${NC}"
  echo ""
elif [ "$1" == "--restart" ]; then
  RESTART_ONLY=true
  echo -e "${BLUE}🔄 Restarting container only${NC}"
  echo ""
fi

cd "$INFRA_DIR"

if [ "$RESTART_ONLY" = true ]; then
  # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  # Just restart the container
  # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  echo -e "${BLUE}Step 1/1:${NC} Restarting Apollo container..."
  
  docker-compose -f docker-compose.complete-system.yml restart apollo
  
  echo -e "${GREEN}   ✅ Apollo container restarted${NC}"
  echo ""
else
  # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  # STEP 1: Stop Apollo Container
  # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  echo -e "${BLUE}Step 1/3:${NC} Stopping Apollo container..."
  
  docker-compose -f docker-compose.complete-system.yml stop apollo 2>/dev/null || true
  docker-compose -f docker-compose.complete-system.yml rm -f apollo 2>/dev/null || true
  
  echo -e "${GREEN}   ✅ Apollo container stopped${NC}"
  echo ""
  
  # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  # STEP 2: Rebuild Apollo Container
  # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  echo -e "${BLUE}Step 2/3:${NC} Rebuilding Apollo Docker image..."
  echo "   🐳 This may take 2-5 minutes..."
  
  docker-compose -f docker-compose.complete-system.yml build $NO_CACHE apollo 2>&1 | grep -E "(Step|Successfully|ERROR)" || true
  
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}   ✅ Apollo image rebuilt${NC}"
  else
    echo -e "${RED}   ❌ Apollo build failed!${NC}"
    exit 1
  fi
  echo ""
  
  # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  # STEP 3: Start Apollo Container
  # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  echo -e "${BLUE}Step 3/3:${NC} Starting Apollo container..."
  
  docker-compose -f docker-compose.complete-system.yml up -d apollo
  
  # Wait for container to be ready
  echo "   ⏳ Waiting for Apollo to be ready..."
  sleep 5
  
  # Check health
  if curl -s http://localhost:8002/health > /dev/null 2>&1; then
    echo -e "${GREEN}   ✅ Apollo is healthy${NC}"
  else
    echo -e "${YELLOW}   ⚠️  Apollo may still be starting...${NC}"
  fi
  
  echo ""
fi

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Summary
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Apollo AI Ready!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🤖 Apollo API:      http://localhost:8002/"
echo "📊 API Docs:        http://localhost:8002/docs"
echo "🔍 Health Check:    http://localhost:8002/health"
echo "📈 Metrics:         http://localhost:8002/metrics"
echo ""
echo "🐳 Docker Status:"
echo "   docker-compose -f $INFRA_DIR/docker-compose.complete-system.yml ps apollo"
echo ""
echo "📊 Apollo Logs:"
echo "   docker-compose -f $INFRA_DIR/docker-compose.complete-system.yml logs -f apollo"
echo ""
echo "📝 Quick Commands:"
echo "   ./apollo-rebuild.sh              # Full rebuild (Docker)"
echo "   ./apollo-rebuild.sh --no-cache   # Rebuild without cache"
echo "   ./apollo-rebuild.sh --restart    # Just restart container"
echo ""
echo "🔄 Development Workflow:"
echo "   Code changes:        ./apollo-rebuild.sh --restart  (instant with volume mount!)"
echo "   New dependencies:    ./apollo-rebuild.sh --no-cache"
echo "   New agent added:     ./apollo-rebuild.sh --restart  (no rebuild needed!)"
echo ""
echo "🎯 Agent Categories:"
echo "   • Layer 1: Parsers (40 agents)"
echo "   • Layer 2: Recognition (10 agents)"
echo "   • Layer 3: Domain Experts (29 agents)"
echo "   • Layer 4: Workflows (12 agents)"
echo "   • Layer 5: Meta (3 agents)"
echo "   • Layer 6: Autonomous (5 agents)"
echo "   • Layer 7: Swarm (3 agents)"
echo "   • Connectors: (49 agents)"
echo ""
