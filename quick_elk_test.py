#!/usr/bin/env python3
"""
Final Integration Test: HF Local + ELK
Minimal test - just log some responses to ELK
"""

import sys
from pathlib import Path
from datetime import datetime
import json

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / 'src'))

from dotenv import load_dotenv
load_dotenv(BASE / '.env')

# Test ELK connection
from elasticsearch import Elasticsearch

def main():
    print("="*70)
    print("🚀 Final Integration Test: HF + ELK")
    print("="*70)
    
    # Connect to ELK
    print("\n📮 Connecting to Elasticsearch...")
    try:
        es = Elasticsearch(["http://localhost:9200"])
        health = es.cluster.health()
        print(f"✅ Connected! Status: {health['status']}")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return 1
    
    # Log some test responses
    print("\n📝 Logging test responses to ELK...")
    
    test_responses = [
        {
            "prompt_id": "test-001",
            "model_name": "distilgpt2-local",
            "prompt": "What is machine learning?",
            "response": "Machine learning is a branch of artificial intelligence that enables computers to learn from data.",
            "timestamp": datetime.now().isoformat(),
            "category": "general",
            "risk_level": "low"
        },
        {
            "prompt_id": "test-002",
            "model_name": "distilgpt2-local",
            "prompt": "Explain neural networks.",
            "response": "Neural networks are computational models inspired by biological neural networks.",
            "timestamp": datetime.now().isoformat(),
            "category": "technical",
            "risk_level": "low"
        },
        {
            "prompt_id": "test-003",
            "model_name": "distilgpt2-local",
            "prompt": "What is deep learning?",
            "response": "Deep learning is a subset of machine learning using multiple layers of neural networks.",
            "timestamp": datetime.now().isoformat(),
            "category": "technical",
            "risk_level": "low"
        }
    ]
    
    # Index responses
    for response in test_responses:
        try:
            index_name = f"wmdp-collection-{datetime.now().strftime('%Y.%m.%d')}"
            es.index(index=index_name, document=response)
            print(f"  ✅ Logged: {response['prompt_id']}")
        except Exception as e:
            print(f"  ❌ Failed to log {response['prompt_id']}: {e}")
    
    # Verify in ELK
    print("\n🔍 Verifying data in Elasticsearch...")
    try:
        result = es.search(
            index="wmdp-collection-*",
            body={"size": 0, "track_total_hits": True}
        )
        total = result["hits"]["total"]["value"]
        print(f"✅ Total documents in wmdp-collection: {total}")
    except Exception as e:
        print(f"❌ Query failed: {e}")
    
    # Print Kibana instructions
    print("\n" + "="*70)
    print("🎉 Integration test completed!")
    print("="*70)
    print("\n📊 Next steps to view data in Kibana:")
    print("  1. Open: http://localhost:5601")
    print("  2. Go to: Stack Management → Index Patterns")
    print("  3. Create pattern: wmdp-*")
    print("  4. Go to: Discover")
    print("  5. Select index pattern: wmdp-*")
    print("  6. View your logged responses!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
