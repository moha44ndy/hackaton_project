#!/usr/bin/env python3
"""
Import WMDP Dashboard dans Kibana - Version améliorée
"""

import requests
import json

KIBANA_URL = "http://localhost:5601"
NDJSON_FILE = "wmdp_dashboard_export.ndjson"

print("\n" + "="*70)
print("📥 IMPORT WMDP DASHBOARD DANS KIBANA")
print("="*70)

# Importer
url = f"{KIBANA_URL}/api/saved_objects/_import?overwrite=true"
headers = {"kbn-xsrf": "true"}

print(f"\n🔗 URL: {url}")
print(f"📦 Envoi des objets du fichier...")

try:
    with open(NDJSON_FILE, 'rb') as f:
        files = {'file': f}
        resp = requests.post(url, files=files, headers=headers)
    print(f"\n📊 Status: {resp.status_code}")
    
    if resp.status_code in [200, 201]:
        result = resp.json()
        print(f"✅ SUCCÈS!")
        print(f"   Objects importés: {len(result.get('saved_objects', []))}")
        
        for obj in result.get('saved_objects', []):
            status = "✅" if obj.get('successful') else "⚠️"
            print(f"   {status} {obj['type']:15} | {obj['id']}")
        
        print(f"\n🎯 Ouvre le dashboard:")
        print(f"   {KIBANA_URL}/app/dashboards/view/wmdp-evaluation-dashboard")
    else:
        print(f"❌ Erreur {resp.status_code}:")
        print(resp.text[:500])
        
except Exception as e:
    print(f"❌ Erreur: {e}")

print("\n" + "="*70)
