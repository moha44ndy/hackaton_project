#!/usr/bin/env python3
"""
Script pour importer le dashboard WMDP dans Kibana
Importe: 1 Index Pattern + 3 Visualisations + 1 Dashboard
"""

import requests
import json
import os

KIBANA_URL = "http://localhost:5601"
NDJSON_FILE = "wmdp_dashboard_export.ndjson"

def import_dashboard():
    """Importer le fichier NDJSON dans Kibana"""
    print("=" * 70)
    print("📥 IMPORT DASHBOARD WMDP DANS KIBANA")
    print("=" * 70)
    
    # Vérifier le fichier
    if not os.path.exists(NDJSON_FILE):
        print(f"❌ Fichier non trouvé: {NDJSON_FILE}")
        return False
    
    print(f"✅ Fichier trouvé: {NDJSON_FILE}")
    
    # Lire le fichier
    with open(NDJSON_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"📋 Contenu: {len(lines)} objets Kibana")
    
    # URL d'import
    url = f"{KIBANA_URL}/api/saved_objects/_import"
    headers = {"kbn-xsrf": "true"}
    
    try:
        with open(NDJSON_FILE, 'rb') as f:
            files = {'file': f}
            resp = requests.post(url, files=files, headers=headers)
        
        if resp.status_code in [200, 201]:
            result = resp.json()
            print("\n✅ IMPORT RÉUSSI!")
            print(f"   Objets importés: {result.get('saved_objects', [])}")
            
            # Afficher les URLs
            print("\n🔗 ACCÉS DIRECT:")
            print(f"   Dashboard: {KIBANA_URL}/app/dashboards/view/wmdp-evaluation-dashboard")
            
            return True
        else:
            print(f"\n❌ Erreur HTTP {resp.status_code}:")
            print(resp.text[:500])
            
            # Essayer avec overwrite
            print("\n🔄 Tentative avec overwrite=true...")
            resp = requests.post(url + "?overwrite=true", files={'file': open(NDJSON_FILE, 'rb')}, headers=headers)
            
            if resp.status_code in [200, 201]:
                print("✅ Import avec overwrite réussi!")
                return True
            else:
                print(f"❌ Erreur: {resp.text[:500]}")
                return False
    
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    print("\n🚀 MÉTHODE 1: Import automatique")
    print("-" * 70)
    success = import_dashboard()
    
    if not success:
        print("\n\n🚀 MÉTHODE 2: Import manuel via UI Kibana")
        print("-" * 70)
        print(f"""
1. Aller à: {KIBANA_URL}
2. Menu → Stack Management → Saved Objects
3. Clic "Import"
4. Sélectionner: {NDJSON_FILE}
5. Clic "Import"
6. Accepter les conflits si demandé
7. ✅ Dashboard disponible!

Puis ouvrir:
{KIBANA_URL}/app/dashboards/view/wmdp-evaluation-dashboard
""")

if __name__ == "__main__":
    main()
