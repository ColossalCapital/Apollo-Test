"""
Akashic CLI - Command-line interface for Akashic Intelligence

Commands:
- akashic analyze: Analyze repository and generate deployment configs
- akashic deploy generate: Generate deployment configs only
- akashic deploy validate: Validate generated configs
"""

import click
import asyncio
import sys
import os
from pathlib import Path
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.akashic_intelligence_orchestrator import AkashicIntelligenceOrchestrator
from services.deployment_mapper import DeploymentMapper
from services.deployment_config_generator import DeploymentConfigGenerator


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """
    Akashic Intelligence CLI
    
    Automated deployment configuration mapping and generation
    """
    pass


@cli.command()
@click.option('--repo-path', default='.', help='Path to repository (default: current directory)')
@click.option('--entity-id', help='Entity ID (default: current user)')
@click.option('--linear-key', envvar='LINEAR_API_KEY', help='Linear API key')
@click.option('--jira-key', envvar='JIRA_API_KEY', help='Jira API key')
@click.option('--github-token', envvar='GITHUB_TOKEN', help='GitHub token')
@click.option('--skip-docs', is_flag=True, help='Skip documentation consolidation')
@click.option('--skip-plan', is_flag=True, help='Skip project plan generation')
@click.option('--skip-graph', is_flag=True, help='Skip knowledge graph building')
@click.option('--skip-index', is_flag=True, help='Skip codebase indexing')
def analyze(
    repo_path: str,
    entity_id: Optional[str],
    linear_key: Optional[str],
    jira_key: Optional[str],
    github_token: Optional[str],
    skip_docs: bool,
    skip_plan: bool,
    skip_graph: bool,
    skip_index: bool
):
    """
    Analyze repository and generate deployment configs
    
    This command will:
    1. Detect project type
    2. Map deployment configurations
    3. Generate optimized configs
    4. Consolidate documentation
    5. Generate project plan
    6. Build knowledge graph
    7. Index codebase for search
    
    Example:
        akashic analyze --repo-path /path/to/repo --entity-id user_123
    """
    click.echo("🚀 Akashic Intelligence Analysis\n")
    
    # Resolve repo path
    repo_path = Path(repo_path).resolve()
    
    if not repo_path.exists():
        click.echo(f"❌ Error: Repository path does not exist: {repo_path}", err=True)
        sys.exit(1)
    
    click.echo(f"📂 Repository: {repo_path}")
    
    # Get entity ID
    if not entity_id:
        entity_id = os.getenv('USER', 'default_user')
        click.echo(f"👤 Entity ID: {entity_id} (auto-detected)")
    else:
        click.echo(f"👤 Entity ID: {entity_id}")
    
    # Create orchestrator
    orchestrator = AkashicIntelligenceOrchestrator(
        entity_id=entity_id,
        linear_api_key=linear_key
    )
    
    # Set options
    options = {
        'watch_files': True,
        'consolidate_docs': not skip_docs,
        'generate_plan': not skip_plan,
        'build_knowledge_graph': not skip_graph,
        'index_for_search': not skip_index,
    }
    
    # Run analysis
    try:
        click.echo("\n" + "=" * 60)
        click.echo("Starting Analysis...")
        click.echo("=" * 60 + "\n")
        
        result = asyncio.run(orchestrator.analyze_repository(
            str(repo_path),
            options=options
        ))
        
        click.echo("\n" + "=" * 60)
        click.echo("✅ Analysis Complete!")
        click.echo("=" * 60 + "\n")
        
        # Show summary
        click.echo("📊 Summary:")
        
        if 'phases' in result:
            phases = result['phases']
            
            # Project type
            if 'project_type' in phases:
                pt = phases['project_type']
                click.echo(f"   🔍 Project Type: {pt.get('type', 'unknown')} ({pt.get('confidence', 0)}% confidence)")
            
            # Deployment mapping
            if 'deployment_mapping' in phases:
                dm = phases['deployment_mapping']
                click.echo(f"   🗺️  Deployment Folders: {dm.get('folders_analyzed', 0)}")
                click.echo(f"   ⚠️  Conflicts: {dm.get('conflicts', 0)}")
                click.echo(f"   💡 Recommendations: {dm.get('recommendations', 0)}")
            
            # Documentation
            if 'docs_consolidation' in phases:
                dc = phases['docs_consolidation']
                click.echo(f"   📝 Documentation: {dc.get('files_consolidated', 0)} files consolidated")
            
            # Project plan
            if 'project_plan' in phases:
                pp = phases['project_plan']
                click.echo(f"   🎯 Project Plan: {pp.get('ticket_count', 0)} tickets generated")
            
            # Knowledge graph
            if 'knowledge_graph' in phases:
                kg = phases['knowledge_graph']
                click.echo(f"   🕸️  Knowledge Graph: {kg.get('node_count', 0)} nodes")
            
            # RAG indexing
            if 'rag_indexing' in phases:
                ri = phases['rag_indexing']
                click.echo(f"   🔍 RAG Index: {ri.get('chunk_count', 0)} chunks")
        
        # Show output location
        output_dir = repo_path / '.akashic'
        click.echo(f"\n📂 Results saved to: {output_dir}")
        
        # Show next steps
        click.echo("\n🚀 Next Steps:")
        click.echo(f"   1. Review mapping: cat {output_dir}/analysis/DEPLOYMENT_MAPPING.md")
        click.echo(f"   2. Review configs: ls -la {output_dir}/deploy/")
        click.echo(f"   3. Try Docker: cd {output_dir}/deploy/local/docker && docker-compose up")
        click.echo(f"   4. Try Tilt: cd {output_dir}/deploy/local/tilt && tilt up")
        click.echo(f"   5. Try Hybrid: cd {output_dir}/deploy/local/scripts && ./start-all.sh")
        
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.group()
def deploy():
    """Deployment configuration commands"""
    pass


@deploy.command('generate')
@click.option('--repo-path', default='.', help='Path to repository')
@click.option('--force', is_flag=True, help='Overwrite existing configs')
def deploy_generate(repo_path: str, force: bool):
    """
    Generate deployment configs only (skip analysis)
    
    Example:
        akashic deploy generate --repo-path /path/to/repo
    """
    click.echo("🔧 Generating Deployment Configs\n")
    
    # Resolve repo path
    repo_path = Path(repo_path).resolve()
    
    if not repo_path.exists():
        click.echo(f"❌ Error: Repository path does not exist: {repo_path}", err=True)
        sys.exit(1)
    
    # Check if mapping exists
    mapping_file = repo_path / '.akashic' / 'analysis' / 'deployment_map.json'
    
    if not mapping_file.exists():
        click.echo("⚠️  No deployment mapping found. Running analysis first...")
        click.echo("   (Use 'akashic analyze' to generate mapping)\n")
        
        # Run mapper
        try:
            mapper = DeploymentMapper(str(repo_path))
            result = asyncio.run(mapper.analyze_deployments())
            
            # Save report
            analysis_dir = repo_path / '.akashic' / 'analysis'
            mapper.save_report(analysis_dir)
            
            deployment_map = result['deployment_map']
            
        except Exception as e:
            click.echo(f"❌ Error during mapping: {e}", err=True)
            sys.exit(1)
    else:
        # Load existing mapping
        import json
        deployment_map = json.loads(mapping_file.read_text())
    
    # Check if configs already exist
    deploy_dir = repo_path / '.akashic' / 'deploy'
    
    if deploy_dir.exists() and not force:
        click.echo(f"⚠️  Deployment configs already exist at {deploy_dir}")
        click.echo("   Use --force to overwrite")
        sys.exit(1)
    
    # Generate configs
    try:
        click.echo("🔧 Generating configs...")
        
        generator = DeploymentConfigGenerator(str(repo_path), deployment_map)
        asyncio.run(generator.generate_all())
        
        click.echo("\n✅ Configs generated successfully!")
        click.echo(f"📂 Location: {deploy_dir}")
        
        # Show what was generated
        click.echo("\n📁 Generated:")
        
        for subdir in ['local/docker', 'local/podman', 'local/tilt', 'local/scripts', 'cloud/terraspace', 'cloud/juju']:
            path = deploy_dir / subdir
            if path.exists():
                file_count = len([f for f in path.rglob('*') if f.is_file()])
                click.echo(f"   ✅ {subdir}/ ({file_count} files)")
        
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@deploy.command('validate')
@click.option('--repo-path', default='.', help='Path to repository')
def deploy_validate(repo_path: str):
    """
    Validate generated deployment configs
    
    Example:
        akashic deploy validate --repo-path /path/to/repo
    """
    click.echo("🔍 Validating Deployment Configs\n")
    
    # Resolve repo path
    repo_path = Path(repo_path).resolve()
    deploy_dir = repo_path / '.akashic' / 'deploy'
    
    if not deploy_dir.exists():
        click.echo(f"❌ Error: No deployment configs found at {deploy_dir}", err=True)
        click.echo("   Run 'akashic analyze' or 'akashic deploy generate' first")
        sys.exit(1)
    
    # Validate configs
    errors = []
    warnings = []
    
    # Check Docker Compose
    docker_compose = deploy_dir / 'local' / 'docker' / 'docker-compose.yml'
    if docker_compose.exists():
        try:
            import yaml
            data = yaml.safe_load(docker_compose.read_text())
            
            if 'version' not in data:
                errors.append("docker-compose.yml: Missing 'version'")
            
            if 'services' not in data:
                errors.append("docker-compose.yml: Missing 'services'")
            else:
                click.echo(f"✅ Docker Compose: {len(data['services'])} services")
                
        except Exception as e:
            errors.append(f"docker-compose.yml: {e}")
    else:
        warnings.append("docker-compose.yml: Not found")
    
    # Check Podman Compose
    podman_compose = deploy_dir / 'local' / 'podman' / 'podman-compose.yml'
    if podman_compose.exists():
        click.echo("✅ Podman Compose: Found")
    else:
        warnings.append("podman-compose.yml: Not found")
    
    # Check Tiltfile
    tiltfile = deploy_dir / 'local' / 'tilt' / 'Tiltfile'
    if tiltfile.exists():
        click.echo("✅ Tiltfile: Found")
    else:
        warnings.append("Tiltfile: Not found")
    
    # Check Terraspace
    terraspace_main = deploy_dir / 'cloud' / 'terraspace' / 'app' / 'stacks' / 'microk8s' / 'main.tf'
    if terraspace_main.exists():
        click.echo("✅ Terraspace: Found")
    else:
        warnings.append("Terraspace: Not found")
    
    # Check Juju bundles
    juju_bundles = list((deploy_dir / 'cloud' / 'juju' / 'bundles').glob('*.yml'))
    if juju_bundles:
        click.echo(f"✅ Juju Bundles: {len(juju_bundles)} found")
    else:
        warnings.append("Juju bundles: Not found")
    
    # Show results
    click.echo("\n" + "=" * 60)
    
    if errors:
        click.echo("❌ Errors:")
        for error in errors:
            click.echo(f"   - {error}")
    
    if warnings:
        click.echo("\n⚠️  Warnings:")
        for warning in warnings:
            click.echo(f"   - {warning}")
    
    if not errors and not warnings:
        click.echo("✅ All configs are valid!")
    elif not errors:
        click.echo("\n✅ No errors found (warnings are optional)")
    else:
        click.echo("\n❌ Validation failed")
        sys.exit(1)


@cli.command()
def version():
    """Show version information"""
    click.echo("Akashic Intelligence CLI v1.0.0")
    click.echo("Deployment System: v1.0.0")
    click.echo("\nComponents:")
    click.echo("  - Deployment Mapper")
    click.echo("  - Config Generator")
    click.echo("  - Intelligence Orchestrator")


if __name__ == '__main__':
    cli()
