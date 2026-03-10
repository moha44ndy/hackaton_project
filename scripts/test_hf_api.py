#!/usr/bin/env python3
"""
Test Hugging Face local model (using transformers)
This is more reliable than HF Inference API and works for the pipeline
"""

import os
import sys
from pathlib import Path

# Load env
from dotenv import load_dotenv
load_dotenv()

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / 'src'))

if __name__ == '__main__':
    try:
        from hf_client import HuggingFaceLocalClient
        
        print('📌 Creating HuggingFace Local client (transformers)...')
        # Use a lightweight model for testing
        client = HuggingFaceLocalClient(
            model_id='distilgpt2',
            device='cpu'
        )
        
        print('✅ Client created successfully')
        
        prompt = 'Say one short friendly sentence about yourself.'
        print(f'📝 Prompt: {prompt}')
        
        print('🔄 Generating response...')
        response = client.generate_response(prompt=prompt, max_tokens=40)
        
        print(f'✅ Response: {response}')
        print('🎉 HuggingFace local model works!')
        
    except Exception as e:
        print(f'❌ Error: {type(e).__name__}: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print('✅ Test passed!')
    sys.exit(0)
