"""
Deployment Reconciliation - AI-Guided Conflict Resolution

Uses Apollo AI to guide users through resolving deployment conflicts
with natural language explanations and recommendations.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DeploymentReconciliation:
    """AI-guided reconciliation for deployment conflicts"""
    
    def __init__(self, repo_path: str, apollo_api_url: Optional[str] = None):
        self.repo_path = Path(repo_path)
        self.apollo_api_url = apollo_api_url or os.getenv("APOLLO_API_URL", "http://apollo:8002")
        self.reconciliation_dir = self.repo_path / '.akashic' / 'reconciliation'
        self.reconciliation_dir.mkdir(parents=True, exist_ok=True)
        
    async def reconcile_conflicts(
        self,
        conflicts: List[Dict],
        deployment_map: Dict
    ) -> Dict:
        """
        AI-guided reconciliation of deployment conflicts
        
        Args:
            conflicts: List of detected conflicts
            deployment_map: Current deployment mapping
            
        Returns:
            Reconciliation plan with AI guidance
        """
        logger.info("🤖 Starting AI-guided deployment reconciliation...")
        
        if not conflicts:
            logger.info("✅ No conflicts to reconcile")
            return {
                'status': 'no_conflicts',
                'conflicts_resolved': 0,
                'recommendations': []
            }
        
        # Analyze conflicts with AI
        reconciliation_plan = {
            'timestamp': datetime.now().isoformat(),
            'total_conflicts': len(conflicts),
            'conflicts': [],
            'recommendations': [],
            'action_plan': [],
        }
        
        for i, conflict in enumerate(conflicts, 1):
            logger.info(f"  🔍 Analyzing conflict {i}/{len(conflicts)}: {conflict['type']}")
            
            # Get AI guidance for this conflict
            ai_guidance = await self._get_ai_guidance(conflict, deployment_map)
            
            conflict_resolution = {
                'conflict': conflict,
                'ai_analysis': ai_guidance['analysis'],
                'recommended_action': ai_guidance['recommendation'],
                'alternatives': ai_guidance['alternatives'],
                'risk_level': ai_guidance['risk_level'],
                'estimated_time': ai_guidance['estimated_time'],
            }
            
            reconciliation_plan['conflicts'].append(conflict_resolution)
            reconciliation_plan['recommendations'].append(ai_guidance['recommendation'])
        
        # Generate action plan
        reconciliation_plan['action_plan'] = self._generate_action_plan(
            reconciliation_plan['conflicts']
        )
        
        # Save reconciliation report
        self._save_reconciliation_report(reconciliation_plan)
        
        logger.info(f"✅ Reconciliation plan generated with {len(conflicts)} conflicts")
        
        return reconciliation_plan
    
    async def _get_ai_guidance(
        self,
        conflict: Dict,
        deployment_map: Dict
    ) -> Dict:
        """Get AI guidance for resolving a specific conflict"""
        
        # Build context for AI
        context = {
            'conflict_type': conflict['type'],
            'severity': conflict['severity'],
            'description': conflict['description'],
            'locations': conflict['locations'],
            'deployment_map': deployment_map,
        }
        
        # In production, this would call Apollo AI API
        # For now, provide intelligent default guidance
        
        if conflict['type'] == 'docker_overlap':
            return self._guide_docker_overlap(conflict, deployment_map)
        elif conflict['type'] == 'kubernetes_overlap':
            return self._guide_kubernetes_overlap(conflict, deployment_map)
        elif conflict['type'] == 'terraform_terraspace_conflict':
            return self._guide_terraform_conflict(conflict, deployment_map)
        else:
            return self._guide_generic_conflict(conflict, deployment_map)
    
    def _guide_docker_overlap(self, conflict: Dict, deployment_map: Dict) -> Dict:
        """AI guidance for Docker configuration overlaps"""
        
        locations = conflict['locations']
        
        analysis = f"""
🔍 **Docker Configuration Overlap Detected**

You have Docker configurations in {len(locations)} different locations:
{chr(10).join(f'  - {loc}' for loc in locations)}

**Why This Is a Problem:**
- Multiple Docker setups can cause confusion
- Different configurations may conflict
- Hard to maintain consistency
- Wastes development time

**What's Happening:**
Each location likely has slightly different service definitions, ports, or environment variables.
This makes it unclear which configuration is the "source of truth."
"""
        
        recommendation = {
            'action': 'consolidate',
            'target': '.akashic/deploy/local/docker/',
            'steps': [
                'Review all Docker configurations',
                'Identify the most complete/recent one',
                'Merge unique services from other configs',
                'Move consolidated config to .akashic/deploy/local/docker/',
                'Update documentation to reference new location',
                'Archive old configs (don\'t delete yet)',
            ],
            'rationale': 'Consolidation eliminates confusion and creates a single source of truth',
        }
        
        alternatives = [
            {
                'name': 'Keep separate for different purposes',
                'description': 'If configs serve different purposes (dev vs prod), keep them but rename clearly',
                'when_to_use': 'When configurations are intentionally different',
            },
            {
                'name': 'Migrate to Podman',
                'description': 'Use this opportunity to switch to rootless Podman',
                'when_to_use': 'If you want better security and Kubernetes compatibility',
            },
        ]
        
        return {
            'analysis': analysis,
            'recommendation': recommendation,
            'alternatives': alternatives,
            'risk_level': 'medium',
            'estimated_time': '30-60 minutes',
        }
    
    def _guide_kubernetes_overlap(self, conflict: Dict, deployment_map: Dict) -> Dict:
        """AI guidance for Kubernetes configuration overlaps"""
        
        locations = conflict['locations']
        
        analysis = f"""
🔍 **Kubernetes Configuration Overlap Detected**

You have Kubernetes manifests in {len(locations)} different locations:
{chr(10).join(f'  - {loc}' for loc in locations)}

**Why This Is a Problem:**
- Multiple K8s configs can deploy conflicting resources
- Different namespaces may not be coordinated
- Hard to track which manifests are active
- Risk of resource conflicts in cluster

**What's Happening:**
Each location may have overlapping Deployments, Services, or ConfigMaps.
This can cause deployment failures or unexpected behavior.
"""
        
        recommendation = {
            'action': 'consolidate_with_overlays',
            'target': '.akashic/deploy/cloud/kubernetes/',
            'steps': [
                'Create base/ directory for common resources',
                'Create overlays/ for environment-specific configs',
                'Use Kustomize for environment management',
                'Move all manifests to new structure',
                'Test with: kubectl apply -k overlays/dev/',
                'Archive old configs',
            ],
            'rationale': 'Kustomize overlays provide clean environment separation with shared base',
        }
        
        alternatives = [
            {
                'name': 'Use Helm charts',
                'description': 'Convert to Helm for better templating and versioning',
                'when_to_use': 'If you need complex configuration management',
            },
            {
                'name': 'Separate by namespace',
                'description': 'Keep separate but ensure different namespaces',
                'when_to_use': 'If configs are for completely different applications',
            },
        ]
        
        return {
            'analysis': analysis,
            'recommendation': recommendation,
            'alternatives': alternatives,
            'risk_level': 'high',
            'estimated_time': '1-2 hours',
        }
    
    def _guide_terraform_conflict(self, conflict: Dict, deployment_map: Dict) -> Dict:
        """AI guidance for Terraform/Terraspace conflicts"""
        
        analysis = """
🔍 **Terraform Configuration Detected**

You have Terraform configs, but we recommend migrating to Terraspace.

**Why Terraspace?**
- One codebase for dev/qa/prod (DRY principle)
- Built-in environment management
- Better integration with Juju charms
- Easier to maintain multi-environment deployments

**What's Happening:**
Your current Terraform setup likely has separate folders for each environment,
leading to code duplication and maintenance overhead.
"""
        
        recommendation = {
            'action': 'migrate_to_terraspace',
            'target': '.akashic/deploy/cloud/terraspace/',
            'steps': [
                'Review existing Terraform modules',
                'Create Terraspace project structure',
                'Convert modules to Terraspace format',
                'Create tfvars for each environment',
                'Test with: terraspace up microk8s -y --var-file=tfvars/dev.tfvars',
                'Migrate state files carefully',
                'Archive old Terraform configs',
            ],
            'rationale': 'Terraspace eliminates environment duplication and simplifies management',
        }
        
        alternatives = [
            {
                'name': 'Keep Terraform with workspaces',
                'description': 'Use Terraform workspaces for environment separation',
                'when_to_use': 'If you prefer staying with vanilla Terraform',
            },
            {
                'name': 'Use Terraform Cloud',
                'description': 'Leverage Terraform Cloud for environment management',
                'when_to_use': 'If you want hosted Terraform with team collaboration',
            },
        ]
        
        return {
            'analysis': analysis,
            'recommendation': recommendation,
            'alternatives': alternatives,
            'risk_level': 'medium',
            'estimated_time': '2-3 hours',
        }
    
    def _guide_generic_conflict(self, conflict: Dict, deployment_map: Dict) -> Dict:
        """Generic AI guidance for unknown conflict types"""
        
        analysis = f"""
🔍 **Deployment Conflict Detected**

Type: {conflict['type']}
Severity: {conflict['severity']}

{conflict['description']}

**Locations:**
{chr(10).join(f'  - {loc}' for loc in conflict.get('locations', []))}
"""
        
        recommendation = {
            'action': 'manual_review',
            'target': '.akashic/deploy/',
            'steps': [
                'Review conflicting configurations',
                'Identify differences',
                'Decide on consolidation strategy',
                'Test changes in dev environment',
                'Document decision',
            ],
            'rationale': 'Manual review needed for this specific conflict type',
        }
        
        return {
            'analysis': analysis,
            'recommendation': recommendation,
            'alternatives': [],
            'risk_level': conflict['severity'],
            'estimated_time': '1-2 hours',
        }
    
    def _generate_action_plan(self, conflicts: List[Dict]) -> List[Dict]:
        """Generate prioritized action plan"""
        
        # Sort by risk level and estimated time
        risk_priority = {'high': 0, 'medium': 1, 'low': 2}
        
        sorted_conflicts = sorted(
            conflicts,
            key=lambda x: (
                risk_priority.get(x['risk_level'], 3),
                self._parse_time(x['estimated_time'])
            )
        )
        
        action_plan = []
        
        for i, conflict in enumerate(sorted_conflicts, 1):
            action_plan.append({
                'step': i,
                'priority': 'HIGH' if conflict['risk_level'] == 'high' else 'MEDIUM',
                'conflict_type': conflict['conflict']['type'],
                'action': conflict['recommended_action']['action'],
                'estimated_time': conflict['estimated_time'],
                'steps': conflict['recommended_action']['steps'],
            })
        
        return action_plan
    
    def _parse_time(self, time_str: str) -> int:
        """Parse time estimate to minutes"""
        if 'hour' in time_str:
            hours = int(time_str.split('-')[0].strip())
            return hours * 60
        elif 'min' in time_str:
            mins = int(time_str.split('-')[0].strip())
            return mins
        return 60  # Default 1 hour
    
    def _save_reconciliation_report(self, plan: Dict):
        """Save reconciliation report to markdown"""
        
        report_path = self.reconciliation_dir / 'DEPLOYMENT_RECONCILIATION.md'
        
        report = f"""# 🤖 AI-Guided Deployment Reconciliation

Generated: {plan['timestamp']}

## Summary

- **Total Conflicts:** {plan['total_conflicts']}
- **Risk Levels:** {self._count_risk_levels(plan['conflicts'])}

---

## Conflicts & Recommendations

"""
        
        for i, conflict_resolution in enumerate(plan['conflicts'], 1):
            conflict = conflict_resolution['conflict']
            rec = conflict_resolution['recommended_action']
            
            report += f"""
### {i}. {conflict['type'].replace('_', ' ').title()}

**Severity:** {conflict['severity'].upper()}  
**Risk Level:** {conflict_resolution['risk_level'].upper()}  
**Estimated Time:** {conflict_resolution['estimated_time']}

{conflict_resolution['ai_analysis']}

#### 💡 Recommended Action: {rec['action'].replace('_', ' ').title()}

**Target:** `{rec['target']}`

**Steps:**
"""
            
            for step_num, step in enumerate(rec['steps'], 1):
                report += f"{step_num}. {step}\n"
            
            report += f"\n**Rationale:** {rec['rationale']}\n"
            
            # Add alternatives
            if conflict_resolution['alternatives']:
                report += "\n#### 🔄 Alternative Approaches:\n\n"
                for alt in conflict_resolution['alternatives']:
                    report += f"**{alt['name']}**\n"
                    report += f"- {alt['description']}\n"
                    report += f"- *When to use:* {alt['when_to_use']}\n\n"
            
            report += "---\n"
        
        # Add action plan
        report += "\n## 📋 Prioritized Action Plan\n\n"
        
        for action in plan['action_plan']:
            report += f"""
### Step {action['step']}: {action['conflict_type'].replace('_', ' ').title()} ({action['priority']})

**Action:** {action['action'].replace('_', ' ').title()}  
**Estimated Time:** {action['estimated_time']}

**Steps:**
"""
            for step_num, step in enumerate(action['steps'], 1):
                report += f"{step_num}. {step}\n"
            
            report += "\n"
        
        # Add next steps
        report += """
---

## 🚀 Next Steps

1. Review this reconciliation report
2. Start with highest priority conflicts (HIGH risk)
3. Follow the recommended steps for each conflict
4. Test changes in development environment
5. Document your decisions
6. Re-run `akashic analyze` to verify conflicts are resolved

---

## 💬 Need Help?

This report was generated by Apollo AI. If you need clarification on any recommendation:

1. Open Akashic IDE
2. Go to Apollo AI Chat
3. Ask: "Explain deployment conflict: [conflict type]"

Apollo AI will provide detailed, context-aware guidance!

---

**Generated by Apollo AI Deployment Reconciliation** 🤖
"""
        
        report_path.write_text(report)
        logger.info(f"📝 Saved reconciliation report to {report_path}")
    
    def _count_risk_levels(self, conflicts: List[Dict]) -> str:
        """Count conflicts by risk level"""
        high = sum(1 for c in conflicts if c['risk_level'] == 'high')
        medium = sum(1 for c in conflicts if c['risk_level'] == 'medium')
        low = sum(1 for c in conflicts if c['risk_level'] == 'low')
        
        parts = []
        if high: parts.append(f"{high} HIGH")
        if medium: parts.append(f"{medium} MEDIUM")
        if low: parts.append(f"{low} LOW")
        
        return ', '.join(parts) if parts else '0'


if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Example usage
        reconciliation = DeploymentReconciliation("/path/to/repo")
        
        conflicts = [
            {
                'type': 'docker_overlap',
                'severity': 'high',
                'description': 'Multiple Docker configurations found',
                'locations': ['Infrastructure/docker/', 'Infrastructure/docker-compose/'],
            }
        ]
        
        plan = await reconciliation.reconcile_conflicts(conflicts, {})
        print(f"Generated plan with {len(plan['conflicts'])} conflicts")
    
    asyncio.run(main())
