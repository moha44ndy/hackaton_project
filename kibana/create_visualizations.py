#!/usr/bin/env python3
"""
Créer les 3 visualisations WMDP directement via l'API Kibana
"""

import requests
import json

KIBANA_URL = "http://localhost:5601"
INDEX = "wmdp-*"

headers = {"kbn-xsrf": "true"}

def create_visualization(vis_id, title, vis_type, aggs, bucket_agg=None):
    """Créer une visualisation"""
    
    url = f"{KIBANA_URL}/api/saved_objects/visualization/{vis_id}"
    
    vis_state = {
        "title": title,
        "type": vis_type,
        "params": {
            "addTooltip": True,
            "addLegend": True,
            "isDonut" if vis_type == "pie" else "legendPosition": "right" if vis_type == "pie" else "bottom"
        },
        "aggs": aggs
    }
    
    if bucket_agg:
        vis_state["aggs"].append(bucket_agg)
    
    data = {
        "attributes": {
            "title": title,
            "visStateJSON": json.dumps(vis_state),
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": INDEX,
                    "query": {"match_all": {}},
                    "filter": []
                })
            }
        }
    }
    
    print(f"\n📊 Création: {title}")
    try:
        resp = requests.post(url, json=data, headers=headers)
        if resp.status_code in [200, 201]:
            print(f"   ✅ Créée (ID: {vis_id})")
            return True
        else:
            print(f"   ❌ Erreur {resp.status_code}: {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

print("\n" + "="*70)
print("📊 CRÉER LES VISUALISATIONS WMDP")
print("="*70)

# Vis 1: Response Behavior Distribution (Pie)
create_visualization(
    "response-behavior-dist",
    "Response Behavior Distribution",
    "pie",
    [{"id": "1", "enabled": True, "type": "count", "schema": "metric", "params": {}}],
    {"id": "2", "enabled": True, "type": "terms", "schema": "segment", "params": {
        "field": "response_behavior.keyword", "size": 10, "order": "desc", "orderBy": "1"
    }}
)

# Vis 2: Response Count by Model (Bar)
create_visualization(
    "response-count-by-model",
    "Response Count by Model",
    "histogram",
    [{"id": "1", "enabled": True, "type": "count", "schema": "metric", "params": {}}],
    {"id": "2", "enabled": True, "type": "terms", "schema": "segment", "params": {
        "field": "model_name.keyword", "size": 10, "order": "desc", "orderBy": "1"
    }}
)

# Vis 3: Average Latency by Model (Bar)
create_visualization(
    "avg-latency-by-model",
    "Average Latency by Model",
    "histogram",
    [{"id": "1", "enabled": True, "type": "avg", "schema": "metric", "params": {"field": "latency_ms"}}],
    {"id": "2", "enabled": True, "type": "terms", "schema": "segment", "params": {
        "field": "model_name.keyword", "size": 10, "order": "desc", "orderBy": "1"
    }}
)

print("\n" + "="*70)
print("✅ Visualisations créées!")
print("="*70)
