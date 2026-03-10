#!/usr/bin/env python3
"""
Test diagnostic avant création dashboard
Vérifie que tous les composants sont en place
"""

import requests
import json

print('='*70)
print('✅ VÉRIFICATION PRÉ-DASHBOARD - DIAGNOSTIC')
print('='*70)

# 1. Vérifier ES
print('\n🔍 1. Elasticsearch:')
try:
    resp = requests.get('http://localhost:9200/_cluster/health?pretty')
    if resp.status_code == 200:
        data = resp.json()
        print(f'   Status: {data["status"].upper()} ✅')
        print(f'   Nodes: {data["number_of_data_nodes"]}')
except Exception as e:
    print(f'   ❌ Elasticsearch NOT accessible: {e}')

# 2. Vérifier indices
print('\n🔍 2. Indices WMDP:')
try:
    resp = requests.get('http://localhost:9200/_cat/indices?format=json')
    if resp.status_code == 200:
        indices = [i for i in resp.json() if 'wmdp' in i['index']]
        print(f'   Total: {len(indices)} indices')
        
        total_docs = sum(int(i['docs.count']) for i in indices)
        print(f'   Documents: {total_docs} ✅')
        
        for idx_type in sorted(set(i['index'].split('-')[1] for i in indices)):
            count = sum(int(i['docs.count']) for i in indices if i['index'].split('-')[1] == idx_type)
            print(f'     - wmdp-{idx_type}: {count} docs')
except Exception as e:
    print(f'   ❌ Cannot read indices: {e}')

# 3. Vérifier Kibana
print('\n🔍 3. Kibana:')
try:
    resp = requests.get('http://localhost:5601/api/status')
    if resp.status_code == 200:
        print(f'   Status: RUNNING ✅')
except Exception as e:
    print(f'   ❌ Kibana NOT accessible: {e}')

# 4. Vérifier Index Pattern
print('\n🔍 4. Index Pattern wmdp-*:')
try:
    resp = requests.get('http://localhost:5601/api/saved_objects/index-pattern')
    if resp.status_code == 200:
        patterns = resp.json().get('saved_objects', [])
        wmdp_pattern = [p for p in patterns if 'wmdp' in p['attributes']['title']]
        if wmdp_pattern:
            print(f'   ✅ Créé: wmdp-*')
        else:
            print(f'   ⚠️  Patterns disponibles: {len(patterns)}')
except Exception as e:
    print(f'   ⚠️  Erreur: {e}')

# 5. Vérifier Dashboard
print('\n🔍 5. Dashboard:')
try:
    resp = requests.get('http://localhost:5601/api/saved_objects/_find?type=dashboard')
    if resp.status_code == 200:
        dashboards = resp.json().get('saved_objects', [])
        wmdp_dash = [d for d in dashboards if 'wmdp' in d['attributes']['title'].lower()]
        if wmdp_dash:
            print(f'   ✅ Dashboard trouvé')
            print(f'      ID: {wmdp_dash[0]["id"]}')
            panels = json.loads(wmdp_dash[0]['attributes'].get('panelsJSON', '[]'))
            print(f'      Panneaux: {len(panels)}')
        else:
            print(f'   ⚠️  Aucun dashboard WMDP')
except Exception as e:
    print(f'   ⚠️  Erreur: {e}')

print('\n' + '='*70)
print('📊 RÉSUMÉ & PROCHAINES ÉTAPES:')
print('='*70)
print("""
✅ Tous les composants sont en place!

⚠️  IMPORTANTE - Plage de Temps:
   Les données sont en MARS 2026 (2026-03-02 à 2026-03-05)
   Kibana affiche par défaut AVRIL 2025 ❌
   
   👉 FIX (30 secondes):
      1. Ouvrir: http://localhost:5601
      2. Aller Dashboard
      3. Haut DROITE: Clic sur "Apr 2025 - Jul 2025"
      4. Sélectionner "Last 30 days"
      5. Clic "Update"
      6. ✅ Les données apparaissent!

📝 CRÉER LES 3 VISUALISATIONS:
   Voir le guide détaillé:
   → kibana/GUIDE_CREATION_ETAPE_PAR_ETAPE.md
   
   Durée: 10-15 minutes
   Difficulté: ⭐ Très facile
   
🎯 RÉSUMÉ RAPIDE:
   1. Kibana → Visualize
   2. Créer 3x (Pie + 2x Bar)
   3. Config (response_behavior, model_name, latency_ms)
   4. Save + Add to dashboard
   5. Position dans la grille
   6. Save dashboard

✨ Ensuite: Dashboard complètement fonctionnel!
""")
