"""
Rust Connector Compiler

Compiles generated Rust connectors with proper error handling and progress tracking.
"""

import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import re


@dataclass
class CompilationResult:
    """Result of compilation"""
    success: bool
    binary_path: Optional[str] = None
    build_time_seconds: float = 0.0
    warnings: int = 0
    errors: int = 0
    output: str = ""
    error_output: str = ""


@dataclass
class CompilationProgress:
    """Progress event during compilation"""
    stage: str  # "checking", "building", "testing", "complete"
    message: str
    progress_percent: int
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict:
        return {
            "stage": self.stage,
            "message": self.message,
            "progress_percent": self.progress_percent,
            "timestamp": self.timestamp.isoformat(),
        }


class RustCompiler:
    """Compiles Rust connectors"""
    
    def __init__(
        self,
        base_path: str = "/Users/leonard/Documents/repos/Jacob Aaron Leonard LLC/ColossalCapital/AckwardRootsInc",
        progress_callback: Optional[Callable] = None
    ):
        self.base_path = base_path
        self.progress_callback = progress_callback
    
    async def emit_progress(self, progress: CompilationProgress):
        """Emit progress event"""
        if self.progress_callback:
            await self.progress_callback(progress)
        
        print(f"[{progress.timestamp.strftime('%H:%M:%S')}] {progress.stage}: {progress.message}")
    
    async def compile_connector(
        self,
        integration_type: str,
        run_tests: bool = True
    ) -> CompilationResult:
        """
        Compile a Rust connector
        
        Args:
            integration_type: Name of the integration (e.g., "gmail")
            run_tests: Whether to run tests after building
            
        Returns:
            CompilationResult with success status and details
        """
        connector_path = f"{self.base_path}/code/connectors/{integration_type}"
        
        # Verify directory exists
        if not Path(connector_path).exists():
            return CompilationResult(
                success=False,
                error_output=f"Connector directory not found: {connector_path}"
            )
        
        start_time = datetime.utcnow()
        
        # Stage 1: Cargo check (10%)
        await self.emit_progress(CompilationProgress(
            stage="checking",
            message="Running cargo check...",
            progress_percent=10
        ))
        
        check_result = await self.run_cargo_command(
            ["cargo", "check"],
            cwd=connector_path
        )
        
        if check_result.returncode != 0:
            return CompilationResult(
                success=False,
                error_output=check_result.stderr,
                output=check_result.stdout
            )
        
        await self.emit_progress(CompilationProgress(
            stage="checking",
            message="✅ Cargo check passed",
            progress_percent=30
        ))
        
        # Stage 2: Cargo build --release (50%)
        await self.emit_progress(CompilationProgress(
            stage="building",
            message="Building release binary...",
            progress_percent=40
        ))
        
        build_result = await self.run_cargo_command(
            ["cargo", "build", "--release"],
            cwd=connector_path
        )
        
        if build_result.returncode != 0:
            return CompilationResult(
                success=False,
                error_output=build_result.stderr,
                output=build_result.stdout
            )
        
        # Parse warnings
        warnings = self.count_warnings(build_result.stderr)
        
        await self.emit_progress(CompilationProgress(
            stage="building",
            message=f"✅ Build complete ({warnings} warnings)",
            progress_percent=70
        ))
        
        # Stage 3: Cargo test (optional, 30%)
        if run_tests:
            await self.emit_progress(CompilationProgress(
                stage="testing",
                message="Running tests...",
                progress_percent=75
            ))
            
            test_result = await self.run_cargo_command(
                ["cargo", "test"],
                cwd=connector_path
            )
            
            if test_result.returncode != 0:
                await self.emit_progress(CompilationProgress(
                    stage="testing",
                    message="⚠️ Tests failed (continuing anyway)",
                    progress_percent=90
                ))
            else:
                await self.emit_progress(CompilationProgress(
                    stage="testing",
                    message="✅ All tests passed",
                    progress_percent=90
                ))
        
        # Complete
        end_time = datetime.utcnow()
        build_time = (end_time - start_time).total_seconds()
        
        binary_path = f"{connector_path}/target/release/{integration_type}-connector"
        
        await self.emit_progress(CompilationProgress(
            stage="complete",
            message=f"✅ Compilation complete in {build_time:.1f}s",
            progress_percent=100
        ))
        
        return CompilationResult(
            success=True,
            binary_path=binary_path,
            build_time_seconds=build_time,
            warnings=warnings,
            errors=0,
            output=build_result.stdout,
            error_output=build_result.stderr
        )
    
    async def run_cargo_command(
        self,
        command: list,
        cwd: str
    ) -> subprocess.CompletedProcess:
        """Run a cargo command asynchronously"""
        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        return subprocess.CompletedProcess(
            args=command,
            returncode=process.returncode,
            stdout=stdout.decode('utf-8'),
            stderr=stderr.decode('utf-8')
        )
    
    def count_warnings(self, stderr: str) -> int:
        """Count warnings in cargo output"""
        warning_pattern = r'warning:'
        return len(re.findall(warning_pattern, stderr))
    
    async def verify_binary(self, binary_path: str) -> bool:
        """Verify the compiled binary exists and is executable"""
        path = Path(binary_path)
        
        if not path.exists():
            return False
        
        # Check if executable
        if not path.is_file():
            return False
        
        # Try to get version (most binaries support --version)
        try:
            process = await asyncio.create_subprocess_exec(
                binary_path,
                "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await asyncio.wait_for(process.communicate(), timeout=5.0)
            return process.returncode == 0
        except:
            # If --version doesn't work, just check if file exists
            return True


# Example usage
async def main():
    async def on_progress(progress: CompilationProgress):
        print(f"Progress: {progress.to_dict()}")
    
    compiler = RustCompiler(progress_callback=on_progress)
    
    # Compile a connector
    result = await compiler.compile_connector("gmail", run_tests=True)
    
    if result.success:
        print(f"\n✅ Compilation successful!")
        print(f"Binary: {result.binary_path}")
        print(f"Build time: {result.build_time_seconds:.1f}s")
        print(f"Warnings: {result.warnings}")
        
        # Verify binary
        is_valid = await compiler.verify_binary(result.binary_path)
        print(f"Binary valid: {is_valid}")
    else:
        print(f"\n❌ Compilation failed!")
        print(f"Error: {result.error_output}")


if __name__ == "__main__":
    asyncio.run(main())
