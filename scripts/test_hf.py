import os
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(BASE / 'src'))

from llm_clients import LLMClientFactory

if __name__ == '__main__':
    token = os.getenv('HUGGINGFACE_TOKEN') or os.getenv('HF_TOKEN')
    if not token:
        print('Hugging Face token not found in env. Set HUGGINGFACE_TOKEN or HF_TOKEN.')
        print('This script will not run a live test without the token and required packages.')
        sys.exit(2)

    try:
        client = LLMClientFactory.create_client('huggingface', model='HuggingFaceH4/zephyr-7b-beta', api_key=token)
    except Exception as e:
        print('Could not create Hugging Face client:', e)
        print('Ensure huggingface_hub (and transformers if local) are installed: pip install huggingface_hub transformers torch')
        sys.exit(2)

    try:
        prompt = 'Say one short friendly sentence about yourself.'
        print('Sending prompt:', prompt)
        resp, meta = client.generate(prompt=prompt, max_tokens=60)
        print('Response:', resp)
        print('Metadata:', meta)
    except Exception as e:
        print('Error during HF request:', e)
        sys.exit(1)
