"""
DeepSeek Coder - AI Code Completion Service

Provides intelligent code completion using DeepSeek Coder models.

Features:
- Multi-language support (Python, JavaScript, TypeScript, Rust, etc.)
- Context-aware completions
- Codebase-aware suggestions (uses CodebaseRAG)
- Fast inference
- Privacy-first (runs locally or on Theta GPU)

Models:
- DeepSeek Coder 1.3B (fast, local)
- DeepSeek Coder 6.7B (balanced)
- DeepSeek Coder 33B (best quality, Theta GPU)
"""

import os
import logging
from typing import List, Dict, Any, Optional
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

from learning.theta_edgecloud import ThetaEdgeCloud

logger = logging.getLogger(__name__)


class DeepSeekCoder:
    """
    DeepSeek Coder for AI-powered code completion
    
    Supports:
    - Code completion
    - Code generation
    - Code explanation
    - Bug fixing
    - Refactoring suggestions
    """
    
    def __init__(
        self,
        model_size: str = "33b",
        model_name: str = "deepseek-coder",
        use_theta: bool = True,
        device: str = "theta"
    ):
        """
        Initialize DeepSeek Coder (or other code models)
        
        Args:
            model_size: Model size (33b default, 32b for Qwen)
            model_name: Model name (deepseek-coder, qwen2.5-coder, starcoder2)
            use_theta: Use Theta GPU for inference (always True now)
            device: Device to use (always "theta" now)
        """
        self.model_size = model_size
        self.model_name = model_name
        self.use_theta = True  # Always use Theta GPU
        self.device = "theta"
        
        # Always use Theta GPU - no local models
        self.theta_client = ThetaEdgeCloud(
            api_key=os.getenv("THETA_API_KEY")
        )
        self.model = None
        self.tokenizer = None
        logger.info(f"✅ {model_name} {model_size} initialized with Theta GPU")
    
    async def complete_code(
        self,
        code: str,
        position: int,
        language: str,
        max_tokens: int = 50,
        temperature: float = 0.2,
        codebase_context: Optional[List[str]] = None
    ) -> List[str]:
        """
        Generate code completions
        
        Args:
            code: Current code
            position: Cursor position
            language: Programming language
            max_tokens: Max tokens to generate
            temperature: Sampling temperature (lower = more deterministic)
            codebase_context: Optional context from CodebaseRAG
        
        Returns:
            List of completion suggestions
        """
        # Split code at cursor position
        prefix = code[:position]
        suffix = code[position:]
        
        # Build prompt with context
        prompt = self._build_prompt(prefix, suffix, language, codebase_context)
        
        # Always use Theta GPU API
        completions = await self._complete_with_theta(
            prompt, max_tokens, temperature
        )
        
        return completions
    
    def _build_prompt(
        self,
        prefix: str,
        suffix: str,
        language: str,
        codebase_context: Optional[List[str]] = None
    ) -> str:
        """Build prompt for code completion"""
        
        # Add language context
        prompt = f"# Language: {language}\n\n"
        
        # Add codebase context if available
        if codebase_context:
            prompt += "# Similar code from codebase:\n"
            for ctx in codebase_context[:3]:  # Top 3 most relevant
                prompt += f"# {ctx}\n"
            prompt += "\n"
        
        # Add code prefix
        prompt += prefix
        
        return prompt
    
    def _complete_local(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> List[str]:
        """Generate completions using local model"""
        
        # Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=temperature > 0,
                num_return_sequences=3,  # Generate 3 suggestions
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode
        completions = []
        for output in outputs:
            completion = self.tokenizer.decode(
                output[inputs.input_ids.shape[1]:],
                skip_special_tokens=True
            )
            completions.append(completion.strip())
        
        return completions
    
    async def _complete_with_theta(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> List[str]:
        """Generate completions using Theta GPU"""
        import aiohttp
        
        theta_endpoint = os.getenv("THETA_MODEL_API_ENDPOINT")
        theta_api_key = os.getenv("THETA_API_KEY")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{theta_endpoint}/completions",
                json={
                    "model": f"deepseek-coder-{self.model_size}",
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "n": 3  # 3 suggestions
                },
                headers={"Authorization": f"Bearer {theta_api_key}"}
            ) as resp:
                result = await resp.json()
                completions = [choice["text"] for choice in result["choices"]]
                
                # Log TFUEL earned
                if "tfuel_earned" in result:
                    logger.info(f"Earned {result['tfuel_earned']} TFUEL for inference")
                
                return completions
    
    async def validate_code(
        self,
        code: str,
        language: str
    ) -> Dict[str, Any]:
        """
        Validate code and find errors
        
        Returns:
            Dict with errors, warnings, and suggestions
        """
        # Use language-specific validators
        if language == "python":
            return await self._validate_python(code)
        elif language in ["javascript", "typescript"]:
            return await self._validate_javascript(code)
        elif language == "rust":
            return await self._validate_rust(code)
        else:
            return {"errors": [], "warnings": [], "score": 100.0}
    
    async def _validate_python(self, code: str) -> Dict[str, Any]:
        """Validate Python code"""
        import ast
        
        errors = []
        warnings = []
        
        try:
            # Parse Python code
            ast.parse(code)
            score = 100.0
        except SyntaxError as e:
            errors.append({
                "line": e.lineno,
                "column": e.offset or 0,
                "message": str(e.msg),
                "severity": "error"
            })
            score = 50.0
        
        return {
            "errors": errors,
            "warnings": warnings,
            "score": score
        }
    
    async def _validate_javascript(self, code: str) -> Dict[str, Any]:
        """Validate JavaScript/TypeScript code"""
        # TODO: Integrate with ESLint or similar
        return {"errors": [], "warnings": [], "score": 100.0}
    
    async def _validate_rust(self, code: str) -> Dict[str, Any]:
        """Validate Rust code"""
        # TODO: Integrate with rust-analyzer
        return {"errors": [], "warnings": [], "score": 100.0}
    
    async def explain_code(
        self,
        code: str,
        language: str
    ) -> str:
        """
        Generate explanation for code
        
        Returns:
            Natural language explanation
        """
        prompt = f"""# Language: {language}
# Task: Explain what this code does

{code}

# Explanation:"""
        
        if self.use_theta:
            explanations = await self._complete_with_theta(prompt, 200, 0.3)
        else:
            explanations = self._complete_local(prompt, 200, 0.3)
        
        return explanations[0] if explanations else "Unable to generate explanation"
    
    async def fix_bugs(
        self,
        code: str,
        language: str,
        error_message: Optional[str] = None
    ) -> str:
        """
        Suggest bug fixes
        
        Returns:
            Fixed code
        """
        prompt = f"""# Language: {language}
# Task: Fix bugs in this code

{code}"""
        
        if error_message:
            prompt += f"\n# Error: {error_message}"
        
        prompt += "\n\n# Fixed code:"
        
        if self.use_theta:
            fixes = await self._complete_with_theta(prompt, 500, 0.1)
        else:
            fixes = self._complete_local(prompt, 500, 0.1)
        
        return fixes[0] if fixes else code


class DeepSeekConfig:
    """Configuration for DeepSeek Coder"""
    
    def __init__(
        self,
        model_size: str = "1.3b",
        use_theta: bool = False,
        device: str = "auto"
    ):
        """
        Args:
            model_size: Model size (1.3b, 6.7b, 33b)
            use_theta: Use Theta GPU for inference
            device: Device to run on
        """
        self.model_size = model_size
        self.use_theta = use_theta
        self.device = device
    
    @classmethod
    def from_env(cls) -> "DeepSeekConfig":
        """Create config from environment variables"""
        # Check both DEEPSEEK_PROVIDER and USE_THETA_GPU for backwards compatibility
        provider = os.getenv("DEEPSEEK_PROVIDER", "").lower()
        use_theta_env = os.getenv("USE_THETA_GPU", "false").lower() == "true"
        use_theta = provider == "theta" or use_theta_env
        
        return cls(
            model_size=os.getenv("DEEPSEEK_MODEL_SIZE", "33b" if use_theta else "1.3b"),
            use_theta=use_theta,
            device=os.getenv("DEEPSEEK_DEVICE", "auto")
        )
