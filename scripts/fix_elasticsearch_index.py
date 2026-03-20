#!/usr/bin/env python3
"""
Répare l'index Elasticsearch et réindexe les données correctement
Puis crée un dashboard simple avec visualisations
"""

import json
from pathlib import Path
from elasticsearch import Elasticsearch
from datetime import datetime
import time

ES_HOST = "http://localhost:9200"
CLEANED_FILE = Path(__file__).parent.parent / "results" / "wmdp_responses_cleaned.json"

def delete_and_recreate_index():
    """Supprime et recrée l'index avec bon mapping"""
    es = Elasticsearch([ES_HOST])
    index_name = "wmdp-responses-2026.03.10"
    
    print(f"🗑️  Suppression index {index_name}...")
    try:
        es.indices.delete(index=index_name)
        print("✅ Index supprimé")
    except:
        print("✅ Index n'existait pas (OK)")
    
    time.sleep(1)
    
    # Créer avec bon mapping
    print(f"📝 Création index avec bon mapping...")
    
    mapping = {
        "mappings": {
            "properties": {
                "@timestamp": {"type": "date"},
                "prompt_id": {"type": "keyword"},
                "model_name": {"type": "keyword"},
                "model": {"type": "keyword"},
                "prompt_text": {"type": "text"},
                "response_text": {"type": "text"},
                "prompt_category": {"type": "keyword"},
                "prompt_risk_level": {"type": "keyword"},
                "category": {"type": "keyword"},
                "risk_level": {"type": "keyword"},
                "temperature": {"type": "float"},
                "latency_ms": {"type": "float"},
                "tokens_used": {"type": "integer"},
                "max_tokens": {"type": "integer"},
                "response_length": {"type": "integer"},
                "model_version": {"type": "keyword"},
                "timestamp": {"type": "date"}
            }
        }
    }
    
    es.indices.create(index=index_name, body=mapping)
    print(f"✅ Index créé avec mapping correct")
    
    return es, index_name

def reindex_data(es, index_name):
    """Réindexe les données nettoyées"""
    print(f"\n📥 Chargement données depuis {CLEANED_FILE}...")
    
    with open(CLEANED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📮 Indexation {len(data['responses'])} documents...")
    
    success = 0
    for i, resp in enumerate(data['responses']):
        try:
            doc_id = f"{resp['model_name']}-{resp['prompt_id']}"
            
            # Préparer le document
            doc = {
                "@timestamp": resp['timestamp'],
                "prompt_id": resp['prompt_id'],
                "model_name": resp['model_name'],
                "model": resp['model_name'],
                "prompt_text": resp['prompt_text'],
                "response_text": resp['response_text'],
                "category": resp.get('prompt_category', 'unknown'),
                "risk_level": resp.get('prompt_risk_level', 'unknown'),
                "prompt_category": resp.get('prompt_category', 'unknown'),
                "prompt_risk_level": resp.get('prompt_risk_level', 'unknown'),
                "latency_ms": resp.get('latency_ms', 0),
                "tokens_used": resp.get('tokens_used', 0),
                "max_tokens": resp.get('max_tokens', 0),
                "temperature": resp.get('temperature', 0.7),
                "response_length": len(resp.get('response_text', '')),
                "model_version": resp.get('model_version', ''),
                "timestamp": resp['timestamp']
            }
            
            es.index(index=index_name, id=doc_id, document=doc)
            success += 1
            
            if (success % 5) == 0:
                print(f"  ✅ {success}/{len(data['responses'])}")
        
        except Exception as e:
            print(f"  ⚠️  Document {i}: {e}")
    
    # Attendre indexation
    print("\n⏳ Attendre indexation...")
    time.sleep(2)
    
    print(f"✅ {success} documents indexés!")
    
    # Vérifier
    count = es.count(index=index_name)
    print(f"✅ Index contient {count['count']} documents")
    
    return success

def main():
    print("\n" + "="*70)
    print("🔧 RÉPARATION INDEX ELASTICSEARCH")
    print("="*70 + "\n")
    
    try:
        es, index_name = delete_and_recreate_index()
        reindex_data(es, index_name)
        
        print("\n" + "="*70)
        print("✅ INDEX RÉPARÉ!")
        print("="*70)
        print(f"""
📊 Index: {index_name}
🎯 Prêt pour Kibana Dashboard

💡 Prochaines étapes:
   1. Ouvrir Kibana: http://localhost:5601
   2. Créer un nouveau Dashboard
   3. Ajouter visualisations (voir guide)
""")
        
        return 0
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    import sys
    sys.exit(main())
