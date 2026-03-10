#!/usr/bin/env python3
"""
Créer et ajouter les visualisations au dashboard WMDP
Approche: Créer via lens + ajouter au dashboard existant
"""

import requests
import json
import uuid

KIBANA_URL = "http://localhost:5601"
DASHBOARD_ID = "9e3e2f30-18c7-11f1-be7c-d3ae7f9bb369"
HEADERS = {"kbn-xsrf": "true", "Content-Type": "application/json"}

def create_lens_visualization(title, layers, description=""):
    """Créer une visualisation Lens (plus compatible Kibana 8.12)"""
    print(f"\n📊 Création: {title}")
    
    vis_id = str(uuid.uuid4())[:8]
    
    url = f"{KIBANA_URL}/api/saved_objects/lens/{vis_id}"
    
    payload = {
        "attributes": {
            "title": title,
            "description": description,
            "visualization": {"layerOrder": list(range(len(layers))), "layers": layers},
            "state": {
                "datasourceStates": {"formBased": {"layers": {}}},
                "visualization": {}
            }
        }
    }
    
    resp = requests.post(url, json=payload, headers=HEADERS, params={"overwrite": "true"})
    
    if resp.status_code in [200, 201]:
        result = resp.json()
        vis_id_actual = result.get('id', vis_id)
        print(f"✅ Créé: {vis_id_actual}")
        return vis_id_actual
    else:
        print(f"⚠️  Erreur ({resp.status_code}): {resp.text[:300]}")
        return None

def add_panel_to_dashboard(dashboard_id, panel_id, x, y, w, h, panel_type="visualization"):
    """Ajouter un panel au dashboard"""
    print(f"   ➕ Ajout au dashboard...")
    
    # Récupérer le dashboard actuel
    url = f"{KIBANA_URL}/api/saved_objects/dashboard/{dashboard_id}"
    resp = requests.get(url, headers=HEADERS)
    
    if resp.status_code != 200:
        print(f"   ❌ Impossible de lire le dashboard")
        return False
    
    dashboard = resp.json()
    panels = json.loads(dashboard["attributes"].get("panelsJSON", "[]"))
    
    # Ajouter le nouveau panel
    panel_index = len(panels)
    new_panel = {
        "version": "8.0.0",
        "gridData": {"x": x, "y": y, "w": w, "h": h},
        "id": panel_id,
        "panelIndex": str(panel_index),
        "type": panel_type,
        "embeddableConfig": {}
    }
    
    panels.append(new_panel)
    
    # Mettre à jour le dashboard
    dashboard["attributes"]["panelsJSON"] = json.dumps(panels)
    
    resp = requests.put(url, json={"attributes": dashboard["attributes"]}, headers=HEADERS)
    
    if resp.status_code in [200, 201]:
        print(f"   ✅ Panel ajouté au dashboard")
        return True
    else:
        print(f"   ❌ Erreur: {resp.text[:300]}")
        return False

def main():
    print("=" * 70)
    print("🔧 CRÉATION DES VISUALISATIONS POUR LE DASHBOARD WMDP")
    print("=" * 70)
    
    # VIS 1: Pie chart - Response Behavior
    layers_1 = [{
        "layerId": "layer1",
        "sourceId": "wmdp-*",
        "columnOrder": ["response_behavior_field", "count_metric"],
        "columns": [
            {
                "columnId": "response_behavior_field",
                "operation": {
                    "label": "response_behavior",
                    "dataType": "string",
                    "sourceId": "wmdp-*",
                    "isBucketed": True,
                    "scale": "ordinal",
                    "operationType": "terms",
                    "params": {"size": 10, "orderBy": {"type": "metrics", "columnId": "count_metric"}, "orderDirection": "descending"}
                }
            },
            {
                "columnId": "count_metric",
                "operation": {
                    "label": "Count",
                    "dataType": "number",
                    "sourceId": "wmdp-*",
                    "isBucketed": False,
                    "scale": "ratio",
                    "operationType": "count"
                }
            }
        ]
    }]
    
    vis1_id = create_lens_visualization(
        "Response Behavior Distribution",
        layers_1,
        "Distribution des comportements de réponse (safe/unsafe)"
    )
    if vis1_id:
        add_panel_to_dashboard(DASHBOARD_ID, vis1_id, 0, 0, 8, 3)
    
    # VIS 2: Bar chart - Count by Model
    layers_2 = [{
        "layerId": "layer2",
        "sourceId": "wmdp-*",
        "columnOrder": ["model_field", "count_metric"],
        "columns": [
            {
                "columnId": "model_field",
                "operation": {
                    "label": "model_name",
                    "dataType": "string",
                    "sourceId": "wmdp-*",
                    "isBucketed": True,
                    "scale": "ordinal",
                    "operationType": "terms",
                    "params": {"size": 10, "orderBy": {"type": "metrics", "columnId": "count_metric"}, "orderDirection": "descending"}
                }
            },
            {
                "columnId": "count_metric",
                "operation": {
                    "label": "Count",
                    "dataType": "number",
                    "sourceId": "wmdp-*",
                    "isBucketed": False,
                    "scale": "ratio",
                    "operationType": "count"
                }
            }
        ]
    }]
    
    vis2_id = create_lens_visualization(
        "Response Count by Model",
        layers_2,
        "Nombre de réponses par modèle de langage"
    )
    if vis2_id:
        add_panel_to_dashboard(DASHBOARD_ID, vis2_id, 8, 0, 8, 3)
    
    # VIS 3: Bar chart - Avg Latency by Model
    layers_3 = [{
        "layerId": "layer3",
        "sourceId": "wmdp-*",
        "columnOrder": ["model_field", "avg_latency"],
        "columns": [
            {
                "columnId": "model_field",
                "operation": {
                    "label": "model_name",
                    "dataType": "string",
                    "sourceId": "wmdp-*",
                    "isBucketed": True,
                    "scale": "ordinal",
                    "operationType": "terms",
                    "params": {"size": 10, "orderBy": {"type": "metrics", "columnId": "avg_latency"}, "orderDirection": "descending"}
                }
            },
            {
                "columnId": "avg_latency",
                "operation": {
                    "label": "Avg Latency",
                    "dataType": "number",
                    "sourceId": "wmdp-*",
                    "isBucketed": False,
                    "scale": "ratio",
                    "operationType": "average",
                    "params": {"field": "latency_ms"}
                }
            }
        ]
    }]
    
    vis3_id = create_lens_visualization(
        "Average Latency by Model",
        layers_3,
        "Latence moyenne de réponse par modèle"
    )
    if vis3_id:
        add_panel_to_dashboard(DASHBOARD_ID, vis3_id, 0, 3, 16, 3)
    
    print("\n" + "=" * 70)
    print("✅ TERMINÉ!")
    print("=" * 70)
    print(f"\n🔗 Accédez au dashboard:")
    print(f"   http://localhost:5601/app/dashboards/view/{DASHBOARD_ID}")
    print("\n⚠️  Si le dashboard affiche 'No data':")
    print("   1. Clic sur le sélecteur de dates (haut droite)")
    print("   2. Sélectionner 'Last 30 days'")
    print("   3. Clic 'Update'")

if __name__ == "__main__":
    main()
