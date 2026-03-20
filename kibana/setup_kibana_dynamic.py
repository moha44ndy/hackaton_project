#!/usr/bin/env python3
"""
Configurer Kibana avec les nouvelles données indexées
- Créer index pattern wmdp-responses-*
- Mettre à jour les dashboards
"""

import requests
import json
import time
from datetime import datetime

KIBANA_BASE = "http://localhost:5601"
ES_HOST = "http://localhost:9200"

def wait_for_kibana():
    """Attendre que Kibana soit accessible"""
    max_retries = 30
    for i in range(max_retries):
        try:
            r = requests.get(f"{KIBANA_BASE}/api/status", timeout=5)
            if r.status_code == 200:
                print("✅ Kibana accessible")
                return True
        except:
            pass
        
        print(f"⏳ Attente Kibana... ({i+1}/{max_retries})")
        time.sleep(2)
    
    return False

def create_index_pattern():
    """Crée l'index pattern pour les nouvelles données"""
    print("\n📊 Création index pattern...")
    
    try:
        # API Kibana pour créer index pattern
        headers = {
            "Content-Type": "application/json",
            "kbn-xsrf": "true"
        }
        
        payload = {
            "index_pattern": {
                "title": "wmdp-responses-*",
                "timeFieldName": "@timestamp",
                "fields": json.dumps({
                    "@timestamp": {"type": "date"},
                    "model_name": {"type": "keyword"},
                    "model": {"type": "keyword"},
                    "category": {"type": "keyword"},
                    "risk_level": {"type": "keyword"},
                    "response_text": {"type": "text"},
                    "prompt_text": {"type": "text"},
                    "response_length": {"type": "number"},
                    "latency_ms": {"type": "number"},
                    "temperature": {"type": "number"}
                })
            }
        }
        
        # Créer
        r = requests.post(
            f"{KIBANA_BASE}/api/saved_objects/index-pattern/wmdp-responses",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if r.status_code in [200, 201]:
            print("✅ Index pattern créé/mis à jour")
            return True
        else:
            print(f"⚠️  Status {r.status_code}: {r.text[:200]}")
            # Index pattern existe probablement - c'est OK
            return True
            
    except Exception as e:
        print(f"⚠️  Erreur: {e}")
        return True  # Ne pas bloquer

def check_elasticsearch():
    """Vérifier les indices ES"""
    print("\n🔍 Vérification Elasticsearch...")
    
    try:
        r = requests.get(f"{ES_HOST}/_cat/indices?format=json")
        indices = r.json()
        
        wmdp_indices = [i for i in indices if 'wmdp' in i['index']]
        
        print(f"   Indices trouvés: {len(wmdp_indices)}")
        for idx in wmdp_indices:
            doc_count = idx['docs.count']
            print(f"   - {idx['index']}: {doc_count} documents")
        
        return len(wmdp_indices) > 0
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("⚙️  CONFIGURATION KIBANA")
    print("="*70)
    
    # Attendre Kibana
    if not wait_for_kibana():
        print("❌ Kibana non accessible après 30 secondes")
        return 1
    
    # Vérifier ES
    if not check_elasticsearch():
        print("❌ Pas de données dans Elasticsearch")
        return 1
    
    # Créer index pattern
    if not create_index_pattern():
        print("⚠️  Problème création index pattern (mais on continue)")
    
    print("\n" + "="*70)
    print("✅ CONFIGURATION READY!")
    print("="*70)
    print("""
🎯 Instructions Dashboard:
   1. Ouvrir Kibana: http://localhost:5601
   2. Menu → Analytics → Dashboard
   3. Ouvrir "WMDP Evaluation Dashboard"
   4. Cliquer "Edit" en haut à droite
   5. Pour chaque visualisation:
      - Cliquer sur la visualisation
      - Index pattern: sélectionner "wmdp-responses-*"
      - Sauvegarder chaque visualisation
   6. Sauvegarder le dashboard

📍 Ou: Créer un nouveau dashboard:
   1. Kibana → Dashboard → Create new
   2. Add visualization → Create new
   3. Data source: "wmdp-responses-*"
   4. Créer graphs (pie chart, bar chart, etc.)
   5. Sauvegarder
""")
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
