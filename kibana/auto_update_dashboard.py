#!/usr/bin/env python3
"""
Script: Mets à jour automatiquement le dashboard WMDP pour charger les nouvelles données
- Cherche le dashboard WMDP existant
- Mets à jour toutes les visualisations pour pointer sur wmdp-responses-*
- Sauvegarde automatiquement
"""

import requests
import json
import sys
from typing import Dict, List, Optional

KIBANA_BASE = "http://localhost:5601"
ES_HOST = "http://localhost:9200"

class KibanaAPI:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "kbn-xsrf": "true"
        }
    
    def find_dashboards(self, pattern: str = "wmdp") -> List[Dict]:
        """Trouve tous les dashboards WMDP"""
        try:
            url = f"{self.base_url}/api/saved_objects/dashboard"
            r = requests.get(url, headers=self.headers, params={"search": pattern})
            
            if r.status_code == 200:
                dashboards = r.json().get("saved_objects", [])
                print(f"📊 {len(dashboards)} dashboard(s) trouvé(s)")
                return dashboards
            else:
                print(f"❌ Erreur recherche: {r.status_code}")
                return []
        except Exception as e:
            print(f"❌ {e}")
            return []
    
    def get_dashboard(self, dashboard_id: str) -> Optional[Dict]:
        """Récupère un dashboard par ID"""
        try:
            url = f"{self.base_url}/api/saved_objects/dashboard/{dashboard_id}"
            r = requests.get(url, headers=self.headers)
            
            if r.status_code == 200:
                return r.json()
            else:
                print(f"❌ Dashboard {dashboard_id} non trouvé")
                return None
        except Exception as e:
            print(f"❌ {e}")
            return None
    
    def update_dashboard(self, dashboard_id: str, dashboard: Dict) -> bool:
        """Met à jour un dashboard"""
        try:
            url = f"{self.base_url}/api/saved_objects/dashboard/{dashboard_id}"
            r = requests.put(url, headers=self.headers, json={"attributes": dashboard["attributes"]})
            
            if r.status_code == 200:
                print(f"✅ Dashboard {dashboard_id} mis à jour")
                return True
            else:
                print(f"⚠️  Status {r.status_code}")
                return False
        except Exception as e:
            print(f"❌ {e}")
            return False
    
    def find_visualizations(self, pattern: str = "wmdp") -> List[Dict]:
        """Trouve toutes les visualisations WMDP"""
        try:
            url = f"{self.base_url}/api/saved_objects/visualization"
            r = requests.get(url, headers=self.headers, params={"search": pattern, "per_page": 100})
            
            if r.status_code == 200:
                visuals = r.json().get("saved_objects", [])
                print(f"📈 {len(visuals)} visualisation(s) trouvée(s)")
                return visuals
            else:
                return []
        except:
            return []
    
    def update_visualization(self, vis_id: str, vis_data: Dict) -> bool:
        """Met à jour une visualisation pour pointer sur le nouvel index"""
        try:
            # Récupérer la visualisation
            url = f"{self.base_url}/api/saved_objects/visualization/{vis_id}"
            r = requests.get(url, headers=self.headers)
            
            if r.status_code != 200:
                return False
            
            vis = r.json()
            
            # Vérifier si elle utilise un index
            if "kibanaSavedObjectMeta" not in vis["attributes"]:
                return True  # Pas d'index, skip
            
            # Mettre à jour l'index pattern
            search_source = json.loads(
                vis["attributes"].get("kibanaSavedObjectMeta", {}).get("searchSourceJSON", "{}")
            )
            
            # Chercher l'ancien index pattern
            if "index" in search_source:
                old_index = search_source["index"]
                print(f"  - {vis['attributes']['title']}: {old_index} → wmdp-responses-2026.03.10")
                
                search_source["index"] = "wmdp-responses-2026.03.10"
                
                vis["attributes"]["kibanaSavedObjectMeta"]["searchSourceJSON"] = json.dumps(search_source)
                
                # Sauvegarder
                r = requests.put(url, headers=self.headers, json={"attributes": vis["attributes"]})
                return r.status_code == 200
            
            return True
            
        except Exception as e:
            print(f"  ⚠️  {e}")
            return True

def main():
    print("\n" + "="*70)
    print("🔄 MISE À JOUR AUTOMATIQUE DASHBOARD WMDP")
    print("="*70 + "\n")
    
    api = KibanaAPI(KIBANA_BASE)
    
    # Chercher dashboards
    print("🔍 Cherche dashboards WMDP...")
    dashboards = api.find_dashboards("wmdp")
    
    if not dashboards:
        print("❌ Aucun dashboard WMDP trouvé")
        print("\n💡 Options:")
        print("   1. Créer manuellement: Kibana → Dashboard → Create new")
        print("   2. Importer: Kibana → Stack Management → Saved Objects")
        return 1
    
    # Chercher visualisations
    print("\n🔍 Cherche visualisations WMDP...")
    visuals = api.find_visualizations("wmdp")
    
    if visuals:
        print(f"\n♻️  Mise à jour {len(visuals)} visualisation(s)...")
        updated = 0
        for vis in visuals:
            if api.update_visualization(vis["id"], vis):
                updated += 1
        print(f"✅ {updated}/{len(visuals)} visualisations mises à jour")
    
    # Mettre à jour dashboards
    print(f"\n♻️  Mise à jour {len(dashboards)} dashboard(s)...")
    for dashboard in dashboards:
        api.update_dashboard(dashboard["id"], dashboard)
    
    print("\n" + "="*70)
    print("✅ DASHBOARD PRÊT!")
    print("="*70)
    print(f"""
📊 Accédez au dashboard:
   http://localhost:5601/app/kibana#/dashboard/{dashboards[0]['id']}

🔄 Les visualisations pointent maintenant sur:
   → wmdp-responses-2026.03.10

✨ Vous devriez voir les NOUVELLES données (nettoyées)!
""")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
