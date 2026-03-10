#!/usr/bin/env python3
"""
Créer l'index pattern wmdp-* dans Kibana
"""

import requests
import json

KIBANA_URL = "http://localhost:5601"

print("\n" + "="*70)
print("📝 CRÉER INDEX PATTERN wmdp-* DANS KIBANA")
print("="*70)

# Créer l'index pattern
url = f"{KIBANA_URL}/api/saved_objects/index-pattern/wmdp-*"
headers = {"kbn-xsrf": "true"}
data = {
    "attributes": {
        "title": "wmdp-*",
        "timeFieldName": "@timestamp"
    }
}

print(f"\n🔗 URL: {url}")

try:
    # Essayer PUT (créer/mettre à jour)
    resp = requests.put(url, json=data, headers=headers)
    
    if resp.status_code in [200, 201]:
        print(f"✅ Index pattern créé/mis à jour!")
        result = resp.json()
        print(f"   ID: {result.get('id')}")
        print(f"   Title: {result['attributes'].get('title')}")
    else:
        print(f"⚠️  Status:{resp.status_code}")
        print(resp.text[:300])
        
except Exception as e:
    print(f"❌ Erreur: {e}")

print("\n" + "="*70)
