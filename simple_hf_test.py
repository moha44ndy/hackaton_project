#!/usr/bin/env python3
"""
Simple test: HF local model directly into PromptRunner
"""

import sys
from pathlib import Path
import logging

# Setup path
BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / 'src'))

# Load environment
from dotenv import load_dotenv
load_dotenv(BASE / '.env')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from prompt_runner import PromptRunner
from hf_client import HuggingFaceLocalClient
from llm_clients import LLMClient
from typing import Optional, Dict, Tuple

class SimpleHFClient(LLMClient):
    """Wrapper around HuggingFaceLocalClient for PromptRunner"""
    def __init__(self, api_key: Optional[str] = None, model: str = "distilgpt2"):
        super().__init__(api_key=None)
        self.hf_client = HuggingFaceLocalClient(model_id=model, device="cpu")
        self.model = model
        
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Tuple[str, Dict]:
        """Generate response"""
        response = self.hf_client.generate_response(prompt, max_tokens=max_tokens)
        self.total_calls += 1
        return response, {
            "model": self.model,
            "tokens": 0,  # Local models don't track tokens easily
            "latency_ms": 0
        }

def main():
    logger.info("="*70)
    logger.info("🚀 WMDP Pipeline Test: HuggingFace Local")
    logger.info("="*70)
    
    # Setup directories
    output_dir = BASE / "results"
    output_dir.mkdir(exist_ok=True)
    
    # Initialize runner
    logger.info("\n📌 Initializing PromptRunner...")
    runner = PromptRunner(
        dataset_path=str(BASE / "data" / "wmdp_prompts.json"),
        output_dir=str(output_dir),
        log_dir=str(BASE / "logs")
    )
    
    # Load dataset
    logger.info("\n📚 Loading dataset...")
    num_loaded = runner.load_dataset()
    logger.info(f"✅ Loaded {num_loaded} prompts")
    
    # Manually run a few prompts with HF local
    logger.info("\n🤗 Running 3 prompts on HuggingFace (distilgpt2)...\n")
    
    hf_client = SimpleHFClient(model="distilgpt2")
    
    responses = []
    for prompt in runner.prompts[:3]:  # First 3 only
        logger.info(f"📝 Prompt: {prompt.text[:60]}...")
        try:
            response_text, metadata = hf_client.generate(prompt.text, max_tokens=50)
            logger.info(f"✅ Response: {response_text[:100]}...\n")
        except Exception as e:
            logger.error(f"❌ Error: {e}\n")
    
    logger.info("🎉 Test completed!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
