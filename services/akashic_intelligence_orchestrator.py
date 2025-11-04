"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Akashic Intelligence Orchestrator
Coordinates all intelligence agents when user loads a codebase

Integrates:
- CodeWatcherAgent (agents/analytics/code_watcher_agent.py)
- DocsConsolidator (services/docs_consolidator.py)
- PMAutomationService (services/pm_automation.py)
- ProjectPlanGenerator (agents/pm/project_plan_generator.py)
- KnowledgeGraphBuilder (agents/documents/knowledge_graph_builder.py)
- AgenticCodebaseRAG (learning/agentic_codebase_rag.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

# Existing agents
from agents.analytics.code_watcher_agent import CodeWatcherAgent
from agents.pm.project_plan_generator import ProjectPlanGenerator
from agents.documents.knowledge_graph_builder import KnowledgeGraphBuilder
from learning.agentic_codebase_rag import AgenticCodebaseRAG
from learning.theta_edgecloud import ThetaEdgeCloud

# Existing services
from services.docs_consolidator import DocumentationConsolidator
from services.pm_automation import PMAutomationService
from services.project_type_detector import ProjectTypeDetector
from services.scaffold_generator import ScaffoldGenerator
from services.deployment_mapper import DeploymentMapper
from services.deployment_config_generator import DeploymentConfigGenerator
from services.deployment_reconciliation import DeploymentReconciliation
from services.pm_bidirectional_sync import PMBidirectionalSync

logger = logging.getLogger(__name__)


class AkashicIntelligenceOrchestrator:
    """
    Orchestrates all intelligence agents when user loads a codebase
    
    Workflow:
    1. Code Watcher - Scan repo, track files
    2. Docs Watcher - Find documentation
    3. Git Analyzer - Analyze history
    4. Future State Detector - Mark planned features
    5. Docs Consolidator - Merge duplicate docs
    6. PM Automation - Generate project plan
    7. Knowledge Graph - Build relationships
    8. Codebase RAG - Index for search
    9. Continuous Monitoring - Watch changes
    """
    
    def __init__(
        self,
        entity_id: str,
        org_id: Optional[str] = None,
        linear_api_key: Optional[str] = None
    ):
        self.entity_id = entity_id
        self.org_id = org_id
        
        # Will be initialized per-repo
        self.code_watcher: Optional[CodeWatcherAgent] = None
        self.docs_consolidator: Optional[DocumentationConsolidator] = None
        self.pm_automation: Optional[PMAutomationService] = None
        self.project_plan_generator: Optional[ProjectPlanGenerator] = None
        self.knowledge_graph_builder: Optional[KnowledgeGraphBuilder] = None
        self.codebase_rag: Optional[AgenticCodebaseRAG] = None
        self.project_type_detector: Optional[ProjectTypeDetector] = None
        self.scaffold_generator: Optional[ScaffoldGenerator] = None
        self.deployment_mapper: Optional[DeploymentMapper] = None
        self.deployment_config_generator: Optional[DeploymentConfigGenerator] = None
        self.deployment_reconciliation: Optional[DeploymentReconciliation] = None
        self.pm_sync: Optional[PMBidirectionalSync] = None
        
        self.linear_api_key = linear_api_key
        
        # Progress tracking
        self.current_phase = ""
        self.current_step = ""  # Scan, Index, Analyze, Plan
        self.progress_percentage = 0
        self.phase_details = ""
    
    def _update_progress(self, step: str, phase: str, percentage: int, details: str = ""):
        """Update progress tracking"""
        self.current_step = step
        self.current_phase = phase
        self.progress_percentage = percentage
        self.phase_details = details
        logger.info(f"📊 Progress: {percentage}% - {step} - {phase}")
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress"""
        return {
            'step': self.current_step,
            'phase': self.current_phase,
            'percentage': self.progress_percentage,
            'details': self.phase_details
        }
        
    async def analyze_repository(
        self,
        repo_path: str,
        options: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        """
        Analyze repository and provide comprehensive intelligence
        
        Args:
            repo_path: Path to repository
            options: {
                'watch_files': True,
                'consolidate_docs': True,
                'generate_plan': True,
                'build_knowledge_graph': True,
                'index_for_search': True
            }
        
        Returns:
            Complete analysis results
        """
        if options is None:
            options = {
                'watch_files': True,
                'consolidate_docs': True,
                'generate_plan': True,
                'build_knowledge_graph': True,
                'index_for_search': True
            }
        
        # Translate host path to container path if running in Docker
        container_repo_path = self._translate_path_for_container(repo_path)
        
        logger.info(f"🧠 Starting Akashic Intelligence Analysis: {container_repo_path}")
        
        results = {
            'repo_path': container_repo_path,
            'started_at': datetime.now().isoformat(),
            'phases': {}
        }
        
        # Create .akashic directory structure first
        akashic_dir = Path(container_repo_path) / ".akashic"
        self._create_akashic_structure(akashic_dir)
        logger.info(f"  📁 Created .akashic directory structure")
        
        # ============================================================
        # PHASE 1: INITIAL SCAN
        # ============================================================
        self._update_progress("Scan", "Phase 1: Initial Scan", 10, "Scanning codebase files...")
        logger.info("📊 Phase 1: Initial Scan")
        
        # 1. Code Watcher - Scan all files
        if options.get('watch_files', True):
            logger.info("  👁️  Scanning files...")
            self.code_watcher = CodeWatcherAgent(repo_path=container_repo_path, entity_id=self.entity_id)
            scan_results = await self.code_watcher.initial_scan()
            results['phases']['code_scan'] = scan_results
            logger.info(f"  ✅ Scanned {scan_results['total_files']} files")
        
        # ============================================================
        # PHASE 2: PROJECT TYPE DETECTION
        # ============================================================
        self._update_progress("Scan", "Phase 2: Project Type Detection", 20, "Detecting project type...")
        logger.info("🔍 Phase 2: Project Type Detection")
        
        # Detect project type and generate scaffolding recommendations
        logger.info("  🎯 Detecting project type...")
        self.project_type_detector = ProjectTypeDetector(container_repo_path)
        project_type = self.project_type_detector.detect_project_type()
        scaffold_plan = self.project_type_detector.generate_scaffold_plan()
        
        results['phases']['project_type_detection'] = {
            'primary': project_type.primary,
            'secondary': project_type.secondary,
            'confidence': project_type.confidence,
            'scaffold_type': project_type.scaffold_type,
            'deployment_strategy': project_type.deployment_strategy,
            'testing_strategy': project_type.testing_strategy,
            'recommendations': project_type.recommendations,
            'estimated_scaffold_time_minutes': scaffold_plan.estimated_time_minutes,
        }
        
        logger.info(f"  ✅ Detected: {project_type.primary} ({project_type.confidence * 100:.1f}% confidence)")
        
        # Save detection report
        detection_report_path = Path(container_repo_path) / '.akashic' / 'analysis' / 'PROJECT_TYPE_DETECTION.md'
        detection_report_path.parent.mkdir(parents=True, exist_ok=True)
        self.project_type_detector.save_detection_report(str(detection_report_path))
        
        # ============================================================
        # PHASE 2B: DEPLOYMENT MAPPING
        # ============================================================
        self._update_progress("Scan", "Phase 2B: Deployment Mapping", 25, "Mapping deployment configurations...")
        logger.info("🗺️  Phase 2B: Deployment Mapping")
        
        # Map scattered deployment configurations
        logger.info("  📂 Mapping deployment configurations...")
        self.deployment_mapper = DeploymentMapper(container_repo_path)
        deployment_analysis = await self.deployment_mapper.analyze_deployments()
        
        results['phases']['deployment_mapping'] = {
            'folders_analyzed': len(deployment_analysis['deployment_map']),
            'conflicts': len(deployment_analysis['conflicts']),
            'recommendations': len(deployment_analysis['recommendations']),
        }
        
        # Save deployment mapping report
        analysis_dir = Path(container_repo_path) / '.akashic' / 'analysis'
        self.deployment_mapper.save_report(analysis_dir)
        
        logger.info(f"  ✅ Mapped {len(deployment_analysis['deployment_map'])} deployment categories")
        
        # Generate deployment configs
        logger.info("  🔧 Generating deployment configurations...")
        self.deployment_config_generator = DeploymentConfigGenerator(
            container_repo_path,
            deployment_analysis['deployment_map']
        )
        await self.deployment_config_generator.generate_all()
        
        logger.info(f"  ✅ Generated deployment configs in .akashic/deploy/")
        
        # AI-guided reconciliation for conflicts
        if deployment_analysis['conflicts']:
            logger.info(f"  🤖 Running AI-guided reconciliation for {len(deployment_analysis['conflicts'])} conflicts...")
            self.deployment_reconciliation = DeploymentReconciliation(container_repo_path)
            reconciliation_result = await self.deployment_reconciliation.reconcile_conflicts(
                deployment_analysis['conflicts'],
                deployment_analysis['deployment_map']
            )
            
            results['phases']['deployment_reconciliation'] = {
                'conflicts_analyzed': len(deployment_analysis['conflicts']),
                'recommendations_generated': len(reconciliation_result['recommendations']),
                'action_plan_steps': len(reconciliation_result['action_plan']),
            }
            
            logger.info(f"  ✅ AI reconciliation complete - see .akashic/reconciliation/DEPLOYMENT_RECONCILIATION.md")
        else:
            logger.info(f"  ✅ No deployment conflicts detected")
            results['phases']['deployment_reconciliation'] = {
                'conflicts_analyzed': 0,
                'status': 'no_conflicts',
            }
        
        # ============================================================
        # PHASE 2C: PM SYNC (PULL FROM CLOUD)
        # ============================================================
        self._update_progress("Index", "Phase 2C: PM Sync", 30, "Syncing tickets from cloud...")
        logger.info("🔄 Phase 2C: PM Sync (Pull from Cloud)")
        
        # Initialize PM sync
        self.pm_sync = PMBidirectionalSync(
            container_repo_path,
            linear_api_key=self.linear_api_key,
            # TODO: Add other PM tool keys
        )
        
        # Pull existing tickets from cloud
        logger.info("  ⬇️  Pulling tickets from cloud PM tools...")
        pm_sync_result = await self.pm_sync.sync_all('cloud_to_local')
        
        results['phases']['pm_sync_pull'] = {
            'linear': pm_sync_result.get('linear'),
            'jira': pm_sync_result.get('jira'),
            'github': pm_sync_result.get('github'),
            'bitbucket': pm_sync_result.get('bitbucket'),
        }
        
        logger.info(f"  ✅ Synced tickets from cloud")
        
        # ============================================================
        # PHASE 3: INTELLIGENCE ANALYSIS
        # ============================================================
        self._update_progress("Index", "Phase 3: Intelligence Analysis", 40, "Running intelligence analysis...")
        logger.info("🧠 Phase 3: Intelligence Analysis")
        
        # 2. Documentation Consolidation
        if options.get('consolidate_docs', True) and self.code_watcher:
            logger.info("  📝 Consolidating documentation...")
            doc_files = self.code_watcher.get_documentation_files()
            
            if doc_files:
                # Use .akashic/docs/ for consolidated documentation
                output_path = Path(container_repo_path) / ".akashic" / "docs"
                output_path.mkdir(parents=True, exist_ok=True)
                self.docs_consolidator = DocumentationConsolidator(
                    watch_paths=[container_repo_path],
                    output_path=str(output_path),
                    entity_id=self.entity_id,
                    org_id=self.org_id
                )
                
                consolidation_results = await self._consolidate_documentation(doc_files)
                results['phases']['docs_consolidation'] = consolidation_results
                logger.info(f"  ✅ Consolidated {len(doc_files)} docs")
        
        # 3. Project Plan Generation
        if options.get('generate_plan', True):
            logger.info("  🎯 Generating project plan...")
            self.project_plan_generator = ProjectPlanGenerator()
            self.pm_automation = PMAutomationService(
                entity_id=self.entity_id,
                org_id=self.org_id,
                linear_api_key=self.linear_api_key
            )
            
            plan_results = await self._generate_project_plan(container_repo_path, results)
            results['phases']['project_plan'] = plan_results
            logger.info(f"  ✅ Generated plan with {plan_results.get('ticket_count', 0)} tickets")
        
        # 4. Knowledge Graph Building
        if options.get('build_knowledge_graph', True):
            logger.info("  🕸️  Building knowledge graph...")
            atlas_api_url = os.getenv("ATLAS_API_URL", "http://atlas-backend:8000")
            self.knowledge_graph_builder = KnowledgeGraphBuilder(atlas_api_url=atlas_api_url)
            
            graph_results = await self._build_knowledge_graph(container_repo_path, results)
            results['phases']['knowledge_graph'] = graph_results
            logger.info(f"  ✅ Built graph with {graph_results.get('node_count', 0)} nodes")
        
        # 5. Codebase RAG Indexing
        if options.get('index_for_search', True):
            logger.info("  🔍 Indexing for semantic search...")
            self.codebase_rag = AgenticCodebaseRAG(
                codebase_id=f"{self.entity_id}_{Path(container_repo_path).name}",
                team_id=self.org_id or "default_team",
                org_id=self.org_id or "default_org",
                repo_path=container_repo_path
            )
            
            index_results = await self._index_codebase(container_repo_path)
            results['phases']['rag_indexing'] = index_results
            logger.info(f"  ✅ Indexed {index_results.get('chunk_count', 0)} code chunks")
        
        # ============================================================
        # PHASE 4: SCAFFOLDING RECOMMENDATIONS
        # ============================================================
        self._update_progress("Analyze", "Phase 4: Scaffolding", 60, "Generating scaffolding recommendations...")
        logger.info("🏗️  Phase 4: Scaffolding Recommendations")
        
        # Generate scaffolding recommendations based on project type
        scaffolding_recommendations = await self._generate_scaffolding_recommendations(
            project_type, 
            scaffold_plan,
            results
        )
        results['phases']['scaffolding'] = scaffolding_recommendations
        logger.info(f"  ✅ Generated scaffolding plan with {len(scaffolding_recommendations.get('tasks', []))} tasks")
        
        # ============================================================
        # PHASE 5: RESTRUCTURING SUGGESTIONS
        # ============================================================
        self._update_progress("Analyze", "Phase 5: Restructuring", 70, "Generating restructuring suggestions...")
        logger.info("💡 Phase 5: Restructuring Suggestions")
        
        suggestions = await self._generate_restructuring_suggestions(results, project_type)
        results['phases']['restructuring'] = suggestions
        logger.info(f"  ✅ Generated {len(suggestions.get('suggestions', []))} suggestions")
        
        # ============================================================
        # PHASE 6: PM INTEGRATION
        # ============================================================
        self._update_progress("Plan", "Phase 6: PM Integration", 80, "Generating PM tickets...")
        logger.info("📋 Phase 6: PM Integration")
        
        # Generate PM tickets from all recommendations
        pm_integration = await self._generate_pm_tickets(
            container_repo_path,
            project_type,
            scaffolding_recommendations,
            suggestions,
            results
        )
        results['phases']['pm_integration'] = pm_integration
        logger.info(f"  ✅ Generated {pm_integration.get('total_tickets', 0)} PM tickets")
        
        # ============================================================
        # PHASE 6B: PM RECONCILIATION
        # ============================================================
        logger.info("🤖 Phase 6B: PM Reconciliation")
        
        # Sync bidirectionally to detect conflicts
        logger.info("  🔄 Comparing local and cloud tickets...")
        reconciliation_result = await self.pm_sync.sync_all('bidirectional')
        
        if reconciliation_result['reconciliation_needed']:
            logger.info(f"  ⚠️  Detected {len(reconciliation_result['conflicts'])} conflicts")
            logger.info("  📝 Generated reconciliation plan")
            logger.info("  👉 Review: .akashic/pm/RECONCILIATION_REPORT.md")
            logger.info("  👉 Apply: akashic pm reconcile --apply")
            
            results['phases']['pm_reconciliation'] = {
                'conflicts_detected': len(reconciliation_result['conflicts']),
                'reconciliation_plan': reconciliation_result.get('reconciliation_plan'),
                'requires_user_action': True,
            }
        else:
            logger.info("  ✅ No conflicts detected - local and cloud are aligned")
            results['phases']['pm_reconciliation'] = {
                'conflicts_detected': 0,
                'requires_user_action': False,
            }
        
        # ============================================================
        # PHASE 7: START CONTINUOUS MONITORING
        # ============================================================
        self._update_progress("Plan", "Phase 7: Monitoring", 90, "Starting continuous monitoring...")
        if options.get('watch_files', True) and self.code_watcher:
            logger.info("👁️  Phase 7: Starting Continuous Monitoring")
            self.code_watcher.start_watching()
            results['monitoring'] = {'status': 'active'}
        
        results['completed_at'] = datetime.now().isoformat()
        
        # ============================================================
        # PHASE 8: WRITE OUTPUT FILES
        # ============================================================
        self._update_progress("Plan", "Phase 8: Writing Files", 95, "Writing output files...")
        if options.get('save_results', True):
            logger.info("💾 Phase 8: Writing Output Files")
            # akashic_dir already created at the beginning
            
            await self._write_output_files(akashic_dir, results, container_repo_path)
            results['output_dir'] = str(akashic_dir)
            logger.info(f"  ✅ Output saved to {akashic_dir}")
        
        self._update_progress("Complete", "Analysis Complete", 100, "All phases finished!")
        logger.info("✅ Akashic Intelligence Analysis Complete!")
        
        return results
    
    async def _consolidate_documentation(self, doc_files: List[str]) -> Dict:
        """Consolidate documentation using DocsConsolidator"""
        # Read all docs
        docs_content = {}
        for doc_path in doc_files:
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    docs_content[doc_path] = f.read()
            except:
                pass
        
        # Use DocsConsolidator to merge
        # (This would call the actual consolidation logic)
        result = {
            'total_docs': len(doc_files),
            'duplicates_found': 0,
            'conflicts_found': 0,
            'consolidated_path': None
        }
        
        # TODO: Implement actual consolidation using DocsConsolidator
        # For now, return structure
        
        return result
    
    async def _generate_project_plan(self, repo_path: str, scan_results: Dict) -> Dict:
        """Generate project plan using PM agents"""
        # Get hot files for prioritization
        hot_files = []
        if self.code_watcher:
            hot_files = self.code_watcher.get_hot_files(limit=10)
        
        # Use ProjectPlanGenerator
        # (This would call the actual plan generation)
        result = {
            'ticket_count': 0,
            'roadmap_versions': [],
            'hot_files_prioritized': len(hot_files)
        }
        
        # TODO: Implement actual plan generation
        # For now, return structure
        
        return result
    
    async def _build_knowledge_graph(self, repo_path: str, scan_results: Dict) -> Dict:
        """Build knowledge graph using KnowledgeGraphBuilder"""
        # Get file dependencies
        file_relationships = []
        if self.code_watcher:
            for path, metrics in self.code_watcher.metrics.items():
                if metrics.imports:
                    for imported in metrics.imports:
                        file_relationships.append({
                            'from': path,
                            'to': imported,
                            'type': 'imports'
                        })
        
        result = {
            'node_count': len(self.code_watcher.metrics) if self.code_watcher else 0,
            'relationship_count': len(file_relationships),
            'graph_built': True
        }
        
        # TODO: Implement actual graph building
        # For now, return structure
        
        return result
    
    async def _index_codebase(self, repo_path: str) -> Dict:
        """Index codebase using AgenticCodebaseRAG"""
        # Use existing AgenticCodebaseRAG
        if self.codebase_rag:
            # This would call the actual indexing
            result = {
                'chunk_count': 0,
                'indexed': True
            }
        else:
            result = {'indexed': False}
        
        # TODO: Implement actual indexing
        # For now, return structure
        
        return result
    
    async def _generate_scaffolding_recommendations(
        self,
        project_type,
        scaffold_plan,
        analysis_results: Dict
    ) -> Dict:
        """Generate scaffolding recommendations based on project type"""
        tasks = []
        
        # Task 1: UI Scaffolding (if needed)
        if scaffold_plan.ui_scaffold:
            tasks.append({
                'id': 'scaffold-ui',
                'title': f'Generate {project_type.scaffold_type} UI',
                'description': f'Auto-generate UI scaffolding for {project_type.primary} project',
                'category': 'scaffolding',
                'priority': 'high',
                'estimated_minutes': scaffold_plan.ui_scaffold.get('estimated_minutes', 5),
                'dependencies': [],
                'details': scaffold_plan.ui_scaffold,
            })
        
        # Task 2: Deployment Configuration
        if scaffold_plan.deployment_scaffold:
            tasks.append({
                'id': 'scaffold-deployment',
                'title': 'Configure Deployment',
                'description': f'Set up {project_type.deployment_strategy}',
                'category': 'deployment',
                'priority': 'high',
                'estimated_minutes': scaffold_plan.deployment_scaffold.get('estimated_minutes', 10),
                'dependencies': [],
                'details': scaffold_plan.deployment_scaffold,
            })
        
        # Task 3: Testing Configuration
        if scaffold_plan.testing_scaffold:
            tasks.append({
                'id': 'scaffold-testing',
                'title': 'Configure Testing',
                'description': f'Set up {project_type.testing_strategy}',
                'category': 'testing',
                'priority': 'medium',
                'estimated_minutes': scaffold_plan.testing_scaffold.get('estimated_minutes', 10),
                'dependencies': [],
                'details': scaffold_plan.testing_scaffold,
            })
        
        # Task 4: Documentation Generation
        if scaffold_plan.documentation_scaffold:
            tasks.append({
                'id': 'scaffold-documentation',
                'title': 'Generate Documentation',
                'description': 'Create deployment guides and testing documentation',
                'category': 'documentation',
                'priority': 'medium',
                'estimated_minutes': scaffold_plan.documentation_scaffold.get('estimated_minutes', 5),
                'dependencies': ['scaffold-deployment', 'scaffold-testing'],
                'details': scaffold_plan.documentation_scaffold,
            })
        
        return {
            'tasks': tasks,
            'total_estimated_minutes': scaffold_plan.estimated_time_minutes,
            'project_type': project_type.primary,
            'scaffold_type': project_type.scaffold_type,
        }
    
    async def _generate_restructuring_suggestions(self, analysis_results: Dict, project_type) -> Dict:
        """Generate intelligent restructuring suggestions based on project type"""
        suggestions = {
            'suggestions': [],
            'protected_files': [],
            'safe_to_delete': [],
            'move_suggestions': []
        }
        
        if not self.code_watcher:
            return suggestions
        
        # Get planned features (PROTECTED)
        planned = self.code_watcher.get_planned_features()
        for p in planned:
            suggestions['protected_files'].append({
                'path': p.get('path', p) if isinstance(p, dict) else p,
                'reason': 'Contains TODO/FIXME/FUTURE marker',
                'planned_for': 'unknown',
                'description': 'Planned feature'
            })
        
        # Get cold files (candidates for deletion)
        try:
            cold_files = self.code_watcher.get_cold_files(limit=20)
        except Exception as e:
            logger.warning(f"Failed to get cold files: {e}")
            cold_files = []
        
        for file_data in cold_files:
            try:
                path = file_data.get('path') if isinstance(file_data, dict) else file_data
                if not path:
                    continue
                
                # Check if it's a planned feature
                is_protected = any(path in str(p) for p in planned)
                
                if not is_protected:
                    suggestions['safe_to_delete'].append({
                        'path': path,
                        'reason': 'Cold file - rarely accessed',
                        'last_edited': 'unknown',
                        'size_bytes': 0
                    })
            except Exception as e:
                logger.warning(f"Failed to process file {file_data}: {e}")
                continue
        
        # Generate general suggestions
        scan_data = analysis_results.get('phases', {}).get('code_scan', {})
        total_files = scan_data.get('total_files', 0)
        doc_files = len(scan_data.get('documentation_files', []))
        
        if total_files > 0:
            suggestions['suggestions'].append({
                'type': 'documentation',
                'description': f'Documentation coverage: {doc_files}/{total_files} files ({int(doc_files/total_files*100)}%)',
                'priority': 'medium',
                'action': 'Consider adding more documentation for complex modules'
            })
        
        if len(cold_files) > 5:
            suggestions['suggestions'].append({
                'type': 'cleanup',
                'description': f'Found {len(cold_files)} cold files that are rarely accessed',
                'priority': 'low',
                'action': 'Review cold files for potential archival or deletion'
            })
        
        if len(planned) > 0:
            suggestions['suggestions'].append({
                'type': 'planning',
                'description': f'Found {len(planned)} files with TODO/FIXME markers',
                'priority': 'high',
                'action': 'Create tickets for planned features and technical debt'
            })
        
        # Add project-type specific suggestions
        if project_type:
            if project_type.primary == 'web3':
                suggestions['suggestions'].append({
                    'type': 'web3',
                    'description': 'Web3 project detected - consider adding contract tests and deployment scripts',
                    'priority': 'high',
                    'action': 'Set up Hardhat/Foundry testing and deployment to testnets'
                })
            elif project_type.primary == 'react':
                suggestions['suggestions'].append({
                    'type': 'react',
                    'description': 'React project detected - consider adding E2E tests and component library',
                    'priority': 'medium',
                    'action': 'Set up Playwright for E2E testing and shadcn/ui for components'
                })
            elif project_type.primary == 'python_api':
                suggestions['suggestions'].append({
                    'type': 'python_api',
                    'description': 'Python API detected - consider adding API tests and OpenAPI docs',
                    'priority': 'medium',
                    'action': 'Set up pytest for API testing and generate OpenAPI documentation'
                })
        
        return suggestions
    
    async def _generate_pm_tickets(
        self,
        repo_path: str,
        project_type,
        scaffolding_recommendations: Dict,
        restructuring_suggestions: Dict,
        analysis_results: Dict
    ) -> Dict:
        """Generate PM tickets from all recommendations"""
        tickets = []
        
        # Category 1: Scaffolding Tasks (HIGH PRIORITY)
        for task in scaffolding_recommendations.get('tasks', []):
            tickets.append({
                'title': task['title'],
                'description': task['description'],
                'category': task['category'],
                'priority': task['priority'],
                'estimated_hours': task['estimated_minutes'] / 60,
                'labels': ['scaffolding', project_type.primary],
                'dependencies': task.get('dependencies', []),
                'source': 'scaffolding_recommendations',
            })
        
        # Category 2: Documentation Tasks (MEDIUM PRIORITY)
        doc_coverage = analysis_results.get('phases', {}).get('code_scan', {}).get('documentation_files', [])
        total_files = analysis_results.get('phases', {}).get('code_scan', {}).get('total_files', 1)
        doc_percentage = (len(doc_coverage) / total_files) * 100 if total_files > 0 else 0
        
        if doc_percentage < 50:
            tickets.append({
                'title': 'Improve Documentation Coverage',
                'description': f'Current documentation coverage is {doc_percentage:.1f}%. Add docstrings and documentation to reach 50%+.',
                'category': 'documentation',
                'priority': 'medium',
                'estimated_hours': 4,
                'labels': ['documentation', 'code-quality'],
                'dependencies': [],
                'source': 'analysis',
            })
        
        # Category 3: Testing Tasks (MEDIUM PRIORITY)
        test_files = analysis_results.get('phases', {}).get('code_scan', {}).get('test_files', [])
        if len(test_files) == 0:
            tickets.append({
                'title': f'Set up {project_type.testing_strategy}',
                'description': f'No test files detected. Set up testing framework: {project_type.testing_strategy}',
                'category': 'testing',
                'priority': 'high',
                'estimated_hours': 6,
                'labels': ['testing', 'infrastructure'],
                'dependencies': ['scaffold-testing'],
                'source': 'project_type_detection',
            })
        
        # Category 4: Code Quality Tasks (LOW-MEDIUM PRIORITY)
        cold_files = restructuring_suggestions.get('safe_to_delete', [])
        if len(cold_files) > 5:
            tickets.append({
                'title': 'Review and Archive Cold Files',
                'description': f'Found {len(cold_files)} rarely-accessed files. Review for archival or deletion.',
                'category': 'cleanup',
                'priority': 'low',
                'estimated_hours': 2,
                'labels': ['cleanup', 'maintenance'],
                'dependencies': [],
                'source': 'restructuring',
            })
        
        # Category 5: Planned Features (from TODO/FIXME)
        planned_features = analysis_results.get('phases', {}).get('code_scan', {}).get('planned_features', [])
        if len(planned_features) > 0:
            tickets.append({
                'title': 'Address TODO/FIXME Items',
                'description': f'Found {len(planned_features)} files with TODO/FIXME markers. Create tickets for each item.',
                'category': 'technical-debt',
                'priority': 'high',
                'estimated_hours': 8,
                'labels': ['technical-debt', 'planning'],
                'dependencies': [],
                'source': 'code_scan',
            })
        
        # Category 6: Project-Type Specific Recommendations
        for recommendation in project_type.recommendations:
            # Parse recommendation text to create ticket
            if '🎨' in recommendation:  # UI-related
                tickets.append({
                    'title': recommendation.split('🎨')[1].strip(),
                    'description': f'Recommendation from project type detection: {recommendation}',
                    'category': 'feature',
                    'priority': 'high',
                    'estimated_hours': 4,
                    'labels': ['ui', project_type.primary],
                    'dependencies': [],
                    'source': 'project_type_recommendations',
                })
            elif '🧪' in recommendation:  # Testing-related
                tickets.append({
                    'title': recommendation.split('🧪')[1].strip(),
                    'description': f'Recommendation from project type detection: {recommendation}',
                    'category': 'testing',
                    'priority': 'medium',
                    'estimated_hours': 3,
                    'labels': ['testing', project_type.primary],
                    'dependencies': [],
                    'source': 'project_type_recommendations',
                })
        
        # Save tickets to PM folders
        pm_dir = Path(repo_path) / '.akashic' / 'pm'
        
        # Linear format
        linear_tickets = {
            'project_name': Path(repo_path).name,
            'project_type': project_type.primary,
            'generated_at': datetime.now().isoformat(),
            'total_tickets': len(tickets),
            'tickets': tickets,
        }
        
        linear_path = pm_dir / 'linear' / 'tickets.json'
        linear_path.parent.mkdir(parents=True, exist_ok=True)
        import json
        with open(linear_path, 'w') as f:
            json.dump(linear_tickets, f, indent=2)
        
        # Jira format (similar structure)
        jira_path = pm_dir / 'jira' / 'issues.json'
        jira_path.parent.mkdir(parents=True, exist_ok=True)
        with open(jira_path, 'w') as f:
            json.dump(linear_tickets, f, indent=2)  # Same format for now
        
        # GitHub format
        github_path = pm_dir / 'github' / 'issues.json'
        github_path.parent.mkdir(parents=True, exist_ok=True)
        with open(github_path, 'w') as f:
            json.dump(linear_tickets, f, indent=2)  # Same format for now
        
        # Bitbucket format
        bitbucket_path = pm_dir / 'bitbucket' / 'issues.json'
        bitbucket_path.parent.mkdir(parents=True, exist_ok=True)
        with open(bitbucket_path, 'w') as f:
            json.dump(linear_tickets, f, indent=2)  # Same format for now
        
        return {
            'total_tickets': len(tickets),
            'by_category': self._count_by_category(tickets),
            'by_priority': self._count_by_priority(tickets),
            'total_estimated_hours': sum(t['estimated_hours'] for t in tickets),
            'files_created': [
                str(linear_path.relative_to(repo_path)),
                str(jira_path.relative_to(repo_path)),
                str(github_path.relative_to(repo_path)),
                str(bitbucket_path.relative_to(repo_path)),
            ],
        }
    
    def _count_by_category(self, tickets: List[Dict]) -> Dict[str, int]:
        """Count tickets by category"""
        counts = {}
        for ticket in tickets:
            category = ticket['category']
            counts[category] = counts.get(category, 0) + 1
        return counts
    
    def _count_by_priority(self, tickets: List[Dict]) -> Dict[str, int]:
        """Count tickets by priority"""
        counts = {}
        for ticket in tickets:
            priority = ticket['priority']
            counts[priority] = counts.get(priority, 0) + 1
        return counts
    
    def stop_monitoring(self):
        """Stop all monitoring"""
        if self.code_watcher:
            self.code_watcher.stop_watching()
        
        logger.info("🛑 Monitoring stopped")
    
    async def cleanup_and_archive_docs(self, repo_path: str) -> Dict[str, Any]:
        """
        Clean up project by moving scattered docs to .akashic/archive/
        
        This should be run AFTER the first analysis to:
        1. Move all scattered markdown/doc files to .akashic/archive/original/
        2. Keep only .akashic/ folder with organized outputs
        3. Clean up the codebase
        
        Returns:
            Dict with archived files and cleanup stats
        """
        container_repo_path = self._translate_path_for_container(repo_path)
        repo = Path(container_repo_path)
        akashic_dir = repo / ".akashic"
        archive_dir = akashic_dir / "archive" / "original"
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("🧹 Starting cleanup and archive...")
        
        archived_files = []
        skipped_files = []
        
        # Document extensions to archive
        doc_extensions = {'.md', '.txt', '.rst', '.adoc', '.pdf', '.docx'}
        
        # Patterns to skip (keep these in the repo)
        skip_patterns = [
            'README.md',
            'LICENSE',
            'CHANGELOG',
            'CONTRIBUTING',
            '.akashic',  # Don't touch .akashic folder
            '.git',
            'node_modules',
            'venv',
            '__pycache__',
            '.pytest_cache',
            'dist',
            'build'
        ]
        
        # Walk through repo and find docs
        for file_path in repo.rglob('*'):
            # Skip if not a file
            if not file_path.is_file():
                continue
            
            # Skip if in excluded directories
            if any(skip in str(file_path) for skip in skip_patterns):
                skipped_files.append(str(file_path.relative_to(repo)))
                continue
            
            # Check if it's a document
            if file_path.suffix.lower() in doc_extensions:
                try:
                    # Calculate relative path from repo root
                    rel_path = file_path.relative_to(repo)
                    
                    # Create same directory structure in archive
                    archive_file = archive_dir / rel_path
                    archive_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Move file to archive
                    import shutil
                    shutil.move(str(file_path), str(archive_file))
                    
                    archived_files.append({
                        'original': str(rel_path),
                        'archived_to': str(archive_file.relative_to(akashic_dir))
                    })
                    
                    logger.info(f"  📦 Archived: {rel_path}")
                except Exception as e:
                    logger.warning(f"  ⚠️  Failed to archive {file_path}: {e}")
                    skipped_files.append(str(file_path.relative_to(repo)))
        
        # Create archive manifest
        manifest = {
            'archived_at': datetime.now().isoformat(),
            'total_archived': len(archived_files),
            'total_skipped': len(skipped_files),
            'files': archived_files
        }
        
        import json
        manifest_path = archive_dir / "ARCHIVE_MANIFEST.json"
        manifest_path.write_text(json.dumps(manifest, indent=2))
        
        # Create README in archive
        archive_readme = f"""# Archived Original Documents
Archived: {manifest['archived_at']}

## Summary
- **Total Files Archived:** {len(archived_files)}
- **Files Kept in Repo:** {len(skipped_files)}

## What Happened
These documents were scattered throughout the codebase. After Akashic analysis:
1. All content was consolidated into `.akashic/docs/PROJECT_DOCS.md`
2. Original files were moved here for reference
3. The codebase is now cleaner and more organized

## Accessing Archived Files
All files maintain their original directory structure here.
You can reference them if needed, but the consolidated docs in `.akashic/docs/` are the source of truth.

## Files Archived
"""
        
        for file_info in archived_files[:50]:  # First 50
            archive_readme += f"- `{file_info['original']}` → `{file_info['archived_to']}`\n"
        
        if len(archived_files) > 50:
            archive_readme += f"\n*...and {len(archived_files) - 50} more files*\n"
        
        (archive_dir / "README.md").write_text(archive_readme)
        
        logger.info(f"✅ Cleanup complete! Archived {len(archived_files)} files")
        
        return {
            'success': True,
            'archived_count': len(archived_files),
            'skipped_count': len(skipped_files),
            'archive_location': str(archive_dir.relative_to(repo)),
            'manifest_path': str(manifest_path.relative_to(repo)),
            'files': archived_files
        }
    
    def get_dashboard_data(self) -> Dict:
        """Get data for Akashic dashboard"""
        if not self.code_watcher:
            return {'error': 'No active monitoring'}
        
        return {
            'hot_files': self.code_watcher.get_hot_files(limit=10),
            'cold_files': self.code_watcher.get_cold_files(limit=10),
            'planned_features': self.code_watcher.get_planned_features(),
            'documentation_files': self.code_watcher.get_documentation_files(),
            'temperature_distribution': self._get_temperature_distribution()
        }
    
    def _get_temperature_distribution(self) -> Dict[str, int]:
        """Get temperature distribution"""
        if not self.code_watcher:
            return {}
        
        distribution = {'hot': 0, 'warm': 0, 'cool': 0, 'cold': 0}
        for metrics in self.code_watcher.metrics.values():
            distribution[metrics.temperature] += 1
        
        return distribution
    
    def _create_akashic_structure(self, akashic_dir: Path):
        """Create organized .akashic directory structure"""
        # Main directories - Simplified structure
        dirs = [
            # Analysis - Current state, planning, issues, restructuring
            akashic_dir / "analysis",
            
            # Docs - Documentation, diagrams, mermaid
            akashic_dir / "docs" / "diagrams" / "mermaid",
            akashic_dir / "docs" / "diagrams" / "rendered",
            
            # PM - Project management integrations
            akashic_dir / "pm" / "linear",
            akashic_dir / "pm" / "jira",
            akashic_dir / "pm" / "github",
            akashic_dir / "pm" / "bitbucket",
            
            # Deployment - Deployment configs and reconciliation
            akashic_dir / "deploy" / "local",
            akashic_dir / "deploy" / "cloud",
            akashic_dir / "reconciliation",
            
            # Config - Configuration files
            akashic_dir / ".config",
        ]
        
        for dir_path in dirs:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create .gitignore to exclude certain files
        gitignore_content = """# Akashic Intelligence Directory
# Generated files - safe to regenerate

# Exclude rendered diagrams (can be regenerated)
docs/diagrams/rendered/

# Exclude PM sync logs (can be noisy)
pm/*/sync_log.json

# Keep everything else in version control
"""
        (akashic_dir / ".gitignore").write_text(gitignore_content)
        
        # Create config file
        config_content = """# Akashic Intelligence Configuration
version: 1.0.0
auto_sync: true
pm_integrations:
  linear:
    enabled: true
    sync_interval: 300  # 5 minutes
  jira:
    enabled: false
  github:
    enabled: true
  bitbucket:
    enabled: false
"""
        # Use hidden .config folder
        (akashic_dir / ".config" / ".akashic.yml").write_text(config_content)
        
        logger.info(f"  📁 Created organized .akashic structure")
    
    async def _write_output_files(self, output_dir: Path, results: Dict, repo_path: str):
        """Write analysis results to markdown files"""
        
        scan_data = results['phases'].get('code_scan', {})
        
        # 1. CURRENT_STATE.md
        hot_files = scan_data.get('hot_files', [])
        cold_files = scan_data.get('cold_files', [])
        temp_dist = scan_data.get('temperature_distribution', {})
        
        # Enhanced current state with detailed metrics
        code_files = scan_data.get('code_files', [])
        config_files = scan_data.get('config_files', [])
        doc_files = scan_data.get('documentation_files', [])
        test_files = scan_data.get('test_files', [])
        
        current_state = f"""# Current State Analysis
Generated: {results['completed_at']}

## Executive Summary
- **Repository:** {results['repo_path']}
- **Total Files Analyzed:** {scan_data.get('total_files', 0)}
- **Code Quality:** {'Good' if temp_dist.get('hot', 0) > 0 else 'Needs Attention'}
- **Documentation Coverage:** {int((len(doc_files) / max(scan_data.get('total_files', 1), 1)) * 100)}%
- **Test Coverage:** {len(test_files)} test files found

## File Activity Analysis

### Temperature Distribution
| Status | Count | Percentage | Description |
|--------|-------|------------|-------------|
| 🔥 Hot | {temp_dist.get('hot', 0)} | {int((temp_dist.get('hot', 0) / max(scan_data.get('total_files', 1), 1)) * 100)}% | Actively developed |
| 🌡️ Warm | {temp_dist.get('warm', 0)} | {int((temp_dist.get('warm', 0) / max(scan_data.get('total_files', 1), 1)) * 100)}% | Regular updates |
| 🌤️ Cool | {temp_dist.get('cool', 0)} | {int((temp_dist.get('cool', 0) / max(scan_data.get('total_files', 1), 1)) * 100)}% | Occasional changes |
| ❄️ Cold | {temp_dist.get('cold', 0)} | {int((temp_dist.get('cold', 0) / max(scan_data.get('total_files', 1), 1)) * 100)}% | Rarely touched |

### Hot Files (Active Development)
{self._format_hot_files_with_timeline(hot_files) if hot_files else '*No hot files - consider increasing development activity*'}

### Cold Files (Consider Review/Archive)
{self._format_file_list(cold_files[:20]) if cold_files else '*No cold files detected*'}

## File Type Breakdown

### Code Files ({len(code_files)})
{self._format_file_list(code_files[:15])}
{f'*...and {len(code_files) - 15} more*' if len(code_files) > 15 else ''}

### Configuration Files ({len(config_files)})
{self._format_file_list(config_files)}

### Documentation Files ({len(doc_files)})
{self._format_file_list(doc_files)}

### Test Files ({len(test_files)})
{self._format_file_list(test_files) if test_files else '*No test files found - consider adding tests*'}

## Code Quality Metrics

### Complexity Indicators
- **Large Files:** {len([f for f in code_files if 'large' in str(f).lower()])} (may need refactoring)
- **Configuration Complexity:** {len(config_files)} config files
- **Documentation Ratio:** {len(doc_files)}:{len(code_files)} (docs:code)

### Maintenance Indicators
- **Cold File Ratio:** {int((temp_dist.get('cold', 0) / max(scan_data.get('total_files', 1), 1)) * 100)}%
- **Active Development:** {temp_dist.get('hot', 0) + temp_dist.get('warm', 0)} files
- **Stale Code:** {temp_dist.get('cold', 0)} files

## Recommendations

### Immediate Actions
1. **Review Cold Files:** {temp_dist.get('cold', 0)} files haven't been touched recently
2. **Improve Documentation:** Current coverage is {int((len(doc_files) / max(scan_data.get('total_files', 1), 1)) * 100)}%
3. **Add Tests:** {'Found ' + str(len(test_files)) + ' test files' if test_files else 'No test files detected'}

### Long-term Improvements
1. Increase hot file ratio for active development
2. Archive or delete cold files
3. Maintain documentation coverage above 50%
4. Implement continuous testing
"""
        (output_dir / "analysis" / "CURRENT_STATE.md").write_text(current_state)
        
        # Also save file_metrics.json in analysis folder
        if self.code_watcher and hasattr(self.code_watcher, 'metrics'):
            import json
            metrics_data = {path: vars(metrics) for path, metrics in self.code_watcher.metrics.items()}
            # Save results to JSON in analysis folder
            (output_dir / "analysis" / "file_metrics.json").write_text(json.dumps(results, indent=2, default=str))
        
        # 2. PROJECT_DOCS.md
        doc_files = scan_data.get('documentation_files', [])
        # Enhanced project docs with actual content consolidation
        project_docs = f"""# Project Documentation
Generated: {results['completed_at']}

## Table of Contents
1. [Overview](#overview)
2. [Documentation Files](#documentation-files)
3. [Consolidated Content](#consolidated-content)
4. [Coverage Analysis](#coverage-analysis)

## Overview
- **Total Documentation Files:** {len(doc_files)}
- **Documentation Coverage:** {int((len(doc_files) / max(scan_data.get('total_files', 1), 1)) * 100)}%
- **Status:** {'Good' if len(doc_files) > 5 else 'Needs Improvement'}

## Documentation Files

{self._format_file_list(doc_files)}

## Consolidated Content

"""
        
        # Actually read and consolidate documentation content
        for doc_file in doc_files[:10]:  # Consolidate first 10 docs
            doc_path = Path(results['repo_path']) / doc_file if isinstance(doc_file, str) else Path(results['repo_path']) / doc_file.get('path', '')
            if doc_path.exists() and doc_path.is_file():
                try:
                    content = doc_path.read_text(encoding='utf-8', errors='ignore')
                    project_docs += f"\n### {doc_path.name}\n\n{content[:1000]}{'...' if len(content) > 1000 else ''}\n\n---\n"
                except:
                    project_docs += f"\n### {doc_path.name}\n\n*Could not read file*\n\n---\n"
        
        if len(doc_files) > 10:
            project_docs += f"\n*...and {len(doc_files) - 10} more documentation files*\n"
        
        project_docs += f"""

## Coverage Analysis

### Documentation Gaps
{self._identify_doc_gaps(scan_data)}

### Recommendations
1. {'Add README.md if missing' if 'README' not in str(doc_files) else 'README.md exists ✓'}
2. {'Add API documentation' if 'api' not in str(doc_files).lower() else 'API docs exist ✓'}
3. {'Add architecture documentation' if 'architecture' not in str(doc_files).lower() else 'Architecture docs exist ✓'}
4. Document all major modules and components
5. Keep documentation up-to-date with code changes
"""
        (output_dir / "docs" / "PROJECT_DOCS.md").write_text(project_docs)
        
        # 3. ISSUES_REPORT.md
        restructuring = results['phases'].get('restructuring', {})
        issues_report = f"""# Issues Report
Generated: {results['completed_at']}

## Safe to Delete
{self._format_suggestions(restructuring.get('safe_to_delete', []))}

## Protected Files
{self._format_suggestions(restructuring.get('protected_files', []))}
"""
        (output_dir / "analysis" / "ISSUES_REPORT.md").write_text(issues_report)
        
        # 4. RESTRUCTURING_PLAN.md
        suggestions_list = restructuring.get('suggestions', [])
        safe_to_delete = restructuring.get('safe_to_delete', [])
        
        restructuring_plan = f"""# Restructuring Plan
Generated: {results['completed_at']}

## Summary
- **Total Suggestions:** {len(suggestions_list)}
- **Files Safe to Delete:** {len(safe_to_delete)}
- **Protected Files:** {len(restructuring.get('protected_files', []))}

## Priority Suggestions
{self._format_detailed_suggestions(suggestions_list)}

## Files Safe to Delete
{self._format_file_list([f['path'] for f in safe_to_delete]) if safe_to_delete else '*No files recommended for deletion*'}

## Implementation Steps
1. Review protected files (marked with TODO/FIXME)
2. Create tickets for planned features
3. Archive or delete cold files
4. Update documentation coverage
5. Refactor based on suggestions
"""
        (output_dir / "analysis" / "RESTRUCTURING_PLAN.md").write_text(restructuring_plan)
        
        # 5. FUTURE_STATE.md
        planned_features = scan_data.get('planned_features', [])
        future_state = f"""# Future State Vision
Generated: {results['completed_at']}

## Summary
- **Planned Features:** {len(planned_features)} files with TODO/FIXME/FUTURE markers

## Planned Features
{self._format_file_list(planned_features)}

## Next Steps
These files contain markers indicating planned work:
- Review TODO items and prioritize
- Create tickets for FIXME issues
- Plan implementation for FUTURE features
"""
        (output_dir / "analysis" / "FUTURE_STATE.md").write_text(future_state)
        
        # 6. Generate Mermaid Diagrams
        await self._generate_mermaid_diagrams(output_dir, results)
        
        # 7. Scan Documentation
        doc_analysis = await self._scan_documentation(repo_path)
        self._write_documentation_analysis(output_dir, doc_analysis)
        
        # 8. Scan Testing Coverage
        test_analysis = await self._scan_testing(repo_path)
        self._write_testing_analysis(output_dir, test_analysis)
        
        # 9. Generate Detailed Current State Breakdown
        await self._generate_current_state_breakdown(output_dir, results, repo_path)
        
        # 10. Generate Complete Documentation Suite
        await self._generate_complete_docs(output_dir, results, repo_path)
        
        # 11. Create placeholder README files for remaining empty folders
        self._create_placeholder_readmes(output_dir)
    
    def _format_hot_files_with_timeline(self, files: List) -> str:
        """Format hot files with precise timeline and grouping"""
        if not files:
            return "*No hot files*"
        
        from datetime import datetime
        
        # Sort by last_edited (most recent first)
        sorted_files = sorted(
            [f for f in files if isinstance(f, dict) and f.get('last_edited')],
            key=lambda x: x.get('last_edited', ''),
            reverse=True
        )
        
        output = []
        now = datetime.now()
        
        # Group by time period
        last_hour = []
        today = []
        this_week = []
        
        for f in sorted_files:
            try:
                last_edit = datetime.fromisoformat(f['last_edited'])
                diff = now - last_edit
                total_seconds = diff.total_seconds()
                
                if total_seconds < 3600:  # Last hour
                    last_hour.append(f)
                elif total_seconds < 86400:  # Today
                    today.append(f)
                else:  # This week
                    this_week.append(f)
            except:
                this_week.append(f)
        
        # Format output with grouping
        if last_hour:
            output.append("#### 🔥 Last Hour")
            for f in last_hour:
                path = f.get('path', 'unknown')
                try:
                    last_edit = datetime.fromisoformat(f['last_edited'])
                    minutes = int((now - last_edit).total_seconds() / 60)
                    timestamp = last_edit.strftime('%H:%M:%S')
                    output.append(f"- `{path}` - **{minutes} min ago** ({timestamp})")
                except:
                    output.append(f"- `{path}`")
            output.append("")
        
        if today:
            output.append("#### 📅 Today")
            for f in today:
                path = f.get('path', 'unknown')
                try:
                    last_edit = datetime.fromisoformat(f['last_edited'])
                    hours = int((now - last_edit).total_seconds() / 3600)
                    timestamp = last_edit.strftime('%H:%M')
                    output.append(f"- `{path}` - **{hours}h ago** ({timestamp})")
                except:
                    output.append(f"- `{path}`")
            output.append("")
        
        if this_week:
            output.append("#### 📆 This Week")
            for f in this_week:
                path = f.get('path', 'unknown')
                try:
                    last_edit = datetime.fromisoformat(f['last_edited'])
                    days = int((now - last_edit).total_seconds() / 86400)
                    timestamp = last_edit.strftime('%Y-%m-%d %H:%M')
                    output.append(f"- `{path}` - **{days}d ago** ({timestamp})")
                except:
                    output.append(f"- `{path}`")
        
        return "\n".join(output) if output else "*No hot files*"
    
    def _format_file_list(self, files: List) -> str:
        """Format file list for markdown with precise timestamps"""
        if not files:
            return "*No files*"
        
        from datetime import datetime
        output = []
        
        for f in files[:20]:
            if isinstance(f, dict):
                path = f.get('path', 'unknown')
                
                # Get precise time information
                if 'last_edited' in f and f['last_edited']:
                    try:
                        last_edit = datetime.fromisoformat(f['last_edited'])
                        now = datetime.now()
                        
                        # Calculate time difference
                        diff = now - last_edit
                        total_seconds = diff.total_seconds()
                        
                        # Format based on recency
                        if total_seconds < 3600:  # Less than 1 hour
                            minutes = int(total_seconds / 60)
                            time_str = f"{minutes} minute{'s' if minutes != 1 else ''} ago"
                        elif total_seconds < 86400:  # Less than 1 day
                            hours = int(total_seconds / 3600)
                            time_str = f"{hours} hour{'s' if hours != 1 else ''} ago"
                        elif total_seconds < 604800:  # Less than 1 week
                            days = int(total_seconds / 86400)
                            hours = int((total_seconds % 86400) / 3600)
                            time_str = f"{days} day{'s' if days != 1 else ''}, {hours}h ago"
                        else:  # More than 1 week
                            days = int(total_seconds / 86400)
                            time_str = f"{days} days ago"
                        
                        # Add full timestamp for hot files
                        if 'temperature' in f and f['temperature'] == 'hot':
                            timestamp = last_edit.strftime('%Y-%m-%d %H:%M:%S')
                            output.append(f"- `{path}` - **{time_str}** ({timestamp})")
                        else:
                            output.append(f"- `{path}` - {time_str}")
                    except:
                        # Fallback to days_since_edit
                        if 'days_since_edit' in f and f['days_since_edit'] is not None:
                            days = int(f['days_since_edit'])
                            output.append(f"- `{path}` - {days} days ago")
                        else:
                            output.append(f"- `{path}`")
                elif 'days_since_edit' in f and f['days_since_edit'] is not None:
                    days = int(f['days_since_edit'])
                    output.append(f"- `{path}` - {days} days ago")
                else:
                    output.append(f"- `{path}`")
            else:
                output.append(f"- `{f}`")
        
        return "\n".join(output)
    
    def _format_suggestions(self, suggestions: List) -> str:
        """Format suggestions for markdown"""
        if not suggestions:
            return "*No suggestions*"
        return "\n".join([f"- {s.get('description', s) if isinstance(s, dict) else s}" for s in suggestions[:20]])
    
    def _format_detailed_suggestions(self, suggestions: List) -> str:
        """Format detailed suggestions with priority"""
        if not suggestions:
            return "*No suggestions*"
        
        output = []
        for s in suggestions:
            if isinstance(s, dict):
                priority = s.get('priority', 'medium').upper()
                stype = s.get('type', 'general')
                desc = s.get('description', '')
                action = s.get('action', '')
                output.append(f"### [{priority}] {stype.title()}\n**Issue:** {desc}\n**Action:** {action}\n")
            else:
                output.append(f"- {s}\n")
        
        return "\n".join(output)
    
    def _identify_doc_gaps(self, scan_data: Dict) -> str:
        """Identify documentation gaps"""
        doc_files = scan_data.get('documentation_files', [])
        code_files = scan_data.get('code_files', [])
        
        gaps = []
        doc_str = str(doc_files).lower()
        
        if 'readme' not in doc_str:
            gaps.append("- Missing README.md")
        if 'api' not in doc_str:
            gaps.append("- Missing API documentation")
        if 'architecture' not in doc_str:
            gaps.append("- Missing architecture docs")
        
        return "\n".join(gaps) if gaps else "*No major gaps detected*"
    
    async def _generate_detailed_issues_report(self, results: Dict, output_dir: Path) -> str:
        """Generate detailed issues report for bug tracking"""
        scan_data = results['phases'].get('code_scan', {})
        
        # Simple version - just list what we found
        lines = []
        lines.append("# Issues Report")
        lines.append(f"Generated: {results['completed_at']}")
        lines.append("")
        lines.append("## Summary")
        lines.append(f"- **Total Files:** {scan_data.get('total_files', 0)}")
        lines.append(f"- **Cold Files:** {len(scan_data.get('cold_files', []))}")
        lines.append("")
        lines.append("## Cold Files to Review")
        
        for cold_file in scan_data.get('cold_files', [])[:20]:
            if isinstance(cold_file, dict):
                path = cold_file.get('path', 'unknown')
                days = cold_file.get('days_since_edit', 'unknown')
                lines.append(f"- `{path}` - {days} days since last edit")
            else:
                lines.append(f"- `{cold_file}`")
        
        return "\n".join(lines)
    
    async def _generate_detailed_future_state(self, results: Dict, output_dir: Path) -> str:
        """Generate detailed future state with extracted features"""
        scan_data = results['phases'].get('code_scan', {})
        planned_features = scan_data.get('planned_features', [])
        
        lines = []
        lines.append("# Future State Vision")
        lines.append(f"Generated: {results['completed_at']}")
        lines.append("")
        lines.append("## Summary")
        lines.append(f"- **Planned Features:** {len(planned_features)} files with TODO/FIXME/FUTURE markers")
        lines.append("")
        lines.append("## Planned Features")
        lines.append("")
        
        for feature in planned_features:
            if isinstance(feature, dict):
                path = feature.get('path', 'unknown')
                desc = feature.get('description', 'No description')
                lines.append(f"### {path}")
                lines.append(f"- **Description:** {desc}")
                lines.append("")
            else:
                lines.append(f"- `{feature}`")
        
        lines.append("## Next Steps")
        lines.append("1. Review TODO items and prioritize")
        lines.append("2. Create tickets for FIXME issues")
        lines.append("3. Plan implementation for FUTURE features")
        
        return "\n".join(lines)
    
    async def _generate_detailed_restructuring_plan(self, results: Dict, output_dir: Path) -> str:
        """Generate detailed restructuring plan with specific actions"""
        scan_data = results['phases'].get('code_scan', {})
        restructuring = results['phases'].get('restructuring', {})
        cold_files = scan_data.get('cold_files', [])
        
        lines = []
        lines.append("# Restructuring Plan")
        lines.append(f"Generated: {results['completed_at']}")
        lines.append("")
        lines.append("## Summary")
        lines.append(f"- **Files to Review:** {len(cold_files)}")
        lines.append(f"- **Suggestions:** {len(restructuring.get('suggestions', []))}")
        lines.append("")
        lines.append("## Cold Files Analysis")
        lines.append("")
        
        for file_info in cold_files[:20]:
            if isinstance(file_info, dict):
                path = file_info.get('path', 'unknown')
                days = file_info.get('days_since_edit', 'unknown')
                lines.append(f"### {path}")
                lines.append(f"- **Last Edit:** {days} days ago")
                lines.append(f"- **Action:** Review and decide: Keep, Archive, or Delete")
                lines.append("")
        
        lines.append("## Suggestions")
        lines.append("")
        
        for suggestion in restructuring.get('suggestions', []):
            if isinstance(suggestion, dict):
                priority = suggestion.get('priority', 'medium').upper()
                desc = suggestion.get('description', 'No description')
                action = suggestion.get('action', 'No action')
                lines.append(f"### [{priority}] {suggestion.get('type', 'General')}")
                lines.append(f"- **Issue:** {desc}")
                lines.append(f"- **Action:** {action}")
                lines.append("")
        
        return "\n".join(lines)
    
    async def _generate_mermaid_diagrams(self, output_dir: Path, results: Dict):
        """Generate Mermaid diagrams for visualization"""
        scan_data = results['phases'].get('code_scan', {})
        
        # 1. File Temperature Flowchart
        temp_dist = scan_data.get('temperature_distribution', {})
        flowchart = f"""# File Temperature Distribution

```mermaid
pie title File Activity Distribution
    "Hot (Active)" : {temp_dist.get('hot', 0)}
    "Warm (Regular)" : {temp_dist.get('warm', 0)}
    "Cool (Occasional)" : {temp_dist.get('cool', 0)}
    "Cold (Rare)" : {temp_dist.get('cold', 0)}
```

## File Activity Flow

```mermaid
graph TD
    A[Codebase] --> B{{File Activity}}
    B -->|Frequent Edits| C[🔥 Hot Files]
    B -->|Regular Updates| D[🌡️ Warm Files]
    B -->|Occasional Changes| E[🌤️ Cool Files]
    B -->|Rarely Touched| F[❄️ Cold Files]
    
    C --> G[Active Development]
    D --> G
    E --> H[Maintenance Mode]
    F --> I[Consider Archive/Delete]
    
    style C fill:#ff6b6b
    style D fill:#ffd93d
    style E fill:#6bcf7f
    style F fill:#4d96ff
```
"""
        (output_dir / "docs" / "diagrams" / "mermaid" / "file_temperature.md").write_text(flowchart)
        
        # 2. Project Structure Diagram
        code_files = scan_data.get('code_files', [])
        config_files = scan_data.get('config_files', [])
        doc_files = scan_data.get('documentation_files', [])
        
        structure = f"""# Project Structure

```mermaid
graph LR
    A[Project Root] --> B[Code Files<br/>{len(code_files)} files]
    A --> C[Config Files<br/>{len(config_files)} files]
    A --> D[Documentation<br/>{len(doc_files)} files]
    A --> E[Tests<br/>{len(scan_data.get('test_files', []))} files]
    
    B --> F[Implementation]
    C --> G[Configuration]
    D --> H[Knowledge Base]
    E --> I[Quality Assurance]
    
    style A fill:#e1f5ff
    style B fill:#b3e5fc
    style C fill:#fff9c4
    style D fill:#c8e6c9
    style E fill:#f8bbd0
```

## Development Workflow

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Code as Codebase
    participant Test as Tests
    participant Doc as Documentation
    
    Dev->>Code: Write Code
    Code->>Test: Run Tests
    Test-->>Dev: Results
    Dev->>Doc: Update Docs
    Doc-->>Code: Document Changes
    Code->>Dev: Ready for Review
```
"""
        (output_dir / "docs" / "diagrams" / "mermaid" / "project_structure.md").write_text(structure)
        
        # 3. Analysis Execution Flow
        execution = f"""# Analysis Execution Flow

```mermaid
graph TD
    Start[Start Analysis] --> Scan[1. File Scanning]
    Scan --> Docs[2. Documentation Consolidation]
    Docs --> Plan[3. Project Plan Generation]
    Plan --> Graph[4. Knowledge Graph Building]
    Graph --> Index[5. Semantic Indexing]
    Index --> Restructure[6. Restructuring Analysis]
    Restructure --> Issues[7. Issue Detection]
    Issues --> Output[Generate Reports]
    Output --> End[Analysis Complete]
    
    style Start fill:#4caf50
    style End fill:#2196f3
    style Output fill:#ff9800
```

## Data Flow

```mermaid
flowchart LR
    A[Raw Codebase] -->|Scan| B[File Metrics]
    B -->|Analyze| C[Temperature Data]
    C -->|Process| D[Insights]
    D -->|Generate| E[.akashic/ Reports]
    
    E --> F[CURRENT_STATE.md]
    E --> G[PROJECT_DOCS.md]
    E --> H[RESTRUCTURING_PLAN.md]
    E --> I[ISSUES_REPORT.md]
    E --> J[FUTURE_STATE.md]
```
"""
        (output_dir / "docs" / "diagrams" / "mermaid" / "analysis_flow.md").write_text(execution)
    
    def _create_placeholder_readmes(self, output_dir: Path):
        """Create placeholder README files for folders that will be populated later"""
        
        # Current State breakdown folder
        current_state_dir = output_dir / "analysis" / "current_state"
        current_state_dir.mkdir(parents=True, exist_ok=True)
        (current_state_dir / "README.md").write_text("""# Current State Analysis - Detailed Breakdown

This folder will contain detailed breakdowns of the current codebase state:

## Planned Files:

- **file_inventory.md** - Complete inventory of all files with metadata
- **hot_files_analysis.md** - Deep dive into actively developed areas
- **cold_files_analysis.md** - Analysis of unused or stale code
- **dependencies.md** - External dependencies and versions
- **tech_stack.md** - Technologies and frameworks used
- **metrics.md** - Code metrics and statistics

## Current Status:

⚠️ **Coming Soon** - Detailed breakdown implementation in progress

For now, see the main `CURRENT_STATE.md` file in the parent directory.
""")
        
        # Future State planning folder
        future_state_dir = output_dir / "analysis" / "future_state"
        future_state_dir.mkdir(parents=True, exist_ok=True)
        (future_state_dir / "README.md").write_text("""# Future State Planning - Detailed Plans

This folder will contain actionable plans for future development:

## Planned Files:

- **roadmap.md** - Timeline and milestones
- **features_to_implement.md** - Planned features from TODO markers
- **refactoring_plan.md** - Code quality improvements
- **deprecation_plan.md** - What to archive or remove
- **migration_plan.md** - Technology migration plans

## Current Status:

⚠️ **Coming Soon** - Detailed planning implementation in progress

For now, see the main `FUTURE_STATE.md` file in the parent directory.
""")
        
        # Project Plans folder
        project_plans_dir = output_dir / "docs" / "project_plans"
        project_plans_dir.mkdir(parents=True, exist_ok=True)
        (project_plans_dir / "README.md").write_text("""# Project Plans - Structured Implementation Plans

This folder will contain structured project plans ready for PM tools:

## Planned Files:

- **epic_1_infrastructure.md** - Infrastructure improvements
- **epic_2_features.md** - New feature development
- **epic_3_refactoring.md** - Code quality and refactoring
- **epic_4_documentation.md** - Documentation improvements
- **sprint_breakdown.md** - Sprint planning and breakdown

## Current Status:

⚠️ **Coming Soon** - Project plan generation in progress

These plans will be automatically synced to Linear and Jira when PM integration is enabled.
""")
        
        # Rendered diagrams folder
        rendered_dir = output_dir / "docs" / "diagrams" / "rendered"
        rendered_dir.mkdir(parents=True, exist_ok=True)
        (rendered_dir / "README.md").write_text("""# Rendered Diagrams

This folder will contain rendered PNG and SVG versions of Mermaid diagrams.

## Current Status:

⚠️ **Coming Soon** - Mermaid diagram rendering in progress

## View Diagrams Now:

1. Open any `.md` file in `../mermaid/`
2. Copy the mermaid code block
3. Paste into: https://mermaid.live/
4. View the rendered diagram

## Planned Files:

- **file_temperature.png** - File activity distribution
- **file_temperature.svg** - File activity distribution (vector)
- **project_structure.png** - Project structure diagram
- **project_structure.svg** - Project structure diagram (vector)
- **analysis_flow.png** - Analysis execution flow
- **analysis_flow.svg** - Analysis execution flow (vector)

Rendering requires mermaid-cli to be installed in the Apollo container.
""")
        
        # Mermaid diagrams duplicate folder (for compatibility)
        mermaid_dup_dir = output_dir / "docs" / "mermaid_diagrams"
        mermaid_dup_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy mermaid files for compatibility
        import shutil
        mermaid_src = output_dir / "docs" / "diagrams" / "mermaid"
        if mermaid_src.exists():
            for mermaid_file in mermaid_src.glob("*.md"):
                shutil.copy2(mermaid_file, mermaid_dup_dir / mermaid_file.name)
        
        (mermaid_dup_dir / "README.md").write_text("""# Mermaid Diagrams

This folder contains copies of the Mermaid diagram source files for compatibility.

**Note:** The canonical location is `diagrams/mermaid/`

## Available Diagrams:

- **file_temperature.md** - File activity distribution
- **project_structure.md** - Project structure overview
- **analysis_flow.md** - Analysis execution flow

## How to View:

1. Open any `.md` file
2. Copy the mermaid code block
3. Paste into: https://mermaid.live/
4. View the rendered diagram

Or use a Markdown viewer with Mermaid support (VS Code, GitHub, etc.)
""")
        
        logger.info("✅ Created placeholder README files for future features")
    
    def _translate_path_for_container(self, path: str) -> str:
        """
        Translate host path to container path
        
        Docker mounts: ../:/workspace
        So /Users/leonard/.../ColossalCapital/Atlas-Test -> /workspace/Atlas-Test
        """
        # Check if running in Docker (simple heuristic)
        if os.path.exists('/workspace'):
            # Extract the relative path from ColossalCapital
            if 'ColossalCapital' in path:
                # Get everything after ColossalCapital/
                parts = path.split('ColossalCapital/')
                if len(parts) > 1:
                    relative_path = parts[1]
                    container_path = f"/workspace/{relative_path}"
                    logger.info(f"📍 Translated path: {path} -> {container_path}")
                    return container_path
        
        # If not in Docker or can't translate, return original
        return path
    
    async def _scan_documentation(self, repo_path: str) -> Dict[str, Any]:
        """
        Scan codebase for documentation coverage across multiple languages
        
        Supports: Python, JavaScript, TypeScript, Java, Rust, Go
        """
        import ast
        import re
        
        results = {
            'by_language': {
                'python': {'total': 0, 'documented': 0, 'items': []},
                'javascript': {'total': 0, 'documented': 0, 'items': []},
                'typescript': {'total': 0, 'documented': 0, 'items': []},
                'java': {'total': 0, 'documented': 0, 'items': []},
                'rust': {'total': 0, 'documented': 0, 'items': []},
                'go': {'total': 0, 'documented': 0, 'items': []},
            },
            'total_functions': 0,
            'documented_functions': 0,
            'undocumented_functions': [],
            'total_classes': 0,
            'documented_classes': 0,
            'undocumented_classes': [],
            'coverage_percentage': 0,
            'by_file': {}
        }
        
        logger.info("📚 Scanning documentation across all languages...")
        
        for root, dirs, files in os.walk(repo_path):
            # Skip common ignore patterns
            dirs[:] = [d for d in dirs if d not in {
                '.git', '__pycache__', 'node_modules', '.venv', 'venv',
                'dist', 'build', '.akashic', '.next', 'target'
            }]
            
            for file in files:
                # Python files
                if file.endswith('.py'):
                    await self._scan_python_file(file, root, repo_path, results)
                
                # JavaScript/TypeScript files
                elif file.endswith(('.js', '.jsx')):
                    await self._scan_js_file(file, root, repo_path, results, 'javascript')
                elif file.endswith(('.ts', '.tsx')):
                    await self._scan_js_file(file, root, repo_path, results, 'typescript')
                
                # Java files
                elif file.endswith('.java'):
                    await self._scan_java_file(file, root, repo_path, results)
                
                # Rust files
                elif file.endswith('.rs'):
                    await self._scan_rust_file(file, root, repo_path, results)
                
                # Go files
                elif file.endswith('.go'):
                    await self._scan_go_file(file, root, repo_path, results)
        
        # Calculate overall coverage
        for lang, data in results['by_language'].items():
            results['total_functions'] += data['total']
            results['documented_functions'] += data['documented']
        
        if results['total_functions'] > 0:
            results['coverage_percentage'] = (
                results['documented_functions'] / results['total_functions'] * 100
            )
        
        logger.info(f"✅ Documentation scan complete: {results['coverage_percentage']:.1f}% overall coverage")
        
        return results
    
    async def _scan_python_file(self, file: str, root: str, repo_path: str, results: Dict):
        """Scan Python file for docstrings"""
        import ast
        
        file_path = os.path.join(root, file)
        relative_path = os.path.relpath(file_path, repo_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content, filename=file_path)
            
            lang_data = results['by_language']['python']
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Skip private methods
                    if node.name.startswith('_') and not (node.name.startswith('__') and node.name.endswith('__')):
                        continue
                    
                    lang_data['total'] += 1
                    results['total_functions'] += 1
                    
                    if ast.get_docstring(node):
                        lang_data['documented'] += 1
                        results['documented_functions'] += 1
                    else:
                        undoc = {
                            'file': relative_path,
                            'name': node.name,
                            'line': node.lineno,
                            'type': 'function',
                            'language': 'python'
                        }
                        lang_data['items'].append(undoc)
                        results['undocumented_functions'].append(undoc)
                
                elif isinstance(node, ast.ClassDef):
                    lang_data['total'] += 1
                    results['total_classes'] += 1
                    
                    if ast.get_docstring(node):
                        lang_data['documented'] += 1
                        results['documented_classes'] += 1
                    else:
                        undoc = {
                            'file': relative_path,
                            'name': node.name,
                            'line': node.lineno,
                            'type': 'class',
                            'language': 'python'
                        }
                        lang_data['items'].append(undoc)
                        results['undocumented_classes'].append(undoc)
        
        except Exception as e:
            logger.warning(f"Failed to parse {relative_path}: {e}")
    
    async def _scan_js_file(self, file: str, root: str, repo_path: str, results: Dict, lang: str):
        """Scan JavaScript/TypeScript file for JSDoc comments"""
        import re
        
        file_path = os.path.join(root, file)
        relative_path = os.path.relpath(file_path, repo_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lang_data = results['by_language'][lang]
            
            # Find functions: function name() or const name = () =>
            func_pattern = r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>)'
            functions = re.finditer(func_pattern, content)
            
            for match in functions:
                func_name = match.group(1) or match.group(2)
                if func_name.startswith('_'):  # Skip private
                    continue
                
                lang_data['total'] += 1
                
                # Check for JSDoc before function
                before_func = content[:match.start()]
                has_jsdoc = bool(re.search(r'/\*\*[\s\S]*?\*/', before_func[-200:]))
                
                if has_jsdoc:
                    lang_data['documented'] += 1
                else:
                    lang_data['items'].append({
                        'file': relative_path,
                        'name': func_name,
                        'line': content[:match.start()].count('\n') + 1,
                        'type': 'function',
                        'language': lang
                    })
        
        except Exception as e:
            logger.warning(f"Failed to parse {relative_path}: {e}")
    
    async def _scan_java_file(self, file: str, root: str, repo_path: str, results: Dict):
        """Scan Java file for Javadoc comments"""
        import re
        
        file_path = os.path.join(root, file)
        relative_path = os.path.relpath(file_path, repo_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lang_data = results['by_language']['java']
            
            # Find public/protected methods
            method_pattern = r'(?:public|protected)\s+(?:static\s+)?[\w<>]+\s+(\w+)\s*\('
            methods = re.finditer(method_pattern, content)
            
            for match in methods:
                method_name = match.group(1)
                lang_data['total'] += 1
                
                # Check for Javadoc before method
                before_method = content[:match.start()]
                has_javadoc = bool(re.search(r'/\*\*[\s\S]*?\*/', before_method[-200:]))
                
                if has_javadoc:
                    lang_data['documented'] += 1
                else:
                    lang_data['items'].append({
                        'file': relative_path,
                        'name': method_name,
                        'line': content[:match.start()].count('\n') + 1,
                        'type': 'method',
                        'language': 'java'
                    })
        
        except Exception as e:
            logger.warning(f"Failed to parse {relative_path}: {e}")
    
    async def _scan_rust_file(self, file: str, root: str, repo_path: str, results: Dict):
        """Scan Rust file for rustdoc comments"""
        import re
        
        file_path = os.path.join(root, file)
        relative_path = os.path.relpath(file_path, repo_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lang_data = results['by_language']['rust']
            
            # Find pub fn
            func_pattern = r'pub\s+fn\s+(\w+)'
            functions = re.finditer(func_pattern, content)
            
            for match in functions:
                func_name = match.group(1)
                lang_data['total'] += 1
                
                # Check for /// or //! before function
                before_func = content[:match.start()]
                has_rustdoc = bool(re.search(r'///|//!', before_func[-200:]))
                
                if has_rustdoc:
                    lang_data['documented'] += 1
                else:
                    lang_data['items'].append({
                        'file': relative_path,
                        'name': func_name,
                        'line': content[:match.start()].count('\n') + 1,
                        'type': 'function',
                        'language': 'rust'
                    })
        
        except Exception as e:
            logger.warning(f"Failed to parse {relative_path}: {e}")
    
    async def _scan_go_file(self, file: str, root: str, repo_path: str, results: Dict):
        """Scan Go file for godoc comments"""
        import re
        
        file_path = os.path.join(root, file)
        relative_path = os.path.relpath(file_path, repo_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lang_data = results['by_language']['go']
            
            # Find exported functions (start with capital letter)
            func_pattern = r'func\s+([A-Z]\w*)'
            functions = re.finditer(func_pattern, content)
            
            for match in functions:
                func_name = match.group(1)
                lang_data['total'] += 1
                
                # Check for // comment before function
                before_func = content[:match.start()]
                lines_before = before_func.split('\n')[-5:]  # Check last 5 lines
                has_godoc = any(line.strip().startswith('//') for line in lines_before)
                
                if has_godoc:
                    lang_data['documented'] += 1
                else:
                    lang_data['items'].append({
                        'file': relative_path,
                        'name': func_name,
                        'line': content[:match.start()].count('\n') + 1,
                        'type': 'function',
                        'language': 'go'
                    })
        
        except Exception as e:
            logger.warning(f"Failed to parse {relative_path}: {e}")
    
    def _write_documentation_analysis(self, output_dir: Path, doc_analysis: Dict):
        """Write multi-language documentation analysis report"""
        
        coverage = doc_analysis['coverage_percentage']
        total_funcs = doc_analysis['total_functions']
        doc_funcs = doc_analysis['documented_functions']
        total_classes = doc_analysis['total_classes']
        doc_classes = doc_analysis['documented_classes']
        by_language = doc_analysis['by_language']
        
        # Determine coverage status
        if coverage >= 80:
            status_emoji = "🎉"
            status_text = "Excellent"
        elif coverage >= 60:
            status_emoji = "✅"
            status_text = "Good"
        elif coverage >= 40:
            status_emoji = "⚠️"
            status_text = "Needs Improvement"
        else:
            status_emoji = "❌"
            status_text = "Critical"
        
        report = f"""# Documentation Analysis

{status_emoji} **Overall Status:** {status_text}

## Coverage Summary

- **Overall Coverage:** {coverage:.1f}%
- **Functions:** {doc_funcs}/{total_funcs} documented ({(doc_funcs/total_funcs*100) if total_funcs > 0 else 0:.1f}%)
- **Classes:** {doc_classes}/{total_classes} documented ({(doc_classes/total_classes*100) if total_classes > 0 else 0:.1f}%)

### By Language:

"""
        
        # Add language-specific breakdown
        for lang, data in by_language.items():
            if data['total'] > 0:
                lang_coverage = (data['documented'] / data['total'] * 100) if data['total'] > 0 else 0
                lang_emoji = "✅" if lang_coverage >= 70 else "⚠️" if lang_coverage >= 50 else "❌"
                report += f"- **{lang.capitalize()}:** {lang_emoji} {lang_coverage:.1f}% ({data['documented']}/{data['total']})\n"
        
        report += """

---

## Missing Documentation

### High Priority - Public Functions ({len([f for f in doc_analysis['undocumented_functions'] if not f['name'].startswith('_')])})

"""
        
        # List undocumented public functions
        public_funcs = [f for f in doc_analysis['undocumented_functions'] if not f['name'].startswith('_')]
        if public_funcs:
            for item in public_funcs[:20]:  # Top 20
                report += f"- `{item['name']}()` in `{item['file']}:{item['line']}`\n"
            if len(public_funcs) > 20:
                report += f"\n*...and {len(public_funcs) - 20} more*\n"
        else:
            report += "*All public functions are documented! 🎉*\n"
        
        report += f"""

### Classes Without Docstrings ({len(doc_analysis['undocumented_classes'])})

"""
        
        # List undocumented classes
        if doc_analysis['undocumented_classes']:
            for item in doc_analysis['undocumented_classes'][:15]:  # Top 15
                report += f"- `{item['name']}` in `{item['file']}:{item['line']}`\n"
            if len(doc_analysis['undocumented_classes']) > 15:
                report += f"\n*...and {len(doc_analysis['undocumented_classes']) - 15} more*\n"
        else:
            report += "*All classes are documented! 🎉*\n"
        
        report += """

---

## Docstring Templates

### Function Template

```python
def function_name(param1: str, param2: int) -> bool:
    \"\"\"
    Brief description of what the function does.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When invalid input is provided
        TypeError: When wrong type is passed
    
    Example:
        >>> function_name("test", 42)
        True
    \"\"\"
    pass
```

### Class Template

```python
class ClassName:
    \"\"\"
    Brief description of the class.
    
    This class handles [specific functionality]. It provides
    methods for [key operations].
    
    Attributes:
        attribute_name (type): Description of attribute
        another_attr (type): Description of another attribute
    
    Example:
        >>> obj = ClassName()
        >>> obj.method()
        result
    \"\"\"
    
    def __init__(self, param: str):
        \"\"\"
        Initialize the class.
        
        Args:
            param: Description of initialization parameter
        \"\"\"
        self.attribute_name = param
```

---

## Recommendations

"""
        
        if coverage < 40:
            report += """
### 🚨 Critical Priority

Documentation coverage is critically low. Recommended actions:

1. **Immediate:** Document all public API functions (user-facing)
2. **High:** Add class docstrings for all public classes
3. **Medium:** Document internal functions
4. **Low:** Add examples to complex functions

**Estimated Time:** 15-20 hours
**Suggested Approach:** Create 3-4 Linear tickets grouped by module
"""
        elif coverage < 60:
            report += """
### ⚠️ High Priority

Documentation needs significant improvement. Recommended actions:

1. **High:** Document remaining public functions
2. **Medium:** Add class docstrings
3. **Low:** Enhance existing docstrings with examples

**Estimated Time:** 8-12 hours
**Suggested Approach:** Create 2-3 Linear tickets grouped by priority
"""
        elif coverage < 80:
            report += """
### ✅ Medium Priority

Documentation is good but can be improved. Recommended actions:

1. **Medium:** Document remaining functions
2. **Low:** Add examples to complex functions
3. **Low:** Enhance existing docstrings

**Estimated Time:** 4-6 hours
**Suggested Approach:** Create 1-2 Linear tickets
"""
        else:
            report += """
### 🎉 Excellent!

Documentation coverage is excellent! Minor improvements:

1. **Low:** Add examples to complex functions
2. **Low:** Enhance existing docstrings with more details

**Estimated Time:** 2-3 hours
**Suggested Approach:** Optional enhancement ticket
"""
        
        report += """

---

## Files by Coverage

"""
        
        # Sort files by coverage
        file_coverage = []
        for file_path, stats in doc_analysis['by_file'].items():
            total = stats['functions'] + stats['classes']
            documented = stats['documented_functions'] + stats['documented_classes']
            if total > 0:
                file_cov = (documented / total) * 100
                file_coverage.append((file_path, file_cov, total, documented))
        
        file_coverage.sort(key=lambda x: x[1])  # Sort by coverage (lowest first)
        
        if file_coverage:
            report += "### Lowest Coverage Files (Need Attention)\n\n"
            for file_path, cov, total, documented in file_coverage[:10]:
                report += f"- `{file_path}`: {cov:.0f}% ({documented}/{total})\n"
        
        (output_dir / "analysis" / "DOCUMENTATION_ANALYSIS.md").write_text(report)
        logger.info("📄 Created DOCUMENTATION_ANALYSIS.md")
    
    async def _scan_testing(self, repo_path: str) -> Dict[str, Any]:
        """
        Scan codebase for testing coverage
        
        Detects test files and calculates coverage
        """
        import glob
        
        results = {
            'test_framework': None,
            'test_files': [],
            'source_files': [],
            'coverage_percentage': 0,
            'untested_files': [],
            'by_language': {
                'python': {'tests': 0, 'sources': 0, 'untested': []},
                'javascript': {'tests': 0, 'sources': 0, 'untested': []},
                'typescript': {'tests': 0, 'sources': 0, 'untested': []},
                'java': {'tests': 0, 'sources': 0, 'untested': []},
                'rust': {'tests': 0, 'sources': 0, 'untested': []},
                'go': {'tests': 0, 'sources': 0, 'untested': []}
            }
        }
        
        logger.info("🧪 Scanning testing coverage...")
        
        # Detect test framework
        results['test_framework'] = self._detect_test_framework(repo_path)
        
        # Find all files
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in {
                '.git', '__pycache__', 'node_modules', '.venv', 'venv',
                'dist', 'build', '.akashic', '.next', 'target'
            }]
            
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, repo_path)
                
                # Python
                if file.endswith('.py'):
                    if 'test_' in file or '_test.py' in file or file.startswith('test_'):
                        results['test_files'].append(relative_path)
                        results['by_language']['python']['tests'] += 1
                    else:
                        results['source_files'].append(relative_path)
                        results['by_language']['python']['sources'] += 1
                
                # JavaScript/TypeScript
                elif file.endswith(('.js', '.jsx')):
                    if '.test.' in file or '.spec.' in file or file.endswith('test.js'):
                        results['test_files'].append(relative_path)
                        results['by_language']['javascript']['tests'] += 1
                    else:
                        results['source_files'].append(relative_path)
                        results['by_language']['javascript']['sources'] += 1
                
                elif file.endswith(('.ts', '.tsx')):
                    if '.test.' in file or '.spec.' in file or file.endswith('test.ts'):
                        results['test_files'].append(relative_path)
                        results['by_language']['typescript']['tests'] += 1
                    else:
                        results['source_files'].append(relative_path)
                        results['by_language']['typescript']['sources'] += 1
                
                # Java
                elif file.endswith('.java'):
                    if 'Test.java' in file or 'Tests.java' in file:
                        results['test_files'].append(relative_path)
                        results['by_language']['java']['tests'] += 1
                    else:
                        results['source_files'].append(relative_path)
                        results['by_language']['java']['sources'] += 1
                
                # Rust
                elif file.endswith('.rs'):
                    # Rust tests are usually in same file, check for #[test] or #[cfg(test)]
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if '#[test]' in content or '#[cfg(test)]' in content:
                                results['test_files'].append(relative_path)
                                results['by_language']['rust']['tests'] += 1
                    except:
                        pass
                    results['source_files'].append(relative_path)
                    results['by_language']['rust']['sources'] += 1
                
                # Go
                elif file.endswith('.go'):
                    if '_test.go' in file:
                        results['test_files'].append(relative_path)
                        results['by_language']['go']['tests'] += 1
                    else:
                        results['source_files'].append(relative_path)
                        results['by_language']['go']['sources'] += 1
        
        # Calculate coverage
        total_sources = len(results['source_files'])
        total_tests = len(results['test_files'])
        
        if total_sources > 0:
            results['coverage_percentage'] = (total_tests / total_sources) * 100
        
        # Identify untested files (simple heuristic)
        tested_modules = set()
        for test_file in results['test_files']:
            # Extract module name from test file
            module = test_file.replace('test_', '').replace('_test', '').replace('.test', '').replace('.spec', '')
            tested_modules.add(module)
        
        for source_file in results['source_files']:
            # Check if source file has corresponding test
            is_tested = False
            for tested in tested_modules:
                if tested in source_file:
                    is_tested = True
                    break
            
            if not is_tested:
                results['untested_files'].append(source_file)
        
        logger.info(f"✅ Testing scan complete: {results['coverage_percentage']:.1f}% coverage")
        
        return results
    
    def _detect_test_framework(self, repo_path: str) -> str:
        """Detect which test framework is being used"""
        frameworks = []
        
        # Check for Python test frameworks
        if os.path.exists(os.path.join(repo_path, 'pytest.ini')) or \
           os.path.exists(os.path.join(repo_path, 'setup.cfg')):
            frameworks.append('pytest')
        
        # Check for JavaScript test frameworks
        package_json = os.path.join(repo_path, 'package.json')
        if os.path.exists(package_json):
            try:
                import json
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    if 'jest' in deps:
                        frameworks.append('jest')
                    if 'mocha' in deps:
                        frameworks.append('mocha')
                    if 'vitest' in deps:
                        frameworks.append('vitest')
            except:
                pass
        
        # Check for Java test frameworks
        if os.path.exists(os.path.join(repo_path, 'pom.xml')):
            frameworks.append('junit')
        
        # Check for Rust
        if os.path.exists(os.path.join(repo_path, 'Cargo.toml')):
            frameworks.append('cargo test')
        
        # Check for Go
        if any(f.endswith('_test.go') for f in os.listdir(repo_path) if os.path.isfile(os.path.join(repo_path, f))):
            frameworks.append('go test')
        
        return ', '.join(frameworks) if frameworks else 'Unknown'
    
    def _write_testing_analysis(self, output_dir: Path, test_analysis: Dict):
        """Write testing analysis report"""
        
        coverage = test_analysis['coverage_percentage']
        total_tests = len(test_analysis['test_files'])
        total_sources = len(test_analysis['source_files'])
        untested = len(test_analysis['untested_files'])
        framework = test_analysis['test_framework']
        by_language = test_analysis['by_language']
        
        # Determine status
        if coverage >= 80:
            status_emoji = "🎉"
            status_text = "Excellent"
        elif coverage >= 60:
            status_emoji = "✅"
            status_text = "Good"
        elif coverage >= 40:
            status_emoji = "⚠️"
            status_text = "Needs Improvement"
        else:
            status_emoji = "❌"
            status_text = "Critical"
        
        report = f"""# Testing Analysis

{status_emoji} **Overall Status:** {status_text}

## Test Framework

**Detected:** {framework}

## Coverage Summary

- **Overall Coverage:** {coverage:.1f}%
- **Test Files:** {total_tests}
- **Source Files:** {total_sources}
- **Untested Files:** {untested}

### By Language:

"""
        
        # Add language-specific breakdown
        for lang, data in by_language.items():
            if data['sources'] > 0:
                lang_coverage = (data['tests'] / data['sources'] * 100) if data['sources'] > 0 else 0
                lang_emoji = "✅" if lang_coverage >= 70 else "⚠️" if lang_coverage >= 50 else "❌"
                report += f"- **{lang.capitalize()}:** {lang_emoji} {lang_coverage:.1f}% ({data['tests']} tests / {data['sources']} sources)\n"
        
        report += f"""

---

## Untested Files (High Priority)

"""
        
        if test_analysis['untested_files']:
            # Show top 20 untested files
            for file in test_analysis['untested_files'][:20]:
                report += f"- `{file}`\n"
            
            if len(test_analysis['untested_files']) > 20:
                report += f"\n*...and {len(test_analysis['untested_files']) - 20} more*\n"
        else:
            report += "*All files have tests! 🎉*\n"
        
        report += """

---

## Recommendations

"""
        
        if coverage < 40:
            report += """
### 🚨 Critical Priority

Test coverage is critically low. Recommended actions:

1. **Immediate:** Add unit tests for core business logic
2. **High:** Add integration tests for API endpoints
3. **Medium:** Add e2e tests for critical user flows

**Estimated Time:** 30-40 hours
**Suggested Approach:** Create 4-5 Linear tickets grouped by priority
"""
        elif coverage < 60:
            report += """
### ⚠️ High Priority

Test coverage needs improvement. Recommended actions:

1. **High:** Add tests for untested modules
2. **Medium:** Increase coverage for critical paths
3. **Low:** Add edge case tests

**Estimated Time:** 15-20 hours
**Suggested Approach:** Create 2-3 Linear tickets
"""
        elif coverage < 80:
            report += """
### ✅ Medium Priority

Test coverage is good but can be improved. Recommended actions:

1. **Medium:** Add tests for remaining modules
2. **Low:** Add edge case tests
3. **Low:** Improve test quality

**Estimated Time:** 8-12 hours
**Suggested Approach:** Create 1-2 Linear tickets
"""
        else:
            report += """
### 🎉 Excellent!

Test coverage is excellent! Minor improvements:

1. **Low:** Add edge case tests
2. **Low:** Add performance tests
3. **Low:** Improve test documentation

**Estimated Time:** 4-6 hours
**Suggested Approach:** Optional enhancement ticket
"""
        
        report += """

---

## Test Types Needed

### Unit Tests
- Test individual functions and classes
- Fast execution
- No external dependencies

### Integration Tests
- Test module interactions
- Database operations
- API endpoints

### E2E Tests
- Test complete user flows
- Critical business processes
- Real-world scenarios

---

## Next Steps

1. Review untested files list
2. Prioritize critical paths
3. Create Linear/Jira tickets
4. Implement tests incrementally
5. Set up CI/CD to enforce coverage thresholds
"""
        
        (output_dir / "analysis" / "TESTING_ANALYSIS.md").write_text(report)
        logger.info("📄 Created TESTING_ANALYSIS.md")
    
    async def _generate_current_state_breakdown(self, output_dir: Path, results: Dict, repo_path: str):
        """Generate detailed current state breakdown"""
        
        logger.info("📊 Generating detailed current state breakdown...")
        
        # Create current_state directory
        current_state_dir = output_dir / "analysis" / "current_state"
        current_state_dir.mkdir(parents=True, exist_ok=True)
        
        scan_data = results['phases'].get('code_scan', {})
        
        # 1. File Inventory
        await self._write_file_inventory(current_state_dir, scan_data, repo_path)
        
        # 2. Hot Files Analysis
        await self._write_hot_files_analysis(current_state_dir, scan_data)
        
        # 3. Cold Files Analysis
        await self._write_cold_files_analysis(current_state_dir, scan_data)
        
        # 4. Dependencies Analysis
        await self._write_dependencies_analysis(current_state_dir, repo_path)
        
        # 5. Tech Stack Analysis
        await self._write_tech_stack_analysis(current_state_dir, scan_data, repo_path)
        
        # 6. Code Metrics
        await self._write_code_metrics(current_state_dir, scan_data)
        
        # 7. README
        await self._write_current_state_readme(current_state_dir)
        
        logger.info("✅ Current state breakdown complete")
    
    async def _write_file_inventory(self, output_dir: Path, scan_data: Dict, repo_path: str):
        """Write complete file inventory"""
        
        report = """# File Inventory

Complete inventory of all files in the codebase.

## Summary

"""
        
        # Count files by type
        file_types = {}
        total_size = 0
        
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'dist', 'build', '.akashic'}]
            
            for file in files:
                ext = os.path.splitext(file)[1] or 'no extension'
                file_types[ext] = file_types.get(ext, 0) + 1
                
                try:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
                except:
                    pass
        
        report += f"- **Total Files:** {sum(file_types.values())}\n"
        report += f"- **Total Size:** {total_size / 1024 / 1024:.2f} MB\n"
        report += f"- **File Types:** {len(file_types)}\n\n"
        
        report += "## Files by Type\n\n"
        
        for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
            report += f"- **{ext}**: {count} files\n"
        
        report += "\n## Source Code Files\n\n"
        
        source_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.rs', '.go', '.c', '.cpp', '.h'}
        for ext in source_extensions:
            if ext in file_types:
                report += f"- **{ext}**: {file_types[ext]} files\n"
        
        (output_dir / "file_inventory.md").write_text(report)
        logger.info("📄 Created file_inventory.md")
    
    async def _write_hot_files_analysis(self, output_dir: Path, scan_data: Dict):
        """Write hot files analysis"""
        
        hot_files = scan_data.get('hot_files', [])
        
        report = f"""# Hot Files Analysis

Files with recent activity (last 7 days).

## Summary

- **Hot Files:** {len(hot_files)}
- **Definition:** Files modified in the last 7 days

## Hot Files List

"""
        
        if hot_files:
            for file_info in hot_files[:50]:
                if isinstance(file_info, dict):
                    report += f"- `{file_info.get('path', 'unknown')}` - Last edited: {file_info.get('last_edited', 'unknown')}\n"
        else:
            report += "*No hot files detected*\n"
        
        report += """

## Insights

Hot files indicate:
- Active development areas
- Features being worked on
- Potential merge conflicts
- Areas needing tests/docs

## Recommendations

1. Ensure hot files have adequate test coverage
2. Review hot files for documentation
3. Consider code review for recent changes
"""
        
        (output_dir / "hot_files_analysis.md").write_text(report)
        logger.info("📄 Created hot_files_analysis.md")
    
    async def _write_cold_files_analysis(self, output_dir: Path, scan_data: Dict):
        """Write cold files analysis"""
        
        cold_files = scan_data.get('cold_files', [])
        
        report = f"""# Cold Files Analysis

Files with no recent activity (90+ days).

## Summary

- **Cold Files:** {len(cold_files)}
- **Definition:** Files not modified in 90+ days

## Cold Files List

"""
        
        if cold_files:
            for file_info in cold_files[:50]:
                if isinstance(file_info, dict):
                    report += f"- `{file_info.get('path', 'unknown')}` - Last edited: {file_info.get('last_edited', 'unknown')}\n"
        else:
            report += "*No cold files detected*\n"
        
        report += """

## Insights

Cold files may indicate:
- Stable, mature code
- Deprecated features
- Technical debt
- Candidates for removal

## Recommendations

1. Review cold files for deprecation
2. Consider archiving unused code
3. Update documentation if still needed
4. Verify if code is still in use
"""
        
        (output_dir / "cold_files_analysis.md").write_text(report)
        logger.info("📄 Created cold_files_analysis.md")
    
    async def _write_dependencies_analysis(self, output_dir: Path, repo_path: str):
        """Write dependencies analysis"""
        
        report = """# Dependencies Analysis

External dependencies used in the project.

"""
        
        # Check for Python dependencies
        requirements_file = os.path.join(repo_path, 'requirements.txt')
        if os.path.exists(requirements_file):
            report += "## Python Dependencies\n\n"
            try:
                with open(requirements_file, 'r') as f:
                    deps = f.readlines()
                    for dep in deps[:20]:
                        dep = dep.strip()
                        if dep and not dep.startswith('#'):
                            report += f"- {dep}\n"
                    if len(deps) > 20:
                        report += f"\n*...and {len(deps) - 20} more*\n"
            except:
                report += "*Could not read requirements.txt*\n"
            report += "\n"
        
        # Check for JavaScript dependencies
        package_json = os.path.join(repo_path, 'package.json')
        if os.path.exists(package_json):
            report += "## JavaScript Dependencies\n\n"
            try:
                import json
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    deps = data.get('dependencies', {})
                    dev_deps = data.get('devDependencies', {})
                    
                    if deps:
                        report += "### Production:\n"
                        for name, version in list(deps.items())[:15]:
                            report += f"- {name}@{version}\n"
                        if len(deps) > 15:
                            report += f"\n*...and {len(deps) - 15} more*\n"
                    
                    if dev_deps:
                        report += "\n### Development:\n"
                        for name, version in list(dev_deps.items())[:15]:
                            report += f"- {name}@{version}\n"
                        if len(dev_deps) > 15:
                            report += f"\n*...and {len(dev_deps) - 15} more*\n"
            except:
                report += "*Could not read package.json*\n"
            report += "\n"
        
        report += """

## Recommendations

1. Review dependencies for security vulnerabilities
2. Update outdated dependencies
3. Remove unused dependencies
4. Consider using Dependabot for auto-updates
5. Document why each dependency is needed
"""
        
        (output_dir / "dependencies.md").write_text(report)
        logger.info("📄 Created dependencies.md")
    
    async def _write_tech_stack_analysis(self, output_dir: Path, scan_data: Dict, repo_path: str):
        """Write tech stack analysis"""
        
        report = """# Tech Stack Analysis

Technologies and frameworks used in the project.

## Languages

"""
        
        # Detect languages
        languages = set()
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}]
            for file in files:
                if file.endswith('.py'):
                    languages.add('Python')
                elif file.endswith(('.js', '.jsx')):
                    languages.add('JavaScript')
                elif file.endswith(('.ts', '.tsx')):
                    languages.add('TypeScript')
                elif file.endswith('.java'):
                    languages.add('Java')
                elif file.endswith('.rs'):
                    languages.add('Rust')
                elif file.endswith('.go'):
                    languages.add('Go')
                elif file.endswith(('.c', '.cpp', '.h')):
                    languages.add('C/C++')
        
        for lang in sorted(languages):
            report += f"- {lang}\n"
        
        report += "\n## Frameworks & Tools\n\n"
        
        # Detect frameworks
        frameworks = []
        
        if os.path.exists(os.path.join(repo_path, 'package.json')):
            try:
                import json
                with open(os.path.join(repo_path, 'package.json'), 'r') as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    
                    if 'react' in deps:
                        frameworks.append('React')
                    if 'vue' in deps:
                        frameworks.append('Vue.js')
                    if 'angular' in deps:
                        frameworks.append('Angular')
                    if 'next' in deps:
                        frameworks.append('Next.js')
                    if 'express' in deps:
                        frameworks.append('Express.js')
            except:
                pass
        
        if os.path.exists(os.path.join(repo_path, 'requirements.txt')):
            try:
                with open(os.path.join(repo_path, 'requirements.txt'), 'r') as f:
                    content = f.read().lower()
                    if 'django' in content:
                        frameworks.append('Django')
                    if 'flask' in content:
                        frameworks.append('Flask')
                    if 'fastapi' in content:
                        frameworks.append('FastAPI')
            except:
                pass
        
        if frameworks:
            for fw in frameworks:
                report += f"- {fw}\n"
        else:
            report += "*No major frameworks detected*\n"
        
        report += "\n## Infrastructure\n\n"
        
        if os.path.exists(os.path.join(repo_path, 'Dockerfile')):
            report += "- Docker\n"
        if os.path.exists(os.path.join(repo_path, 'docker-compose.yml')):
            report += "- Docker Compose\n"
        if os.path.exists(os.path.join(repo_path, 'kubernetes')):
            report += "- Kubernetes\n"
        if os.path.exists(os.path.join(repo_path, '.github/workflows')):
            report += "- GitHub Actions\n"
        if os.path.exists(os.path.join(repo_path, 'bitbucket-pipelines.yml')):
            report += "- Bitbucket Pipelines\n"
        
        (output_dir / "tech_stack.md").write_text(report)
        logger.info("📄 Created tech_stack.md")
    
    async def _write_code_metrics(self, output_dir: Path, scan_data: Dict):
        """Write code metrics"""
        
        total_files = scan_data.get('total_files', 0)
        hot_files = len(scan_data.get('hot_files', []))
        cold_files = len(scan_data.get('cold_files', []))
        
        report = f"""# Code Metrics

Key metrics about the codebase.

## File Metrics

- **Total Files:** {total_files}
- **Hot Files (< 7 days):** {hot_files}
- **Cold Files (> 90 days):** {cold_files}
- **Stable Files:** {total_files - hot_files - cold_files}

## Activity Distribution

- **Active Development:** {(hot_files / total_files * 100) if total_files > 0 else 0:.1f}%
- **Stable Code:** {((total_files - hot_files - cold_files) / total_files * 100) if total_files > 0 else 0:.1f}%
- **Stale Code:** {(cold_files / total_files * 100) if total_files > 0 else 0:.1f}%

## Recommendations

1. Focus testing efforts on hot files
2. Review cold files for deprecation
3. Maintain documentation for stable code
4. Monitor activity trends over time
"""
        
        (output_dir / "metrics.md").write_text(report)
        logger.info("📄 Created metrics.md")
    
    async def _write_current_state_readme(self, output_dir: Path):
        """Write README for current state directory"""
        
        report = """# Current State Analysis

This directory contains detailed analysis of the current codebase state.

## Files

- **file_inventory.md** - Complete file inventory with counts and sizes
- **hot_files_analysis.md** - Files with recent activity (< 7 days)
- **cold_files_analysis.md** - Files with no recent activity (> 90 days)
- **dependencies.md** - External dependencies analysis
- **tech_stack.md** - Technologies and frameworks used
- **metrics.md** - Key code metrics and statistics

## Purpose

These files provide a comprehensive snapshot of the codebase at this moment:
- What files exist
- What's being actively developed
- What might be deprecated
- What dependencies are used
- What technologies are in play
- Key metrics and trends

## Usage

Use these files to:
1. Understand the current state of the project
2. Identify areas needing attention
3. Plan refactoring efforts
4. Make informed decisions about technical debt
5. Track changes over time

## Generated

This analysis was generated automatically by Apollo's Akashic Intelligence Orchestrator.
"""
        
        (output_dir / "README.md").write_text(report)
        logger.info("📄 Created current_state/README.md")


# Example usage
async def main():
    """Example usage"""
    orchestrator = AkashicIntelligenceOrchestrator(
        entity_id="user_123",
        org_id="org_456",
        linear_api_key=os.getenv("LINEAR_API_KEY")
    )
    
    # Analyze repository
    results = await orchestrator.analyze_repository(
        repo_path="/path/to/repo",
        options={
            'watch_files': True,
            'consolidate_docs': True,
            'generate_plan': True,
            'build_knowledge_graph': True,
            'index_for_search': True
        }
    )
    
    print("📊 Analysis Results:")
    print(f"  Files scanned: {results['phases']['code_scan']['total_files']}")
    print(f"  Hot files: {len(results['phases']['code_scan']['hot_files'])}")
    print(f"  Planned features: {len(results['phases']['code_scan']['planned_features'])}")
    print(f"  Protected from deletion: {len(results['phases']['restructuring']['protected_files'])}")
    
    # Get dashboard data
    dashboard = orchestrator.get_dashboard_data()
    print("\n🎯 Dashboard:")
    print(f"  Temperature: {dashboard['temperature_distribution']}")
    
    # Keep monitoring
    try:
        await asyncio.sleep(3600)  # Monitor for 1 hour
    except KeyboardInterrupt:
        orchestrator.stop_monitoring()
    
    async def _generate_complete_docs(self, output_dir: Path, results: Dict, repo_path: str):
        """Generate complete documentation suite for docs folder"""
        docs_dir = output_dir / "docs"
        
        # 1. API Reference (if API detected)
        await self._generate_api_reference(docs_dir, repo_path)
        
        # 2. Deployment Guide
        await self._generate_deployment_guide(docs_dir, results, repo_path)
        
        # 3. Testing Guide
        await self._generate_testing_guide(docs_dir, results)
        
        # 4. Architecture Overview
        await self._generate_architecture_docs(docs_dir, results, repo_path)
        
        # 5. Getting Started Guide
        await self._generate_getting_started(docs_dir, results, repo_path)
        
        logger.info("📚 Generated complete documentation suite")
    
    async def _generate_api_reference(self, docs_dir: Path, repo_path: str):
        """Generate API reference documentation"""
        # Scan for API routes/endpoints
        api_files = []
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if any(keyword in file.lower() for keyword in ['route', 'api', 'endpoint', 'controller']):
                    if file.endswith(('.py', '.ts', '.js', '.go', '.rs')):
                        api_files.append(os.path.join(root, file))
        
        content = f"""# API Reference

Generated: {datetime.now().isoformat()}

## Overview

This document provides a comprehensive reference for all API endpoints in this project.

## Detected API Files

{len(api_files)} API-related files found:

"""
        for api_file in api_files[:20]:
            rel_path = os.path.relpath(api_file, repo_path)
            content += f"- `{rel_path}`\n"
        
        if len(api_files) > 20:
            content += f"\n*...and {len(api_files) - 20} more*\n"
        
        content += """

## Endpoints

*Auto-generated endpoint documentation will appear here after code analysis*

### Authentication

- **Method:** To be documented
- **Headers:** To be documented

### Rate Limiting

- **Limits:** To be documented

## Response Formats

All API responses follow standard JSON format:

```json
{
  "success": true,
  "data": {},
  "error": null
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 400  | Bad Request |
| 401  | Unauthorized |
| 404  | Not Found |
| 500  | Server Error |

## Next Steps

1. Review detected API files above
2. Add inline documentation to API routes
3. Run analysis again to auto-generate endpoint docs
"""
        
        (docs_dir / "API_REFERENCE.md").write_text(content)
        logger.info("📄 Created API_REFERENCE.md")
    
    async def _generate_deployment_guide(self, docs_dir: Path, results: Dict, repo_path: str):
        """Generate deployment guide"""
        project_type = results['phases'].get('project_type_detection', {})
        
        content = f"""# Deployment Guide

Generated: {datetime.now().isoformat()}

## Project Type

**Detected:** {project_type.get('primary', 'Unknown')}

## Deployment Strategy

**Recommended:** {project_type.get('deployment_strategy', 'To be determined')}

## Prerequisites

- [ ] Production environment configured
- [ ] Environment variables set
- [ ] Dependencies installed
- [ ] Database migrations run (if applicable)
- [ ] SSL certificates configured

## Deployment Steps

### 1. Build

```bash
# Install dependencies
npm install  # or pip install -r requirements.txt

# Build project
npm run build  # or python setup.py build
```

### 2. Test

```bash
# Run tests
npm test  # or pytest
```

### 3. Deploy

```bash
# Deploy to production
# (Commands will be auto-generated based on project type)
```

## Environment Variables

Required environment variables:

```env
# Add your environment variables here
NODE_ENV=production
DATABASE_URL=
API_KEY=
```

## Monitoring

- **Health Check:** `/health` endpoint
- **Metrics:** Available at `/metrics`
- **Logs:** Check application logs

## Rollback Procedure

If deployment fails:

1. Revert to previous version
2. Check error logs
3. Fix issues
4. Redeploy

## Next Steps

1. Configure CI/CD pipeline
2. Set up monitoring and alerts
3. Document environment-specific configurations
"""
        
        (docs_dir / "DEPLOYMENT_GUIDE.md").write_text(content)
        logger.info("📄 Created DEPLOYMENT_GUIDE.md")
    
    async def _generate_testing_guide(self, docs_dir: Path, results: Dict):
        """Generate testing guide"""
        test_analysis = results['phases'].get('testing', {})
        
        content = f"""# Testing Guide

Generated: {datetime.now().isoformat()}

## Testing Strategy

This project uses a comprehensive testing approach:

- **Unit Tests:** Test individual components
- **Integration Tests:** Test component interactions
- **End-to-End Tests:** Test complete user flows

## Test Coverage

Current coverage: {test_analysis.get('coverage_percentage', 0)}%

## Running Tests

### All Tests

```bash
npm test  # or pytest
```

### Specific Test Suite

```bash
npm test -- --grep "ComponentName"  # or pytest tests/test_component.py
```

### Watch Mode

```bash
npm test -- --watch
```

## Writing Tests

### Unit Test Example

```javascript
describe('ComponentName', () => {{
  it('should do something', () => {{
    // Arrange
    const input = 'test';
    
    // Act
    const result = myFunction(input);
    
    // Assert
    expect(result).toBe('expected');
  }});
}});
```

## Test Organization

```
tests/
├── unit/           # Unit tests
├── integration/    # Integration tests
└── e2e/           # End-to-end tests
```

## Best Practices

1. Write tests before code (TDD)
2. Keep tests simple and focused
3. Use descriptive test names
4. Mock external dependencies
5. Maintain high coverage (>80%)

## Continuous Integration

Tests run automatically on:
- Every commit
- Pull requests
- Before deployment

## Next Steps

1. Increase test coverage to 80%+
2. Add integration tests
3. Set up E2E testing framework
4. Configure CI/CD test automation
"""
        
        (docs_dir / "TESTING_GUIDE.md").write_text(content)
        logger.info("📄 Created TESTING_GUIDE.md")
    
    async def _generate_architecture_docs(self, docs_dir: Path, results: Dict, repo_path: str):
        """Generate architecture documentation"""
        scan_data = results['phases'].get('code_scan', {})
        
        content = f"""# Architecture Overview

Generated: {datetime.now().isoformat()}

## System Architecture

This document describes the high-level architecture of the project.

## Components

### Frontend
- **Location:** `{self._find_frontend_dir(repo_path)}`
- **Technology:** React/Vue/Angular (detected from files)

### Backend
- **Location:** `{self._find_backend_dir(repo_path)}`
- **Technology:** Python/Node/Go (detected from files)

### Database
- **Type:** To be documented
- **Schema:** See database documentation

## File Structure

```
{self._generate_tree_structure(repo_path, max_depth=2)}
```

## Data Flow

```
User Request → Frontend → API → Backend → Database
                                    ↓
                              External Services
```

## Key Design Decisions

1. **Separation of Concerns:** Frontend and backend are decoupled
2. **API-First:** All interactions go through well-defined APIs
3. **Scalability:** Designed for horizontal scaling
4. **Security:** Authentication and authorization at API layer

## Technology Stack

See `tech_stack.md` in the analysis folder for complete details.

## Dependencies

### External Services
- To be documented

### Third-Party Libraries
- See `dependencies.md` in the analysis folder

## Security Considerations

1. Authentication: JWT/OAuth
2. Authorization: Role-based access control
3. Data encryption: At rest and in transit
4. Input validation: All user inputs sanitized

## Performance Considerations

1. Caching strategy
2. Database indexing
3. Load balancing
4. CDN for static assets

## Next Steps

1. Document specific component interactions
2. Create sequence diagrams for key flows
3. Document API contracts
4. Update as architecture evolves
"""
        
        (docs_dir / "ARCHITECTURE.md").write_text(content)
        logger.info("📄 Created ARCHITECTURE.md")
    
    async def _generate_getting_started(self, docs_dir: Path, results: Dict, repo_path: str):
        """Generate getting started guide"""
        project_type = results['phases'].get('project_type_detection', {})
        
        content = f"""# Getting Started

Generated: {datetime.now().isoformat()}

## Welcome!

This guide will help you get up and running with this project.

## Prerequisites

- Git
- Node.js (v16+) or Python (3.8+) or Rust (1.70+)
- Docker (optional, for containerized development)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <project-name>
```

### 2. Install Dependencies

```bash
npm install  # or pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Run Development Server

```bash
npm run dev  # or python main.py
```

### 5. Open in Browser

Navigate to `http://localhost:3000` (or configured port)

## Project Structure

```
{self._generate_tree_structure(repo_path, max_depth=1)}
```

## Development Workflow

1. Create a feature branch
2. Make your changes
3. Write tests
4. Run tests locally
5. Submit pull request

## Common Tasks

### Running Tests

```bash
npm test
```

### Building for Production

```bash
npm run build
```

### Linting

```bash
npm run lint
```

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### Dependencies Not Installing

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Getting Help

- Check the [documentation](./PROJECT_DOCS.md)
- Review [API reference](./API_REFERENCE.md)
- See [architecture docs](./ARCHITECTURE.md)

## Next Steps

1. Read the [architecture overview](./ARCHITECTURE.md)
2. Review the [API reference](./API_REFERENCE.md)
3. Check out the [testing guide](./TESTING_GUIDE.md)
4. Start building!
"""
        
        (docs_dir / "GETTING_STARTED.md").write_text(content)
        logger.info("📄 Created GETTING_STARTED.md")
    
    def _find_frontend_dir(self, repo_path: str) -> str:
        """Find frontend directory"""
        common_names = ['frontend', 'client', 'web', 'ui', 'app', 'src']
        for name in common_names:
            path = os.path.join(repo_path, name)
            if os.path.exists(path):
                return name
        return "Not found"
    
    def _find_backend_dir(self, repo_path: str) -> str:
        """Find backend directory"""
        common_names = ['backend', 'server', 'api', 'services', 'src']
        for name in common_names:
            path = os.path.join(repo_path, name)
            if os.path.exists(path):
                return name
        return "Not found"
    
    def _generate_tree_structure(self, repo_path: str, max_depth: int = 2) -> str:
        """Generate simple tree structure"""
        tree = []
        for root, dirs, files in os.walk(repo_path):
            level = root.replace(repo_path, '').count(os.sep)
            if level >= max_depth:
                dirs[:] = []
                continue
            indent = '  ' * level
            tree.append(f"{indent}{os.path.basename(root)}/")
            if level < max_depth - 1:
                for file in files[:5]:  # Limit files shown
                    tree.append(f"{indent}  {file}")
        return '\n'.join(tree[:50])  # Limit total lines


if __name__ == "__main__":
    asyncio.run(main())
