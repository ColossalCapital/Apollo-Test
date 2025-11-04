"""
Apollo Self-Update System

Apollo can update itself while running with zero downtime!

Features:
- Hot reload Python modules
- Zero-downtime deployments
- Gradual rollout (canary)
- Automatic rollback on errors
- Health monitoring
- Version tracking
"""

import logging
import importlib
import subprocess
import asyncio
from typing import Dict, List, Optional, Set
from datetime import datetime
import sys
import os

logger = logging.getLogger(__name__)


class SelfUpdatingApollo:
    """
    Apollo updates itself with zero downtime
    
    Workflow:
    1. Watch git repo for changes
    2. Pull latest code
    3. Run tests
    4. Hot reload changed modules
    5. Gradual rollout (10% → 50% → 100%)
    6. Monitor for errors
    7. Rollback if needed
    """
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.current_version = self._get_current_version()
        self.modules_to_watch = [
            'agents',
            'learning',
            'integrations',
            'testing',
            'cicd',
            'self_update'
        ]
        self.running = False
        self.canary_percentage = 0
        self.error_count = 0
        self.max_errors = 10
        
    def _get_current_version(self) -> str:
        """Get current git version"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--short', 'HEAD'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except:
            return "unknown"
            
    async def start_watching(self):
        """Start watching for updates"""
        self.running = True
        logger.info(f"🔄 Apollo self-update system started (version: {self.current_version})")
        
        while self.running:
            try:
                # Check for updates every minute
                await asyncio.sleep(60)
                
                if await self.has_new_commits():
                    logger.info("📥 New commits detected")
                    await self.apply_update()
                    
            except Exception as e:
                logger.error(f"Update check failed: {e}")
                
    async def has_new_commits(self) -> bool:
        """Check if there are new commits"""
        try:
            # Fetch latest
            subprocess.run(
                ['git', 'fetch', 'origin'],
                cwd=self.repo_path,
                check=True,
                capture_output=True
            )
            
            # Check if behind
            result = subprocess.run(
                ['git', 'rev-list', '--count', 'HEAD..origin/main'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            commits_behind = int(result.stdout.strip())
            return commits_behind > 0
            
        except Exception as e:
            logger.error(f"Failed to check for updates: {e}")
            return False
            
    async def apply_update(self):
        """Apply update with zero downtime"""
        logger.info("🚀 Applying update")
        
        try:
            # 1. Pull latest code
            logger.info("📥 Pulling latest code")
            subprocess.run(
                ['git', 'pull', 'origin', 'main'],
                cwd=self.repo_path,
                check=True
            )
            
            new_version = self._get_current_version()
            logger.info(f"📦 New version: {new_version}")
            
            # 2. Get changed files
            changed_files = await self._get_changed_files(
                self.current_version,
                new_version
            )
            logger.info(f"📝 Changed files: {len(changed_files)}")
            
            # 3. Run tests
            logger.info("🧪 Running tests")
            if not await self._run_tests():
                logger.error("❌ Tests failed, skipping update")
                # Rollback
                subprocess.run(
                    ['git', 'reset', '--hard', self.current_version],
                    cwd=self.repo_path
                )
                return
                
            # 4. Hot reload modules
            logger.info("🔄 Hot reloading modules")
            reloaded_modules = await self._hot_reload_modules(changed_files)
            logger.info(f"✅ Reloaded {len(reloaded_modules)} modules")
            
            # 5. Gradual rollout (canary)
            logger.info("🐤 Starting canary deployment")
            await self._canary_deployment()
            
            # 6. Check for errors
            if self.error_count > self.max_errors:
                logger.error(f"❌ Too many errors ({self.error_count}), rolling back")
                await self._rollback(self.current_version)
                return
                
            # 7. Success!
            self.current_version = new_version
            self.error_count = 0
            logger.info(f"✅ Update complete: {new_version}")
            
        except Exception as e:
            logger.error(f"❌ Update failed: {e}")
            await self._rollback(self.current_version)
            
    async def _get_changed_files(
        self,
        old_version: str,
        new_version: str
    ) -> List[str]:
        """Get list of changed files"""
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', old_version, new_version],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            files = result.stdout.strip().split('\n')
            # Filter for Python files in watched modules
            return [
                f for f in files
                if f.endswith('.py') and
                any(f.startswith(m) for m in self.modules_to_watch)
            ]
            
        except Exception as e:
            logger.error(f"Failed to get changed files: {e}")
            return []
            
    async def _run_tests(self) -> bool:
        """Run tests before applying update"""
        try:
            result = subprocess.run(
                ['pytest', 'tests/', '-v'],
                cwd=self.repo_path,
                capture_output=True,
                timeout=300  # 5 minutes
            )
            
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            logger.error("Tests timed out")
            return False
        except Exception as e:
            logger.error(f"Tests failed: {e}")
            return False
            
    async def _hot_reload_modules(self, changed_files: List[str]) -> Set[str]:
        """Hot reload changed Python modules"""
        reloaded = set()
        
        for file_path in changed_files:
            try:
                # Convert file path to module name
                module_name = file_path.replace('/', '.').replace('.py', '')
                
                # Skip if not in sys.modules
                if module_name not in sys.modules:
                    logger.info(f"Skipping {module_name} (not loaded)")
                    continue
                    
                # Reload module
                module = sys.modules[module_name]
                importlib.reload(module)
                
                reloaded.add(module_name)
                logger.info(f"✅ Reloaded {module_name}")
                
            except Exception as e:
                logger.error(f"Failed to reload {file_path}: {e}")
                
        return reloaded
        
    async def _canary_deployment(self):
        """Gradual rollout with monitoring"""
        
        # Phase 1: 10% of traffic
        logger.info("🐤 Canary: 10% traffic")
        self.canary_percentage = 10
        await asyncio.sleep(300)  # Wait 5 minutes
        
        if self.error_count > 5:
            raise Exception("Too many errors in canary phase 1")
            
        # Phase 2: 50% of traffic
        logger.info("🐤 Canary: 50% traffic")
        self.canary_percentage = 50
        await asyncio.sleep(300)  # Wait 5 minutes
        
        if self.error_count > 5:
            raise Exception("Too many errors in canary phase 2")
            
        # Phase 3: 100% of traffic
        logger.info("🐤 Canary: 100% traffic")
        self.canary_percentage = 100
        
    async def _rollback(self, version: str):
        """Rollback to previous version"""
        logger.info(f"⏪ Rolling back to {version}")
        
        try:
            # Reset to previous version
            subprocess.run(
                ['git', 'reset', '--hard', version],
                cwd=self.repo_path,
                check=True
            )
            
            # Reload all modules
            for module_name in self.modules_to_watch:
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
                    
            self.canary_percentage = 100
            self.error_count = 0
            
            logger.info(f"✅ Rolled back to {version}")
            
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            
    def report_error(self):
        """Report an error (for monitoring)"""
        self.error_count += 1
        logger.warning(f"⚠️ Error reported (count: {self.error_count})")
        
    def should_use_new_version(self) -> bool:
        """Determine if request should use new version (for canary)"""
        import random
        return random.randint(1, 100) <= self.canary_percentage
        
    def get_status(self) -> Dict:
        """Get self-update status"""
        return {
            'current_version': self.current_version,
            'canary_percentage': self.canary_percentage,
            'error_count': self.error_count,
            'running': self.running
        }


# Global instance
_self_updater = None


def get_self_updater(repo_path: str = ".") -> SelfUpdatingApollo:
    """Get global self-updater instance"""
    global _self_updater
    if _self_updater is None:
        _self_updater = SelfUpdatingApollo(repo_path)
    return _self_updater


async def start_self_update_system(repo_path: str = "."):
    """Start Apollo self-update system"""
    updater = get_self_updater(repo_path)
    await updater.start_watching()
