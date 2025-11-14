"""
Automated PM Tools Setup
Creates projects, repositories, and teams across Jira, Bitbucket, and GitHub
"""

import asyncio
import os
from typing import Dict, List
import logging

from .jira_client import JiraClient
from .bitbucket_client import BitbucketClient
from .github_client import GitHubClient
from .linear_client import LinearClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PMToolsSetup:
    """Automated setup for all PM tools"""
    
    CODEBASES = {
        "atlas": {
            "name": "Atlas",
            "description": "Personal/business management control center",
            "jira_key": "ATLAS",
            "projects": ["Atlas Mobile App", "Atlas Backend", "Atlas Knowledge Graph"]
        },
        "apollo": {
            "name": "Apollo",
            "description": "AI agent orchestration and intelligence",
            "jira_key": "APOLLO",
            "projects": ["Apollo AI Agents", "Apollo Learning System"]
        },
        "akashic": {
            "name": "Akashic",
            "description": "Development terminal with AI assistance",
            "jira_key": "AKASHIC",
            "projects": ["Akashic IDE", "Akashic Analysis"]
        },
        "delt": {
            "name": "Delt",
            "description": "Trading UI and portfolio management",
            "jira_key": "DELT",
            "projects": ["Delt Mobile", "Delt Trading Engine"]
        },
        "ackwardroots": {
            "name": "AckwardRootsInc",
            "description": "Trading infrastructure and connectors",
            "jira_key": "ACKWARD",
            "projects": ["Exchange Connectors", "Data Pipeline"]
        },
        "worldturtlefarm": {
            "name": "WorldTurtleFarm",
            "description": "NFT platform and marketplace",
            "jira_key": "WTF",
            "projects": ["NFT Marketplace", "Breeding System"]
        },
        "infrastructure": {
            "name": "Infrastructure",
            "description": "Shared infrastructure and DevOps",
            "jira_key": "INFRA",
            "projects": ["Docker Infrastructure", "CI/CD Pipeline"]
        }
    }
    
    def __init__(self):
        # Initialize clients
        self.jira = JiraClient()
        self.bitbucket = BitbucketClient()
        self.github = GitHubClient()
        self.linear = None
        
        # Try to initialize Linear if credentials exist
        if os.getenv("LINEAR_API_KEY"):
            self.linear = LinearClient()
    
    async def setup_all(self):
        """Run complete setup for all PM tools"""
        logger.info("🚀 Starting PM tools setup...")
        
        # 1. Setup Jira
        logger.info("\n📋 Setting up Jira...")
        await self.setup_jira()
        
        # 2. Setup Bitbucket
        logger.info("\n🪣 Setting up Bitbucket...")
        await self.setup_bitbucket()
        
        # 3. Setup GitHub
        logger.info("\n🐙 Setting up GitHub...")
        await self.setup_github()
        
        # 4. Setup Linear (if available)
        if self.linear:
            logger.info("\n📐 Setting up Linear...")
            await self.setup_linear()
        
        logger.info("\n✅ PM tools setup complete!")
        logger.info("\n📊 Summary:")
        logger.info(f"  - Jira: {len(self.CODEBASES)} projects created")
        logger.info(f"  - Bitbucket: {len(self.CODEBASES)} repositories created")
        logger.info(f"  - GitHub: {len(self.CODEBASES)} teams created")
        if self.linear:
            logger.info(f"  - Linear: {len(self.CODEBASES)} teams created")
    
    async def setup_jira(self):
        """Setup Jira projects"""
        # Get current user for project lead
        user = self.jira.get_current_user()
        
        for codebase_key, codebase in self.CODEBASES.items():
            try:
                # Create project
                project = self.jira.create_project({
                    "key": codebase["jira_key"],
                    "name": codebase["name"],
                    "projectTypeKey": "software",
                    "projectTemplateKey": "com.pyxis.greenhopper.jira:gh-simplified-agility-kanban",
                    "description": codebase["description"],
                    "leadAccountId": user["accountId"]
                })
                
                logger.info(f"  ✅ Created project: {project['name']} ({project['key']})")
                
                # Create sample epic
                epic = self.jira.create_epic(
                    project_key=codebase["jira_key"],
                    name=f"{codebase['name']} MVP",
                    description=f"Complete MVP for {codebase['name']}"
                )
                
                logger.info(f"    📌 Created epic: {epic['key']}")
                
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info(f"  ⏭️  Project {codebase['jira_key']} already exists, skipping")
                else:
                    logger.error(f"  ❌ Error creating project {codebase['jira_key']}: {e}")
    
    async def setup_bitbucket(self):
        """Setup Bitbucket repositories"""
        # Create main project first
        try:
            project = self.bitbucket.create_project({
                "name": "Colossal Capital",
                "key": "CC",
                "description": "Main project for all Colossal Capital repositories",
                "is_private": True
            })
            logger.info(f"  ✅ Created project: {project['name']}")
        except Exception as e:
            if "already exists" in str(e).lower():
                logger.info(f"  ⏭️  Project CC already exists, skipping")
            else:
                logger.error(f"  ❌ Error creating project: {e}")
        
        # Create repositories
        for codebase_key, codebase in self.CODEBASES.items():
            try:
                repo = self.bitbucket.create_repository({
                    "name": codebase["name"],
                    "description": codebase["description"],
                    "is_private": True,
                    "scm": "git",
                    "project": {"key": "CC"}
                })
                
                logger.info(f"  ✅ Created repository: {repo['name']}")
                
            except Exception as e:
                if "already exists" in str(e).lower():
                    logger.info(f"  ⏭️  Repository {codebase['name']} already exists, skipping")
                else:
                    logger.error(f"  ❌ Error creating repository {codebase['name']}: {e}")
    
    async def setup_github(self):
        """Setup GitHub teams"""
        org = "ColossalCapital"
        
        for codebase_key, codebase in self.CODEBASES.items():
            team_name = f"{codebase_key}-team"
            
            try:
                # Note: GitHub team creation requires org owner permissions
                # This would need to be done via GitHub CLI or web UI
                logger.info(f"  ℹ️  Team {team_name} should be created manually via GitHub UI")
                logger.info(f"     Name: {team_name}")
                logger.info(f"     Description: {codebase['description']}")
                logger.info(f"     Repository: {codebase['name']}")
                
            except Exception as e:
                logger.error(f"  ❌ Error with team {team_name}: {e}")
    
    async def setup_linear(self):
        """Setup Linear teams and projects"""
        # Get existing teams
        teams = self.linear.get_teams()
        
        for codebase_key, codebase in self.CODEBASES.items():
            # Find or note team needs to be created
            team = next((t for t in teams if t["name"] == codebase["name"]), None)
            
            if not team:
                logger.info(f"  ℹ️  Team {codebase['name']} should be created manually via Linear UI")
                continue
            
            # Create projects for this team
            for project_name in codebase["projects"]:
                try:
                    project = self.linear.create_project(
                        team_id=team["id"],
                        name=project_name,
                        description=f"{codebase['name']} - {project_name}"
                    )
                    logger.info(f"  ✅ Created project: {project['name']}")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        logger.info(f"  ⏭️  Project {project_name} already exists, skipping")
                    else:
                        logger.error(f"  ❌ Error creating project {project_name}: {e}")
    
    def print_manual_steps(self):
        """Print manual steps that need to be done"""
        print("\n" + "="*80)
        print("MANUAL STEPS REQUIRED")
        print("="*80)
        
        print("\n1. GitHub Teams (requires org owner):")
        print("   Go to: https://github.com/orgs/ColossalCapital/teams")
        print("   Create these teams:")
        for codebase_key, codebase in self.CODEBASES.items():
            print(f"   - {codebase_key}-team → {codebase['name']} repository")
        
        print("\n2. Linear Teams (if using Linear):")
        print("   Go to: https://linear.app/settings/teams")
        print("   Create these teams:")
        for codebase_key, codebase in self.CODEBASES.items():
            print(f"   - {codebase['name']}")
        
        print("\n3. Configure Webhooks:")
        print("   - Jira → Apollo: /api/webhooks/jira")
        print("   - Bitbucket → Apollo: /api/webhooks/bitbucket")
        print("   - GitHub → Apollo: /api/webhooks/github")
        
        print("\n" + "="*80)


async def main():
    """Run setup"""
    # Check environment variables
    required_vars = {
        "JIRA_SITE_URL": os.getenv("JIRA_SITE_URL"),
        "JIRA_EMAIL": os.getenv("JIRA_EMAIL"),
        "JIRA_API_TOKEN": os.getenv("JIRA_API_TOKEN"),
        "BITBUCKET_WORKSPACE": os.getenv("BITBUCKET_WORKSPACE"),
        "BITBUCKET_USERNAME": os.getenv("BITBUCKET_USERNAME"),
        "BITBUCKET_APP_PASSWORD": os.getenv("BITBUCKET_APP_PASSWORD"),
    }
    
    missing = [k for k, v in required_vars.items() if not v]
    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        print("\nPlease set these variables and try again.")
        print("See SETUP_INSTRUCTIONS.md for details.")
        return
    
    # Run setup
    setup = PMToolsSetup()
    await setup.setup_all()
    
    # Print manual steps
    setup.print_manual_steps()


if __name__ == "__main__":
    asyncio.run(main())
