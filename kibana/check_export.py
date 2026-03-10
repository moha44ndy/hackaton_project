#!/usr/bin/env python3
import json

print("\n📋 Contenu de wmdp_dashboard_export.ndjson:\n")
print(f"{'TYPE':<20} | {'ID':<30} | {'TITLE'}")
print("-" * 80)

with open('wmdp_dashboard_export.ndjson', 'r') as f:
    for line in f:
        obj = json.loads(line)
        title = obj['attributes'].get('title', 'NO TITLE')
        print(f"{obj['type']:<20} | {obj['id']:<30} | {title}")
