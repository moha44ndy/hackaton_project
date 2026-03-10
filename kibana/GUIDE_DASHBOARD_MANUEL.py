#!/usr/bin/env python3
"""
Script Kibana v8.12+ compatible pour créer les visualisations WMDP
Format adapté pour les strict mappings de Kibana 8.x
"""

import requests
import json

KIBANA_BASE = "http://localhost:5601"
INDEX_PATTERN = "wmdp-*"

def create_vis_response_behavior():
    """Créer visualisation: Response Behavior Distribution (Donut)"""
    print("\n📊 Création: Response Behavior Distribution")
    
    url = f"{KIBANA_BASE}/api/vis"
    headers = {"kbn-xsrf": "true", "Content-Type": "application/json"}
    
    # Format compatible Kibana 8.x
    payload = {
        "title": "Response Behavior Distribution",
        "type": "pie",
        "params": {
            "addTooltip": True,
            "addLegend": True,
            "isDonut": True,
            "legendPosition": "right"
        },
        "aggs": [
            {
                "id": "1",
                "enabled": True,
                "type": "count",
                "schema": "metric",
                "params": {}
            },
            {
                "id": "2",
                "enabled": True,
                "type": "terms",
                "schema": "segment",
                "params": {
                    "field": "response_behavior.keyword",
                    "size": 10,
                    "order": "desc",
                    "orderBy": "1"
                }
            }
        ],
        "kibanaSavedObjectMeta": {
            "searchSourceJSON": {
                "index": INDEX_PATTERN,
                "query": {"match_all": {}},
                "filter": []
            }
        }
    }
    
    resp = requests.post(url, json=payload, headers=headers)
    if resp.status_code in [200, 201]:
        vis_id = resp.json()["_id"]
        print(f"✅ Visualization créée: {vis_id}")
        return vis_id
    else:
        print(f"❌ Erreur: {resp.status_code} - {resp.text[:200]}")
        return None

def main():
    print("=" * 60)
    print("🔧 Approche alternative: Vérification des indices")
    print("=" * 60)
    
    # Vérifier les données dans Elasticsearch
    resp = requests.get("http://localhost:9200/wmdp-*/_search?size=1&pretty")
    if resp.status_code == 200:
        data = resp.json()
        count = data['hits']['total']['value']
        print(f"✅ Documents disponibles dans ES: {count}")
        
        if count > 0:
            doc = data['hits']['hits'][0]['_source']
            print(f"\n📋 Exemple de document:")
            print(json.dumps(doc, indent=2, default=str)[:500])
    
    print("\n" + "=" * 60)
    print("🎯 GUIDE MANUEL - Créer les visualisations via Kibana UI")
    print("=" * 60)
    print("""
OPTION 1: VIA KIBANA DISCOVER
==============================
1. Ouvrir: http://localhost:5601/app/discover
2. Index Pattern: 'wmdp-*'
3. Time Range: "Last 7 days" (important!)
4. Clic "Save" → Save as Visualization

VIS 1: Response Behavior Distribution (Pie Chart)
--------------------------------------------------
1. Create → Visualization
2. Type: Pie Chart
3. Document: wmdp-*
4. Metrics: Count of records
5. Buckets → Segment:
   - Field: response_behavior.keyword
   - Display: Top 10 (default)
6. Save as: "Response Behavior Distribution"

VIS 2: Response Count by Model (Bar Chart)
-------------------------------------------
1. Create → Visualization
2. Type: Bar (Vertical)
3. Document: wmdp-*
4. Metrics: Count of records
5. Buckets → X-axis (Segment):
   - Field: model_name.keyword
   - Size: 10
6. Save as: "Response Count by Model"

VIS 3: Average Latency by Model (Bar Chart)
--------------------------------------------
1. Create → Visualization
2. Type: Bar (Vertical)
3. Document: wmdp-*
4. Metrics: 
   - Type: Average
   - Field: latency_ms
5. Buckets → X-axis (Segment):
   - Field: model_name.keyword
   - Size: 10
6. Save as: "Average Latency by Model"

PUIS CRÉER LE DASHBOARD
=======================
1. Menu → Dashboards → Create Dashboard
2. Nommer: "WMDP Evaluation Dashboard"
3. Ajouter les 3 visualisations
4. Arrange: position les 3 visualisations
5. Save

⚠️ IMPORTANT: Vérifier la TIME RANGE en haut à droite!
    Doit inclure la date des données (2026-03-02 et +)
""")

if __name__ == "__main__":
    main()
