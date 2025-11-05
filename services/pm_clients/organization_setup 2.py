"""
Organization Setup for Multi-Codebase PM Tools
Automates setup of GitHub, Bitbucket, Linear, and Jira for multiple codebases
"""

from typing import List, Dict, Optional
import logging

from .github_client import GitHubClient
from .linear_client import LinearClient

logger = logging.getLogger(__name__)


class OrganizationSetup:
    """
    Setup multi-codebase organization structure in PM tools
    
    Strategy:
    1. Single organization (ColossalCapital)
    2. Multiple teams (one per codebase)
    3. Multiple projects per team
    4. Cross-repo visibility
    """
    
    CODEBASES = {
        "atlas": {
            "name": "Atlas",
            "description": "Personal/business management control center",
            "repos": ["Atlas"],
            "teams": ["atlas-frontend", "atlas-backend", "atlas-mobile"],
            "projects": [
                "Atlas Mobile App",
                "Atlas Backend API",
                "Atlas Knowledge Graph"
            ]
        },
        "apollo": {
            "name": "Apollo",
            "description": "AI agent orchestration and intelligence",
            "repos": ["Apollo"],
            "teams": ["apollo-ai", "apollo-learning"],
            "projects": [
                "Apollo AI Agents",
                "Apollo Learning System",
                "Apollo PM Integration"
            ]
        },
        "akashic": {
            "name": "Akashic",
            "description": "Development terminal with AI assistance",
            "repos": ["Akashic"],
            "teams": ["akashic-ide", "akashic-analysis"],
            "projects": [
                "Akashic IDE",
                "Akashic Analysis Engine",
                "Akashic PM Sync"
            ]
        },
        "delt": {
            "name": "Delt",
            "description": "Trading UI and portfolio management",
            "repos": ["Delt"],
            "teams": ["delt-frontend", "delt-backend"],
            "projects": [
                "Delt Mobile App",
                "Delt Trading Engine",
                "Delt Portfolio Analytics"
            ]
        },
        "ackwardroots": {
            "name": "AckwardRootsInc",
            "description": "Trading infrastructure and connectors",
            "repos": ["AckwardRootsInc"],
            "teams": ["trading-infrastructure"],
            "projects": [
                "Exchange Connectors",
                "Data Pipeline",
                "Backtesting Engine"
            ]
        },
        "worldturtlefarm": {
            "name": "WorldTurtleFarm",
            "description": "NFT platform and marketplace",
            "repos": ["WorldTurtleFarm"],
            "teams": ["nft-platform"],
            "projects": [
                "NFT Marketplace",
                "Breeding System",
                "Blockchain Integration"
            ]
        },
        "infrastructure": {
            "name": "Infrastructure",
            "description": "Shared infrastructure and DevOps",
            "repos": ["Infrastructure"],
            "teams": ["devops", "security"],
            "projects": [
                "Docker Infrastructure",
                "Kubernetes Deployment",
                "Security & Monitoring"
            ]
        }
    }
    
    def __init__(
        self,
        github_token: Optional[str] = None,
        linear_api_key: Optional[str] = None,
        org_name: str = "ColossalCapital"
    ):
        self.org_name = org_name
        self.github = GitHubClient(token=github_token)
        self.linear = LinearClient(api_key=linear_api_key)
    
    async def setup_linear_workspace(self):
        """
        Setup Linear workspace with teams and projects
        
        Structure:
        - Workspace: ColossalCapital
        - Teams: One per codebase
        - Projects: Multiple per team
        """
        logger.info("🚀 Setting up Linear workspace...")
        
        # Get or create teams
        existing_teams = self.linear.get_teams()
        team_map = {}
        
        for codebase_key, codebase in self.CODEBASES.items():
            # Check if team exists
            team = next(
                (t for t in existing_teams if t["name"] == codebase["name"]),
                None
            )
            
            if not team:
                logger.info(f"📝 Creating Linear team: {codebase['name']}")
                # Note: Linear team creation requires admin API access
                # For now, teams should be created manually via UI
                logger.warning(f"⚠️  Please create team '{codebase['name']}' manually in Linear")
                continue
            
            team_map[codebase_key] = team["id"]
            
            # Create projects for this team
            for project_name in codebase["projects"]:
                logger.info(f"📋 Creating project: {project_name}")
                try:
                    self.linear.create_project(
                        team_id=team["id"],
                        name=project_name,
                        description=f"{codebase['name']} - {project_name}"
                    )
                except Exception as e:
                    logger.warning(f"Project may already exist: {e}")
        
        logger.info("✅ Linear workspace setup complete!")
        return team_map
    
    async def setup_github_organization(self):
        """
        Setup GitHub organization structure
        
        Note: Most org-level operations require owner permissions
        This documents the structure to create manually
        """
        logger.info("🚀 Setting up GitHub organization...")
        
        structure = {
            "organization": self.org_name,
            "repositories": [],
            "teams": []
        }
        
        for codebase_key, codebase in self.CODEBASES.items():
            # Document repos
            for repo in codebase["repos"]:
                structure["repositories"].append({
                    "name": repo,
                    "description": codebase["description"],
                    "teams": codebase["teams"]
                })
            
            # Document teams
            for team in codebase["teams"]:
                structure["teams"].append({
                    "name": team,
                    "repos": codebase["repos"],
                    "permission": "push"  # or "admin" for leads
                })
        
        logger.info("📋 GitHub organization structure:")
        logger.info(f"Organization: {structure['organization']}")
        logger.info(f"Repositories: {len(structure['repositories'])}")
        logger.info(f"Teams: {len(structure['teams'])}")
        
        return structure
    
    def generate_setup_script(self, output_file: str = "setup_pm_tools.sh"):
        """
        Generate shell script for manual setup
        
        This creates a documented script for setting up:
        - GitHub teams
        - Linear teams
        - Repository permissions
        - Project boards
        """
        script = f"""#!/bin/bash
# PM Tools Setup Script for {self.org_name}
# Generated automatically - review before running

echo "🚀 Setting up PM tools for {self.org_name}"

# GitHub Organization: {self.org_name}
# =====================================

"""
        
        for codebase_key, codebase in self.CODEBASES.items():
            script += f"""
# {codebase['name']} - {codebase['description']}
# -------------------------------------
"""
            
            # GitHub repos
            for repo in codebase["repos"]:
                script += f"""
# Repository: {repo}
# gh repo create {self.org_name}/{repo} --public --description "{codebase['description']}"
"""
            
            # GitHub teams
            for team in codebase["teams"]:
                script += f"""
# Team: {team}
# gh api orgs/{self.org_name}/teams -f name="{team}" -f description="{codebase['name']} team"
"""
                
                # Add team to repos
                for repo in codebase["repos"]:
                    script += f"""# gh api orgs/{self.org_name}/teams/{team}/repos/{self.org_name}/{repo} -X PUT -f permission="push"
"""
        
        script += """
echo "✅ Setup complete!"
echo ""
echo "⚠️  Manual steps required:"
echo "1. Create Linear teams via web UI"
echo "2. Configure branch protection rules"
echo "3. Set up CI/CD workflows"
echo "4. Configure webhooks for PM sync"
"""
        
        with open(output_file, 'w') as f:
            f.write(script)
        
        logger.info(f"📝 Setup script generated: {output_file}")
        return output_file
    
    def generate_ownership_docs(self, output_file: str = "OWNERSHIP.md"):
        """
        Generate ownership documentation
        
        Documents:
        - Legal ownership structure
        - Code ownership
        - Access control
        - Future spin-out strategy
        """
        docs = f"""# Ownership Structure - {self.org_name}

## Current Structure (Hybrid)

**Primary Legal Owner:** Colossal Capital LLC

**Code Ownership:**
- Most code owned by Colossal Capital LLC
- WorldTurtleFarm is separate LLC (already spun out)
- All repositories under {self.org_name} GitHub organization (for now)
- All PM tools (Linear, Jira) under Colossal Capital account

**Codebases:**

"""
        
        for codebase_key, codebase in self.CODEBASES.items():
            # Special handling for WorldTurtleFarm
            if codebase_key == "worldturtlefarm":
                status = "**Separate LLC** - WorldTurtleFarm LLC"
                ownership = "Owned by WorldTurtleFarm LLC, code hosted under Colossal Capital org"
            else:
                status = "Product of Colossal Capital LLC"
                ownership = "Owned by Colossal Capital LLC"
            
            docs += f"""
### {codebase['name']}
- **Description:** {codebase['description']}
- **Repositories:** {', '.join(codebase['repos'])}
- **Teams:** {', '.join(codebase['teams'])}
- **Legal Status:** {status}
- **Ownership:** {ownership}
"""
        
        docs += """

## Access Control

**Organization Admins:**
- Full access to all repositories
- Can create/delete teams
- Can manage billing

**Team Leads:**
- Admin access to team repositories
- Can manage team members
- Can create projects

**Team Members:**
- Push access to team repositories
- Can create issues/PRs
- Can comment on all repos

## Current Hybrid Model: WorldTurtleFarm

**WorldTurtleFarm LLC** (already spun out):
- ✅ Separate legal entity
- ✅ Own business model (NFT platform)
- 🔄 Code still in ColossalCapital GitHub org
- 🔄 Uses Colossal Capital PM tools
- 🔄 Shares infrastructure

**Options for WorldTurtleFarm:**

**Option A: Keep in Colossal Capital org (CURRENT)**
- ✅ Easier collaboration
- ✅ Shared infrastructure
- ✅ Single PM tool
- ⚠️ Need clear license agreement
- ⚠️ Code ownership documented

**Option B: Move to separate org (FUTURE)**
- Create WorldTurtleFarm GitHub org
- Transfer repository
- Separate Linear/Jira workspace
- License shared infrastructure
- More administrative overhead

## Future Spin-Out Strategy

If/when other codebases become separate companies:

1. **Create new GitHub organization** for each company
2. **Transfer repository** to new organization
3. **Create new Linear/Jira workspace** for each company
4. **Establish license agreements** between companies
5. **Maintain shared infrastructure** under Colossal Capital

**Example (following WorldTurtleFarm model):**
```
Atlas LLC (new org)
├── Owns: Atlas repository
├── License: Can use shared infrastructure
├── Option: Stay in Colossal org or move to own org
└── Shared: Infrastructure remains with Colossal Capital
```

## Recommendations

**Now (Hybrid Model - RECOMMENDED):**
- ✅ Keep all code under Colossal Capital GitHub org
- ✅ Use teams for separation
- ✅ Single PM tool (Linear or Jira)
- ✅ Single billing, easier management
- ✅ Cross-repo visibility and collaboration
- ✅ Document ownership clearly (WorldTurtleFarm LLC owns their code)
- ✅ License agreement between Colossal Capital and WorldTurtleFarm

**WorldTurtleFarm Specific:**
- Keep in Colossal Capital org for now
- Benefits from shared infrastructure
- Can spin out to own org later if needed
- Clear ownership documentation is sufficient

**Later (Separate Organizations):**
- Only when regulatory requirements demand it
- When seeking separate funding rounds
- When acquisition interest in single codebase
- When administrative overhead is worth it

## Decision Criteria for Moving to Separate Org

Move to separate org when:
- [ ] Separate investors requiring separate cap table
- [ ] Regulatory requirements (e.g., financial services licensing)
- [ ] Acquisition interest in single codebase
- [ ] Need to restrict access between entities
- [ ] Different security/compliance requirements

Keep in single org if:
- [x] Shared team working on multiple codebases (CURRENT)
- [x] Synergies between codebases (CURRENT)
- [x] Shared infrastructure (CURRENT)
- [x] Single funding source (CURRENT)
- [x] Early stage / building MVP (CURRENT)

## License Agreement Template

**For WorldTurtleFarm LLC:**

```
WorldTurtleFarm Code License Agreement

1. Ownership: WorldTurtleFarm LLC owns all code in WorldTurtleFarm repository
2. Hosting: Code hosted in ColossalCapital GitHub organization for convenience
3. Infrastructure: WorldTurtleFarm can use Colossal Capital shared infrastructure
4. Access: Colossal Capital has access to code for infrastructure/DevOps purposes
5. Transfer: WorldTurtleFarm can transfer to own org at any time with 30 days notice
```
"""
        
        with open(output_file, 'w') as f:
            f.write(docs)
        
        logger.info(f"📝 Ownership docs generated: {output_file}")
        return output_file


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Initialize setup
        setup = OrganizationSetup(org_name="ColossalCapital")
        
        # Generate setup script
        setup.generate_setup_script("setup_pm_tools.sh")
        
        # Generate ownership docs
        setup.generate_ownership_docs("OWNERSHIP.md")
        
        # Setup Linear (requires manual team creation first)
        # await setup.setup_linear_workspace()
        
        print("✅ Setup files generated!")
        print("📝 Review setup_pm_tools.sh before running")
        print("📖 Read OWNERSHIP.md for ownership structure")
    
    asyncio.run(main())
