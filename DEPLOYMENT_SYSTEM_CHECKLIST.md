# ✅ Deployment System - Pre-Build Checklist

**Everything you need before building the deployment system in Akashic IDE**

---

## 🎯 Current Status

### **✅ Already Built (Ready to Use)**
- ✅ `deployment_mapper.py` (~500 lines)
- ✅ `deployment_config_generator.py` (~700 lines)
- ✅ `akashic_intelligence_orchestrator.py` (updated)
- ✅ Complete documentation (5 files, ~6,000 lines)
- ✅ Test script

### **⚠️ Missing Components (Need to Build)**

---

## 📋 What's Missing

### **1. Python Dependencies** ⚠️ REQUIRED

**Status:** Most dependencies already in `requirements.txt`, but need to verify YAML support

**Current `requirements.txt` has:**
- ✅ `pyyaml==6.0.1` (for YAML parsing)
- ✅ `gitpython==3.1.40` (for git operations)
- ✅ `watchdog==3.0.0` (for file watching)
- ✅ `aiofiles==23.2.1` (for async file operations)

**Action:** ✅ **NO ACTION NEEDED** - All dependencies are already in `requirements.txt`

---

### **2. Akashic CLI Integration** ⚠️ REQUIRED

**Status:** Need to add `akashic analyze` command

**What's Needed:**
```python
# Apollo/cli/akashic_cli.py (NEW FILE)

import click
from services.akashic_intelligence_orchestrator import AkashicIntelligenceOrchestrator

@click.group()
def cli():
    """Akashic Intelligence CLI"""
    pass

@cli.command()
@click.option('--repo-path', default='.', help='Path to repository')
@click.option('--entity-id', required=True, help='Entity ID')
@click.option('--linear-key', help='Linear API key')
def analyze(repo_path, entity_id, linear_key):
    """Analyze repository and generate deployment configs"""
    import asyncio
    
    orchestrator = AkashicIntelligenceOrchestrator(
        entity_id=entity_id,
        linear_api_key=linear_key
    )
    
    result = asyncio.run(orchestrator.analyze_repository(repo_path))
    
    click.echo("✅ Analysis complete!")
    click.echo(f"📊 Results saved to {repo_path}/.akashic/")

if __name__ == '__main__':
    cli()
```

**Action:** 🔨 **BUILD THIS** - Create CLI interface for Akashic

---

### **3. Error Handling** ⚠️ RECOMMENDED

**Status:** Basic error handling exists, but could be improved

**What's Needed:**
- Better error messages for missing files
- Validation for YAML/JSON parsing
- Graceful fallbacks for missing configs

**Current State:**
```python
# deployment_mapper.py has basic try/catch
try:
    data = yaml.safe_load(content)
except:
    pass  # Silent failure
```

**Improvement Needed:**
```python
try:
    data = yaml.safe_load(content)
except yaml.YAMLError as e:
    logger.warning(f"Invalid YAML in {file}: {e}")
    return None
except Exception as e:
    logger.error(f"Failed to read {file}: {e}")
    return None
```

**Action:** 🔨 **BUILD THIS** - Add better error handling

---

### **4. Configuration Validation** ⚠️ RECOMMENDED

**Status:** No validation for generated configs

**What's Needed:**
- Validate generated Docker Compose files
- Validate Terraspace configs
- Validate Juju bundles

**Example:**
```python
# Apollo/services/config_validator.py (NEW FILE)

class ConfigValidator:
    """Validates generated deployment configs"""
    
    def validate_docker_compose(self, file_path: Path) -> bool:
        """Validate Docker Compose file"""
        try:
            data = yaml.safe_load(file_path.read_text())
            
            # Check required fields
            if 'version' not in data:
                logger.error("Missing 'version' in docker-compose.yml")
                return False
            
            if 'services' not in data:
                logger.error("Missing 'services' in docker-compose.yml")
                return False
            
            # Validate each service
            for service_name, service_config in data['services'].items():
                if 'image' not in service_config and 'build' not in service_config:
                    logger.error(f"Service {service_name} missing 'image' or 'build'")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False
```

**Action:** 🔨 **BUILD THIS** - Add config validation

---

### **5. Integration with Existing Services** ⚠️ REQUIRED

**Status:** Need to verify integration points

**Check These Files:**
- ✅ `akashic_intelligence_orchestrator.py` - Already integrated
- ⚠️ `project_type_detector.py` - Need to verify it exists
- ⚠️ `scaffold_generator.py` - Need to verify it exists
- ⚠️ `pm_bidirectional_sync.py` - Need to verify it exists

**Action:** 🔍 **VERIFY** - Check if these files exist and work correctly

---

### **6. File Permissions** ⚠️ REQUIRED

**Status:** Generated scripts need execute permissions

**Current Code:**
```python
# deployment_config_generator.py
script_path.write_text(script)
script_path.chmod(0o755)  # ✅ Already handled!
```

**Action:** ✅ **NO ACTION NEEDED** - Already implemented

---

### **7. Docker/Podman Detection** 💡 NICE TO HAVE

**Status:** No runtime detection

**What's Needed:**
```python
# Apollo/services/runtime_detector.py (NEW FILE)

import subprocess

class RuntimeDetector:
    """Detects available container runtimes"""
    
    def detect_docker(self) -> bool:
        """Check if Docker is available"""
        try:
            subprocess.run(['docker', '--version'], capture_output=True, check=True)
            return True
        except:
            return False
    
    def detect_podman(self) -> bool:
        """Check if Podman is available"""
        try:
            subprocess.run(['podman', '--version'], capture_output=True, check=True)
            return True
        except:
            return False
    
    def detect_tilt(self) -> bool:
        """Check if Tilt is available"""
        try:
            subprocess.run(['tilt', 'version'], capture_output=True, check=True)
            return True
        except:
            return False
    
    def recommend_runtime(self) -> str:
        """Recommend best available runtime"""
        if self.detect_tilt() and self.detect_docker():
            return 'hybrid'
        elif self.detect_podman():
            return 'podman'
        elif self.detect_docker():
            return 'docker'
        else:
            return 'none'
```

**Action:** 💡 **OPTIONAL** - Add runtime detection

---

### **8. Template Customization** 💡 NICE TO HAVE

**Status:** Templates are hardcoded

**What's Needed:**
- Allow users to customize Tiltfile template
- Allow users to customize Terraspace templates
- Allow users to customize Juju bundle templates

**Example:**
```python
# Apollo/templates/tiltfile.template (NEW FILE)

# Tiltfile - Fast iteration for your services
# Generated by Akashic

{% for service_name, service_config in services.items() %}
# {{ service_name }} service
docker_build('{{ service_name }}', '{{ service_config.build_context }}')

# Live reload for {{ service_name }}
local_resource('{{ service_name }}-hot-reload',
    'cd {{ service_config.build_context }} && {{ service_config.dev_command }}',
    deps=['{{ service_config.build_context }}'],
    labels=['{{ service_name }}'])
{% endfor %}
```

**Action:** 💡 **OPTIONAL** - Add template customization

---

### **9. Progress Indicators** 💡 NICE TO HAVE

**Status:** Basic logging exists

**What's Needed:**
- Progress bars for file analysis
- Real-time status updates
- Estimated time remaining

**Example:**
```python
from tqdm import tqdm

# In deployment_mapper.py
for folder in tqdm(deployment_folders, desc="Analyzing folders"):
    await self._analyze_folder(folder)
```

**Action:** 💡 **OPTIONAL** - Add progress indicators

---

### **10. Dry Run Mode** 💡 NICE TO HAVE

**Status:** No dry run option

**What's Needed:**
```python
# In deployment_config_generator.py
def __init__(self, repo_path: str, deployment_map: Dict, dry_run: bool = False):
    self.dry_run = dry_run
    
async def generate_all(self):
    if self.dry_run:
        logger.info("🔍 DRY RUN MODE - No files will be created")
        # Show what would be created
        return
    
    # Actually create files
```

**Action:** 💡 **OPTIONAL** - Add dry run mode

---

## 🎯 Priority Checklist

### **🔴 CRITICAL (Must Build Before Using)**

1. **✅ Python Dependencies** - Already in requirements.txt
2. **🔨 Akashic CLI** - Need to create `cli/akashic_cli.py`
3. **🔍 Verify Integrations** - Check if dependent services exist

### **🟡 RECOMMENDED (Should Build)**

4. **🔨 Error Handling** - Improve error messages
5. **🔨 Config Validation** - Validate generated configs

### **🟢 OPTIONAL (Nice to Have)**

6. **💡 Runtime Detection** - Detect Docker/Podman/Tilt
7. **💡 Template Customization** - Allow custom templates
8. **💡 Progress Indicators** - Show progress bars
9. **💡 Dry Run Mode** - Preview without creating files

---

## 📝 Action Items

### **Before Building in Akashic IDE:**

#### **1. Create CLI Interface** (CRITICAL)
```bash
# Create file: Apollo/cli/akashic_cli.py
# Add click commands for:
# - akashic analyze
# - akashic deploy generate
# - akashic deploy validate
```

#### **2. Verify Dependencies** (CRITICAL)
```bash
# Check these files exist:
cd Apollo/services/
ls -la project_type_detector.py
ls -la scaffold_generator.py
ls -la pm_bidirectional_sync.py
```

#### **3. Add Error Handling** (RECOMMENDED)
```bash
# Update deployment_mapper.py
# Update deployment_config_generator.py
# Add try/catch blocks with proper logging
```

#### **4. Create Config Validator** (RECOMMENDED)
```bash
# Create file: Apollo/services/config_validator.py
# Add validation for Docker Compose, Terraspace, Juju
```

#### **5. Test Everything** (CRITICAL)
```bash
# Run test script
cd Apollo/
python test_deployment_system.py

# Expected output:
# ✅ All tests pass
```

---

## 🚀 Quick Start After Building

Once you've built the missing components:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run analysis
akashic analyze --repo-path /path/to/Infrastructure --entity-id user_123

# 3. Use generated configs
cd .akashic/deploy/local/scripts/
./start-all.sh
```

---

## 📊 Summary

### **What's Ready:**
- ✅ Core deployment mapper (~500 lines)
- ✅ Core config generator (~700 lines)
- ✅ Orchestrator integration
- ✅ Complete documentation
- ✅ Test script
- ✅ All Python dependencies

### **What's Missing (CRITICAL):**
- 🔨 CLI interface (`cli/akashic_cli.py`)
- 🔍 Verify dependent services exist

### **What's Missing (RECOMMENDED):**
- 🔨 Better error handling
- 🔨 Config validation

### **What's Missing (OPTIONAL):**
- 💡 Runtime detection
- 💡 Template customization
- 💡 Progress indicators
- 💡 Dry run mode

### **Estimated Time to Complete:**
- **Critical items:** 2-4 hours
- **Recommended items:** 2-3 hours
- **Optional items:** 4-6 hours
- **Total:** 8-13 hours

---

## 🎯 Recommendation

**Minimum Viable Product (MVP):**
1. ✅ Build CLI interface (2 hours)
2. ✅ Verify dependencies (30 min)
3. ✅ Add basic error handling (1 hour)
4. ✅ Test everything (30 min)

**Total MVP Time: ~4 hours**

Then you can start using it and add optional features later!

---

## 📞 Questions to Answer

Before building in Akashic IDE:

1. **Do these files exist?**
   - `Apollo/services/project_type_detector.py`
   - `Apollo/services/scaffold_generator.py`
   - `Apollo/services/pm_bidirectional_sync.py`

2. **What CLI framework do you want?**
   - Click (recommended, already used in ecosystem)
   - Typer (modern alternative)
   - Argparse (standard library)

3. **Do you want validation?**
   - Yes (recommended for production)
   - No (faster MVP, add later)

4. **Do you want runtime detection?**
   - Yes (better UX)
   - No (simpler, manual selection)

---

**Ready to build! 🚀**
