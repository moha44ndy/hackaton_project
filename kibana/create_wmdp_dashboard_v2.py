#!/usr/bin/env python3
"""
Script pour créer un Dashboard WMDP dans Kibana
- Visualisation 1: Response Behavior Distribution
- Visualisation 2: Response Count by Model
- Visualisation 3: Average Latency by Model
"""

import requests
import json
import uuid
from datetime import datetime

KIBANA_BASE = "http://localhost:5601"
ES_BASE = "http://localhost:9200"

# Configuration
SPACE_ID = "default"
INDEX_PATTERN = "wmdp-*"

def get_or_create_index_pattern():
    """Créer ou récupérer l'index pattern"""
    print("📋 Étape 1: Vérifier/Créer l'index pattern...")
    
    # Chercher l'index pattern existant
    url = f"{KIBANA_BASE}/api/saved_objects/index-pattern"
    headers = {"kbn-xsrf": "true"}
    
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        patterns = resp.json().get("saved_objects", [])
        for pattern in patterns:
            if pattern["attributes"].get("title") == INDEX_PATTERN:
                print(f"✅ Index pattern '{INDEX_PATTERN}' trouvé: {pattern['id']}")
                return pattern['id']
    
    # Créer le pattern
    print(f"📝 Création du pattern '{INDEX_PATTERN}'...")
    payload = {
        "attributes": {
            "title": INDEX_PATTERN,
            "timeFieldName": "timestamp",
            "fields": "[]"
        }
    }
    
    resp = requests.post(url, json=payload, headers=headers)
    if resp.status_code in [200, 201]:
        pattern_id = resp.json()["id"]
        print(f"✅ Pattern créé: {pattern_id}")
        return pattern_id
    else:
        print(f"❌ Erreur: {resp.text}")
        return None

def create_visualization(index_pattern_id, vis_title, vis_type, config):
    """Créer une visualisation"""
    print(f"\n📊 Création: {vis_title}")
    
    url = f"{KIBANA_BASE}/api/saved_objects/visualization"
    headers = {"kbn-xsrf": "true"}
    
    vis_id = str(uuid.uuid4())
    
    payload = {
        "attributes": {
            "title": vis_title,
            "visStateJSON": json.dumps(config),
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": index_pattern_id,
                    "query": {"match_all": {}},
                    "filter": []
                })
            }
        }
    }
    
    resp = requests.post(url, json=payload, headers=headers)
    if resp.status_code in [200, 201]:
        vis_obj = resp.json()
        print(f"✅ {vis_title}: {vis_obj['id']}")
        return vis_obj['id']
    else:
        print(f"❌ Erreur: {resp.text}")
        return None

def create_dashboard(panel_ids):
    """Créer le dashboard avec les visualisations"""
    print("\n🎨 Création du dashboard WMDP")
    
    url = f"{KIBANA_BASE}/api/saved_objects/dashboard"
    headers = {"kbn-xsrf": "true"}
    
    # Construire les panneaux
    panels = []
    positions = [
        {"x": 0, "y": 0, "w": 8, "h": 3},   # Response Behavior (haut gauche)
        {"x": 8, "y": 0, "w": 8, "h": 3},   # Response by Model (haut droite)
        {"x": 0, "y": 3, "w": 16, "h": 3},  # Avg Latency (bas, full width)
    ]
    
    for i, panel_id in enumerate(panel_ids):
        if panel_id:
            pos = positions[i] if i < len(positions) else {"x": 0, "y": 6, "w": 8, "h": 3}
            panels.append({
                "version": "8.0.0",
                "gridData": pos,
                "id": panel_id,
                "panelIndex": str(i),
                "embeddableConfig": {}
            })
    
    payload = {
        "attributes": {
            "title": "WMDP Evaluation Dashboard",
            "description": "Tableau de bord principal pour l'évaluation WMDP des LLMs",
            "panelsJSON": json.dumps(panels),
            "timeRestore": True,
            "timeFrom": "now-30d",
            "timeTo": "now",
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "query": {"match_all": {}},
                    "filter": []
                })
            }
        }
    }
    
    resp = requests.post(url, json=payload, headers=headers)
    if resp.status_code in [200, 201]:
        dashboard_id = resp.json()["id"]
        print(f"✅ Dashboard créé: {dashboard_id}")
        return dashboard_id
    else:
        print(f"❌ Erreur: {resp.text}")
        return None

def main():
    print("=" * 60)
    print("🚀 CRÉATION DASHBOARD KIBANA - WMDP EVALUATION")
    print("=" * 60)
    
    # Étape 1: Index Pattern
    index_pattern_id = get_or_create_index_pattern()
    if not index_pattern_id:
        print("❌ Impossible de créer l'index pattern")
        return
    
    # Étape 2: Visualisations
    panel_ids = []
    
    # VIS 1: Response Behavior Distribution (Donut)
    vis1_config = {
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
                    "orderBy": "1",
                    "customLabel": "Behavior"
                }
            }
        ]
    }
    
    pid1 = create_visualization(index_pattern_id, "Response Behavior Distribution", "pie", vis1_config)
    panel_ids.append(pid1)
    
    # VIS 2: Response Count by Model (Bar)
    vis2_config = {
        "title": "Response Count by Model",
        "type": "histogram",
        "params": {
            "type": "histogram",
            "grid": {"categoryLines": False},
            "categoryAxes": [
                {
                    "id": "CategoryAxis-1",
                    "type": "category",
                    "position": "bottom",
                    "show": True,
                    "style": {},
                    "scale": {"type": "linear"},
                    "labels": {"show": True, "truncate": 100},
                    "title": {}
                }
            ],
            "valueAxes": [
                {
                    "id": "ValueAxis-1",
                    "name": "Left",
                    "type": "value",
                    "position": "left",
                    "show": True,
                    "style": {},
                    "scale": {"type": "linear", "mode": "normal"},
                    "labels": {"show": True, "rotation": 0},
                    "title": {"text": "Count"}
                }
            ],
            "tooltip": {"show": True, "showDelay": 500}
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
                    "field": "model_name.keyword",
                    "size": 10,
                    "order": "desc",
                    "orderBy": "1",
                    "customLabel": "Model"
                }
            }
        ]
    }
    
    pid2 = create_visualization(index_pattern_id, "Response Count by Model", "histogram", vis2_config)
    panel_ids.append(pid2)
    
    # VIS 3: Average Latency by Model (Bar)
    vis3_config = {
        "title": "Average Latency by Model",
        "type": "histogram",
        "params": {
            "type": "histogram",
            "grid": {"categoryLines": False},
            "categoryAxes": [
                {
                    "id": "CategoryAxis-1",
                    "type": "category",
                    "position": "bottom",
                    "show": True,
                    "style": {},
                    "scale": {"type": "linear"},
                    "labels": {"show": True, "truncate": 100},
                    "title": {}
                }
            ],
            "valueAxes": [
                {
                    "id": "ValueAxis-1",
                    "name": "Left",
                    "type": "value",
                    "position": "left",
                    "show": True,
                    "style": {},
                    "scale": {"type": "linear", "mode": "normal"},
                    "labels": {"show": True, "rotation": 0},
                    "title": {"text": "Avg Latency (ms)"}
                }
            ],
            "tooltip": {"show": True, "showDelay": 500}
        },
        "aggs": [
            {
                "id": "1",
                "enabled": True,
                "type": "avg",
                "schema": "metric",
                "params": {
                    "field": "latency_ms",
                    "customLabel": "Avg Latency"
                }
            },
            {
                "id": "2",
                "enabled": True,
                "type": "terms",
                "schema": "segment",
                "params": {
                    "field": "model_name.keyword",
                    "size": 10,
                    "order": "desc",
                    "orderBy": "1",
                    "customLabel": "Model"
                }
            }
        ]
    }
    
    pid3 = create_visualization(index_pattern_id, "Average Latency by Model", "histogram", vis3_config)
    panel_ids.append(pid3)
    
    # Étape 3: Dashboard
    dashboard_id = create_dashboard(panel_ids)
    
    if dashboard_id:
        print("\n" + "=" * 60)
        print("✅ DASHBOARD CRÉÉ AVEC SUCCÈS!")
        print("=" * 60)
        print(f"\n🔗 Accédez au dashboard:")
        print(f"   http://localhost:5601/app/dashboards/view/{dashboard_id}")
        print("\n📝 Résumé:")
        print(f"   - Index Pattern: {INDEX_PATTERN}")
        print(f"   - Visualisations: 3")
        print(f"     1. Response Behavior Distribution (Pie chart)")
        print(f"     2. Response Count by Model (Bar chart)")
        print(f"     3. Average Latency by Model (Bar chart)")
        print("=" * 60)
    else:
        print("❌ Erreur lors de la création du dashboard")

if __name__ == "__main__":
    main()
