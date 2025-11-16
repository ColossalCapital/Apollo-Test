"""
Test Deployment System

Quick test to verify deployment mapper and config generator work correctly
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Apollo.services.deployment_mapper import DeploymentMapper
from Apollo.services.deployment_config_generator import DeploymentConfigGenerator


async def test_deployment_system():
    """Test the complete deployment system"""
    
    print("🧪 Testing Deployment System\n")
    
    # Test with Infrastructure folder
    infrastructure_path = Path(__file__).parent.parent / "Infrastructure"
    
    if not infrastructure_path.exists():
        print(f"❌ Infrastructure folder not found at {infrastructure_path}")
        return
    
    print(f"📂 Testing with: {infrastructure_path}\n")
    
    # ============================================================
    # Test 1: Deployment Mapper
    # ============================================================
    print("=" * 60)
    print("TEST 1: Deployment Mapper")
    print("=" * 60)
    
    try:
        mapper = DeploymentMapper(str(infrastructure_path))
        result = await mapper.analyze_deployments()
        
        print(f"\n✅ Deployment Mapper Success!")
        print(f"   - Folders analyzed: {len(result['deployment_map'])}")
        print(f"   - Conflicts detected: {len(result['conflicts'])}")
        print(f"   - Recommendations: {len(result['recommendations'])}")
        
        # Show deployment map
        print("\n📊 Deployment Map:")
        for category, folders in result['deployment_map'].items():
            if folders:
                print(f"\n   {category.upper()}:")
                for folder_path, data in folders.items():
                    print(f"   - {folder_path} ({len(data['files'])} files)")
                    print(f"     → {data['target_location']}")
        
        # Show conflicts
        if result['conflicts']:
            print("\n⚠️  Conflicts:")
            for conflict in result['conflicts']:
                print(f"   - {conflict['type']}: {conflict['description']}")
        
        # Save report
        test_output = infrastructure_path / '.akashic' / 'analysis'
        mapper.save_report(test_output)
        print(f"\n📝 Report saved to: {test_output}/DEPLOYMENT_MAPPING.md")
        
    except Exception as e:
        print(f"\n❌ Deployment Mapper Failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # ============================================================
    # Test 2: Config Generator
    # ============================================================
    print("\n" + "=" * 60)
    print("TEST 2: Config Generator")
    print("=" * 60)
    
    try:
        generator = DeploymentConfigGenerator(
            str(infrastructure_path),
            result['deployment_map']
        )
        await generator.generate_all()
        
        print(f"\n✅ Config Generator Success!")
        
        # Check generated files
        deploy_dir = infrastructure_path / '.akashic' / 'deploy'
        
        print("\n📁 Generated Structure:")
        
        # Local configs
        local_dir = deploy_dir / 'local'
        if local_dir.exists():
            print("\n   LOCAL:")
            for subdir in ['docker', 'podman', 'tilt', 'scripts']:
                path = local_dir / subdir
                if path.exists():
                    files = list(path.rglob('*'))
                    file_count = len([f for f in files if f.is_file()])
                    print(f"   - {subdir}/ ({file_count} files)")
        
        # Cloud configs
        cloud_dir = deploy_dir / 'cloud'
        if cloud_dir.exists():
            print("\n   CLOUD:")
            for subdir in ['kubernetes', 'juju', 'terraspace', 'monitoring']:
                path = cloud_dir / subdir
                if path.exists():
                    files = list(path.rglob('*'))
                    file_count = len([f for f in files if f.is_file()])
                    print(f"   - {subdir}/ ({file_count} files)")
        
        # Show some generated files
        print("\n📄 Sample Generated Files:")
        
        docker_compose = deploy_dir / 'local' / 'docker' / 'docker-compose.yml'
        if docker_compose.exists():
            print(f"   ✅ {docker_compose.relative_to(infrastructure_path)}")
        
        podman_compose = deploy_dir / 'local' / 'podman' / 'podman-compose.yml'
        if podman_compose.exists():
            print(f"   ✅ {podman_compose.relative_to(infrastructure_path)}")
        
        tiltfile = deploy_dir / 'local' / 'tilt' / 'Tiltfile'
        if tiltfile.exists():
            print(f"   ✅ {tiltfile.relative_to(infrastructure_path)}")
        
        start_script = deploy_dir / 'local' / 'scripts' / 'start-all.sh'
        if start_script.exists():
            print(f"   ✅ {start_script.relative_to(infrastructure_path)}")
        
        terraspace_main = deploy_dir / 'cloud' / 'terraspace' / 'app' / 'stacks' / 'microk8s' / 'main.tf'
        if terraspace_main.exists():
            print(f"   ✅ {terraspace_main.relative_to(infrastructure_path)}")
        
        juju_bundle = deploy_dir / 'cloud' / 'juju' / 'bundles' / 'dev-bundle.yml'
        if juju_bundle.exists():
            print(f"   ✅ {juju_bundle.relative_to(infrastructure_path)}")
        
        print(f"\n📂 All configs saved to: {deploy_dir}")
        
    except Exception as e:
        print(f"\n❌ Config Generator Failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # ============================================================
    # Summary
    # ============================================================
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 60)
    
    print("\n📊 Summary:")
    print(f"   ✅ Deployment Mapper: Working")
    print(f"   ✅ Config Generator: Working")
    print(f"   ✅ Files Generated: {len(list(deploy_dir.rglob('*')))}")
    
    print("\n🚀 Next Steps:")
    print(f"   1. Review mapping: cat {test_output}/DEPLOYMENT_MAPPING.md")
    print(f"   2. Review configs: ls -la {deploy_dir}/")
    print(f"   3. Try Docker Compose: cd {deploy_dir}/local/docker && docker-compose up")
    print(f"   4. Try Tilt: cd {deploy_dir}/local/tilt && tilt up")
    print(f"   5. Try Hybrid: cd {deploy_dir}/local/scripts && ./start-all.sh")
    
    print("\n✨ Deployment system is ready to use!")


if __name__ == "__main__":
    asyncio.run(test_deployment_system())
