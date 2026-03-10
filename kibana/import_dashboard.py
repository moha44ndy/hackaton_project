#!/usr/bin/env python3
"""
Import Kibana dashboard from NDJSON file via API
"""
import requests
import json
import sys

KIBANA_URL = "http://localhost:5601"
NDJSON_FILE = "kibana_dashboards_export.ndjson"

def import_dashboard():
    """Import saved objects from NDJSON file"""
    try:
        print(f"📖 Reading {NDJSON_FILE}...")
        with open(NDJSON_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✅ File read: {len(content)} bytes")
        
        url = f"{KIBANA_URL}/api/saved_objects/_import?overwrite=true"
        headers = {
            "kbn-xsrf": "true",
            "Content-Type": "application/x-ndjson"
        }
        
        print(f"🚀 Posting to {url}...")
        response = requests.post(url, headers=headers, data=content, timeout=30)
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f"✅ SUCCESS!")
            print(f"   Imported objects:")
            if "saved_objects" in result:
                for obj in result["saved_objects"]:
                    print(f"   - {obj.get('type')}: {obj.get('attributes', {}).get('title', obj.get('id'))}")
            print(f"\n🎉 Dashboard available at: {KIBANA_URL}/app/dashboards/wmdp-overview-dashboard")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return False
            
    except FileNotFoundError:
        print(f"❌ File not found: {NDJSON_FILE}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = import_dashboard()
    sys.exit(0 if success else 1)
