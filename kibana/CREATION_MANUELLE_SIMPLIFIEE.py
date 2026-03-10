#!/usr/bin/env python3
"""
Approche directe: Ajouter les visualisations via l'API Discover Saved Search
Méthode fiable pour Kibana 8.12
"""

import requests
import json
import uuid

KIBANA_URL = "http://localhost:5601"
DASHBOARD_ID = "9e3e2f30-18c7-11f1-be7c-d3ae7f9bb369"
INDEX_PATTERN = "wmdp-*"
HEADERS = {"kbn-xsrf": "true"}

def create_saved_search(title, filters=None):
    """Créer une saved search (pour les découvertes)"""
    saved_search_id = str(uuid.uuid4())[:8]
    
    url = f"{KIBANA_URL}/api/saved_objects/search"
    
    payload = {
        "attributes": {
            "title": title,
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "index": f"{INDEX_PATTERN}",
                    "query": {"match_all": {}},
                    "filter": filters or []
                })
            },
            "uiStateJSON": "{}"
        }
    }
    
    resp = requests.post(url, json=payload, headers=HEADERS)
    
    if resp.status_code in [200, 201]:
        result = resp.json()
        return result.get('id')
    return None

def update_dashboard_with_panels():
    """Ajouter les panneaux au dashboard"""
    print("\n🔄 Mise à jour du dashboard...")
    
    url = f"{KIBANA_URL}/api/saved_objects/dashboard/{DASHBOARD_ID}"
    headers = {"kbn-xsrf": "true"}
    
    # Construire les panèles avec des IDs de visualisations existantes
    panels = [
        {
            "version": "8.0.0",
            "gridData": {"x": 0, "y": 0, "w": 8, "h": 3},
            "id": "response-behavior-pie",
            "panelIndex": "0",
            "type": "visualization"
        },
        {
            "version": "8.0.0",
            "gridData": {"x": 8, "y": 0, "w": 8, "h": 3},
            "id": "response-count-bar",
            "panelIndex": "1",
            "type": "visualization"
        },
        {
            "version": "8.0.0",
            "gridData": {"x": 0, "y": 3, "w": 16, "h": 3},
            "id": "avg-latency-bar",
            "panelIndex": "2",
            "type": "visualization"
        }
    ]
    
    payload = {
        "attributes": {
            "panelsJSON": json.dumps(panels),
            "timeRestore": True,
            "timeFrom": "now-30d",
            "timeTo": "now"
        }
    }
    
    resp = requests.put(url, json=payload, headers=HEADERS)
    
    if resp.status_code in [200, 201]:
        print(f"✅ Dashboard mis à jour avec {len(panels)} panneaux")
        return True
    else:
        print(f"❌ Erreur: {resp.text[:500]}")
        return False

def main():
    print("=" * 70)
    print("🛠️  FINALISATION DU DASHBOARD WMDP")
    print("=" * 70)
    
    print("\n📋 Vérification du dashboard existant...")
    resp = requests.get(
        f"{KIBANA_URL}/api/saved_objects/dashboard/{DASHBOARD_ID}",
        headers=HEADERS
    )
    
    if resp.status_code != 200:
        print(f"❌ Dashboard non trouvé")
        return
    
    print(f"✅ Dashboard trouvé: {DASHBOARD_ID}")
    
    # Ajouter les panels
    update_dashboard_with_panels()
    
    print("\n" + "=" * 70)
    print("🎯 ALTERNATIVE: Créer manuellement via Kibana UI")
    print("=" * 70)
    print(f"""
Puisque l'API a des limitations, créons les visualisations manuellement:

ÉTAPE 1: Créer VIS 1 - Response Behavior
✅ Ouvrir: {KIBANA_URL}/app/visualize/
✅ New → Pie Chart
✅ Index: wmdp-*
✅ Metrics: Count of records
✅ Buckets → Segment: Field = response_behavior.keyword
✅ Title: "Response Behavior Distribution"
✅ Save

ÉTAPE 2: Créer VIS 2 - Response Count by Model
✅ New → Bar chart
✅ Index: wmdp-*
✅ Metrics: Count of records
✅ Buckets → X-Axis: Field = model_name.keyword
✅ Title: "Response Count by Model"
✅ Save

ÉTAPE 3: Créer VIS 3 - Average Latency by Model
✅ New → Bar chart
✅ Index: wmdp-*
✅ Metrics: Average of latency_ms
✅ Buckets → X-Axis: Field = model_name.keyword
✅ Title: "Average Latency by Model"
✅ Save

ÉTAPE 4: Créer le Dashboard
✅ New Dashboard
✅ Title: "WMDP Evaluation Dashboard"
✅ Add les 3 visualisations
✅ Position dans la grille
✅ Save
""")

if __name__ == "__main__":
    main()
