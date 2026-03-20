#!/usr/bin/env python3
"""Vérifie les champs dans l'index Elasticsearch"""
import requests
import json

ES_HOST = "http://localhost:9200"
INDEX = "wmdp-responses-2026.03.10"

print(f"📋 Vérification index: {INDEX}\n")

# 1. Mapping
print("=" * 60)
print("CHAMPS MAPPÉS (disponibles pour Kibana):")
print("=" * 60)

try:
    r = requests.get(f"{ES_HOST}/{INDEX}/_mapping")
    mapping = r.json()[INDEX]["mappings"]["properties"]
    
    for field_name, field_def in mapping.items():
        field_type = field_def.get("type", "?")
        print(f"  ✓ {field_name:30s} ({field_type})")
    
except Exception as e:
    print(f"❌ Erreur mapping: {e}")

# 2. Documents & Samples
print("\n" + "=" * 60)
print("DONNÉES RÉELLES (sample):")
print("=" * 60)

try:
    r = requests.get(f"{ES_HOST}/{INDEX}/_search?size=1")
    docs = r.json()["hits"]["hits"]
    
    if docs:
        doc = docs[0]["_source"]
        print(f"\nPremier document:")
        for key, value in list(doc.items())[:10]:
            if isinstance(value, str) and len(value) > 50:
                print(f"  {key}: {value[:50]}...")
            else:
                print(f"  {key}: {value}")
    
    count = r.json()["hits"]["total"]["value"]
    print(f"\n📊 Total documents: {count}")
    
except Exception as e:
    print(f"❌ Erreur données: {e}")

# 3. Check specific field
print("\n" + "=" * 60)
print("VÉRIFICATION CHAMP: model_name")
print("=" * 60)

try:
    r = requests.get(f"{ES_HOST}/{INDEX}/_search",
                    json={
                        "size": 100,
                        "query": {"match_all": {}},
                        "aggs": {
                            "models": {
                                "terms": {
                                    "field": "model_name.keyword",
                                    "size": 10
                                }
                            }
                        }
                    })
    
    aggs = r.json()["aggregations"]["models"]["buckets"]
    if aggs:
        print("✓ model_name.keyword EXISTS et a des valeurs:")
        for bucket in aggs:
            print(f"  - {bucket['key']}: {bucket['doc_count']} docs")
    else:
        print("❌ model_name.keyword est VIDE (pas de données)")
        
except Exception as e:
    print(f"⚠️  Erreur aggregation: {e}")

print("\n" + "=" * 60)
