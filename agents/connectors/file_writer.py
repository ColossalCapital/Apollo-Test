"""
Connector File Writer

Writes generated Rust connector code to AckwardRootsInc repository.
Emits progress events for real-time monitoring.
"""

import os
import asyncio
from pathlib import Path
from typing import Dict, Callable, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ProgressEvent:
    """Progress event for real-time updates"""
    type: str  # "file_written", "directory_created", "progress"
    message: str
    file_path: Optional[str] = None
    line_count: Optional[int] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        return {
            "type": self.type,
            "message": self.message,
            "file_path": self.file_path,
            "line_count": self.line_count,
            "timestamp": self.timestamp.isoformat(),
        }


class ConnectorFileWriter:
    """Writes connector files to AckwardRootsInc repository"""
    
    def __init__(
        self,
        base_path: str = "/Users/leonard/Documents/repos/Jacob Aaron Leonard LLC/ColossalCapital/AckwardRootsInc",
        progress_callback: Optional[Callable] = None
    ):
        self.base_path = base_path
        self.progress_callback = progress_callback
        
    async def emit_progress(self, event: ProgressEvent):
        """Emit progress event"""
        if self.progress_callback:
            await self.progress_callback(event)
        
        # Also log to console
        print(f"[{event.timestamp.strftime('%H:%M:%S')}] {event.type}: {event.message}")
    
    async def write_connector_files(
        self,
        integration_type: str,
        code_files: Dict[str, str]
    ) -> str:
        """
        Write all connector files to disk
        
        Args:
            integration_type: Name of the integration (e.g., "gmail")
            code_files: Dict with keys: cargo_toml, main_rs, models_rs, etc.
            
        Returns:
            Path to the created connector directory
        """
        connector_path = f"{self.base_path}/code/connectors/{integration_type}"
        
        await self.emit_progress(ProgressEvent(
            type="progress",
            message=f"Creating connector directory: {connector_path}"
        ))
        
        # Create directory structure
        await self.create_directory_structure(connector_path)
        
        # Write Cargo.toml
        await self.write_file(
            path=f"{connector_path}/Cargo.toml",
            content=code_files.get('cargo_toml', ''),
            description="Cargo.toml"
        )
        
        # Write source files
        src_files = {
            'main.rs': code_files.get('main_rs', ''),
            'models.rs': code_files.get('models_rs', ''),
            'kafka_producer.rs': code_files.get('kafka_producer_rs', ''),
            'config.rs': code_files.get('config_rs', ''),
            'connection_manager.rs': code_files.get('connection_manager_rs', ''),
        }
        
        for filename, content in src_files.items():
            await self.write_file(
                path=f"{connector_path}/src/{filename}",
                content=content,
                description=f"src/{filename}"
            )
        
        # Write README
        await self.write_file(
            path=f"{connector_path}/README.md",
            content=code_files.get('readme_md', ''),
            description="README.md"
        )
        
        # Write .gitignore
        await self.write_file(
            path=f"{connector_path}/.gitignore",
            content=self.generate_gitignore(),
            description=".gitignore"
        )
        
        await self.emit_progress(ProgressEvent(
            type="progress",
            message=f"✅ All files written successfully"
        ))
        
        return connector_path
    
    async def create_directory_structure(self, connector_path: str):
        """Create directory structure for connector"""
        directories = [
            connector_path,
            f"{connector_path}/src",
            f"{connector_path}/tests",
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            await self.emit_progress(ProgressEvent(
                type="directory_created",
                message=f"Created directory: {directory}"
            ))
    
    async def write_file(self, path: str, content: str, description: str):
        """Write a single file with progress tracking"""
        # Count lines
        line_count = len(content.split('\n'))
        
        await self.emit_progress(ProgressEvent(
            type="progress",
            message=f"Writing {description}... ({line_count} lines)",
            file_path=path,
            line_count=line_count
        ))
        
        # Write file
        with open(path, 'w') as f:
            f.write(content)
        
        await self.emit_progress(ProgressEvent(
            type="file_written",
            message=f"✅ {description} complete",
            file_path=path,
            line_count=line_count
        ))
        
        # Small delay for visual effect in UI
        await asyncio.sleep(0.1)
    
    def generate_gitignore(self) -> str:
        """Generate .gitignore for Rust project"""
        return """# Rust
/target/
**/*.rs.bk
*.pdb

# Cargo
Cargo.lock

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Environment
.env
.env.local
"""
    
    async def verify_files(self, connector_path: str) -> Dict[str, bool]:
        """Verify all required files exist"""
        required_files = [
            'Cargo.toml',
            'src/main.rs',
            'src/models.rs',
            'src/kafka_producer.rs',
            'src/config.rs',
            'src/connection_manager.rs',
            'README.md',
            '.gitignore',
        ]
        
        verification = {}
        for file in required_files:
            file_path = f"{connector_path}/{file}"
            exists = os.path.exists(file_path)
            verification[file] = exists
            
            if exists:
                await self.emit_progress(ProgressEvent(
                    type="progress",
                    message=f"✅ Verified: {file}"
                ))
            else:
                await self.emit_progress(ProgressEvent(
                    type="progress",
                    message=f"❌ Missing: {file}"
                ))
        
        return verification
    
    async def get_file_stats(self, connector_path: str) -> Dict:
        """Get statistics about generated files"""
        stats = {
            'total_files': 0,
            'total_lines': 0,
            'total_size_bytes': 0,
            'files': {}
        }
        
        for root, dirs, files in os.walk(connector_path):
            for file in files:
                if file.endswith('.rs') or file in ['Cargo.toml', 'README.md']:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, connector_path)
                    
                    with open(file_path, 'r') as f:
                        content = f.read()
                        line_count = len(content.split('\n'))
                        size = len(content.encode('utf-8'))
                    
                    stats['total_files'] += 1
                    stats['total_lines'] += line_count
                    stats['total_size_bytes'] += size
                    stats['files'][rel_path] = {
                        'lines': line_count,
                        'size_bytes': size
                    }
        
        return stats


# Example usage
async def main():
    # Progress callback for real-time updates
    async def on_progress(event: ProgressEvent):
        print(f"Progress: {event.to_dict()}")
    
    writer = ConnectorFileWriter(progress_callback=on_progress)
    
    # Example code files
    code_files = {
        'cargo_toml': '[package]\nname = "gmail-connector"\nversion = "0.1.0"',
        'main_rs': 'fn main() {\n    println!("Hello, world!");\n}',
        'models_rs': 'pub struct Message {}',
        'kafka_producer_rs': 'pub struct KafkaProducer {}',
        'config_rs': 'pub struct Config {}',
        'connection_manager_rs': 'pub struct ConnectionManager {}',
        'readme_md': '# Gmail Connector\n\nGenerated by Apollo',
    }
    
    # Write files
    connector_path = await writer.write_connector_files('gmail', code_files)
    print(f"\nConnector written to: {connector_path}")
    
    # Verify files
    verification = await writer.verify_files(connector_path)
    print(f"\nVerification: {verification}")
    
    # Get stats
    stats = await writer.get_file_stats(connector_path)
    print(f"\nStats: {stats}")


if __name__ == "__main__":
    asyncio.run(main())
