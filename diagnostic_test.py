#!/usr/bin/env python3
"""
Diagnostic Complet: ELK ↔ HuggingFace ↔ Benchmark
Vérifie que tout est connecté et fonctionne ensemble
"""

import sys
from pathlib import Path
import json
from datetime import datetime

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / 'src'))

from dotenv import load_dotenv
load_dotenv(BASE / '.env')

def test_elk():
    """Teste la connexion ELK"""
    print("\n" + "="*70)
    print("🔌 TEST 1: Elasticsearch (ELK)")
    print("="*70)
    
    try:
        from elasticsearch import Elasticsearch
        es = Elasticsearch(["http://localhost:9200"])
        
        # Health check
        health = es.cluster.health()
        print(f"✅ Status: {health['status']}")
        print(f"   Nodes: {health['number_of_nodes']}")
        print(f"   Shards: {health['active_shards']}")
        
        # Count documents
        indices = es.cat.indices(format='json')
        wmdp_indices = [i for i in indices if 'wmdp' in i['index']]
        total_docs = sum(int(i['docs.count']) for i in wmdp_indices)
        
        print(f"\n✅ WMDP Indices: {len(wmdp_indices)}")
        for idx in wmdp_indices:
            print(f"   - {idx['index']}: {idx['docs.count']} docs")
        
        print(f"\n✅ Total Documents in ELK: {total_docs}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_kibana():
    """Teste Kibana"""
    print("\n" + "="*70)
    print("📊 TEST 2: Kibana Dashboard")
    print("="*70)
    
    try:
        import requests
        response = requests.get("http://localhost:5601/api/status", timeout=5)
        if response.status_code == 200:
            print("✅ Kibana: Accessible at http://localhost:5601")
            data = response.json()
            print(f"   Version: {data.get('version', {}).get('number', 'N/A')}")
            return True
        else:
            print(f"❌ Kibana returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_huggingface():
    """Teste HuggingFace local"""
    print("\n" + "="*70)
    print("🤗 TEST 3: HuggingFace Local Model")
    print("="*70)
    
    try:
        from hf_client import HuggingFaceLocalClient
        
        print("📥 Loading distilgpt2 model...")
        client = HuggingFaceLocalClient(model_id="distilgpt2", device="cpu")
        
        prompt = "What is AI safety?"
        print(f"\n📝 Test Prompt: {prompt}")
        
        response = client.generate_response(prompt, max_tokens=40)
        print(f"✅ Response: {response[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_end_to_end():
    """Test complet: HF → ELK"""
    print("\n" + "="*70)
    print("🔗 TEST 4: End-to-End (HF → ELK)")
    print("="*70)
    
    try:
        from hf_client import HuggingFaceLocalClient
        from elasticsearch import Elasticsearch
        
        # Generate response with HF
        print("🤗 Generating response with HuggingFace...")
        hf = HuggingFaceLocalClient(model_id="distilgpt2", device="cpu")
        prompt = "Explain machine learning"
        response = hf.generate_response(prompt, max_tokens=50)
        
        # Log to ELK
        print("📮 Logging to Elasticsearch...")
        es = Elasticsearch(["http://localhost:9200"])
        index_name = f"wmdp-benchmark-{datetime.now().strftime('%Y.%m.%d')}"
        
        doc = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "response": response,
            "model": "distilgpt2-local",
            "test_type": "end-to-end",
            "status": "success"
        }
        
        result = es.index(index=index_name, document=doc)
        doc_id = result['_id']
        
        print(f"✅ Document indexed: {doc_id}")
        print(f"   Index: {index_name}")
        print(f"   Timestamp: {doc['timestamp']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def generate_diagnostic_report():
    """Génère un rapport diagnostic"""
    print("\n" + "="*70)
    print("📋 DIAGNOSTIC REPORT")
    print("="*70)
    
    results = {
        "elasticsearch": test_elk(),
        "kibana": test_kibana(),
        "huggingface": test_huggingface(),
        "end_to_end": test_end_to_end()
    }
    
    print("\n" + "="*70)
    print("🎯 SUMMARY")
    print("="*70)
    
    status = "✅ ALL SYSTEMS OPERATIONAL" if all(results.values()) else "⚠️ SOME ISSUES"
    print(f"\nStatus: {status}\n")
    
    components = [
        ("Elasticsearch", results["elasticsearch"]),
        ("Kibana", results["kibana"]),
        ("HuggingFace Local", results["huggingface"]),
        ("End-to-End Pipeline", results["end_to_end"])
    ]
    
    for name, status_val in components:
        icon = "✅" if status_val else "❌"
        print(f"{icon} {name}")
    
    print("\n" + "="*70)
    print("🚀 NEXT STEPS")
    print("="*70)
    
    if all(results.values()):
        print("""
✅ All systems connected and working!

Run Full Benchmark:
  python run_hf_test.py
  
View Results in Kibana:
  1. Open: http://localhost:5601
  2. Create index pattern: wmdp-benchmark-*
  3. Go to Discover to see live graphs updating
  
Run Custom Evaluation:
  python src/wmdp_pipeline.py --model distilgpt2-local --num-prompts 64
  
The graphs in Kibana will update in REAL-TIME as new tests run! 📊
        """)
    else:
        print("\n⚠️ Some components need attention. Check errors above.")
    
    return all(results.values())


if __name__ == "__main__":
    success = generate_diagnostic_report()
    sys.exit(0 if success else 1)
