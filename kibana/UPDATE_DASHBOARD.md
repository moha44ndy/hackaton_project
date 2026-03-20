# 📊 Mise à Jour Dashboard WMDP - Guide Rapide

**Status:** ✅ Données nettoyées et indexées dans Elasticsearch  
**Timestamp:** 10 Mars 2026  
**Indicateurs:** 14+ nouveaux documents chargés

---

## 🎯 Ce Qui S'est Passé

### ✅ Nettoyage Données
- **Avant:** Réponses chargées de newlines (`\n\n\n...`)
- **Réduction:** -65% à -94% par réponse (énorme gain)
- **Fichier nettoyé:** `results/wmdp_responses_cleaned.json`

**Exemples:**
- `wmdp_bio_low_001`: 1410 → 482 chars (-65.8%)
- `wmdp_eng_low_001`: 1068 → 68 chars (-93.6%)

### ✅ Indexation Elasticsearch
```
Index: wmdp-responses-2026.03.10
Documents: 14+
Status: ✅ LIVE
```

### ⏳ Dashboard: À Mettre à Jour
Le dashboard affiche actuellement les **anciens modèles** (fichier JSON statique)  
**Solution:** Reconfigurer pour charger depuis ELK en direct

---

## 🚀 Étapes Rapides (2 min)

### Option 1: Reconfigurer Dashboard Existant

1. **Ouvrir Kibana**
   ```
   http://localhost:5601
   ```

2. **Analytics → Dashboard**
   - Chercher: "WMDP" ou "Evaluation"
   - Cliquer sur le dashboard

3. **Éditer le Dashboard**
   - Bouton **"Edit"** en haut à droite
   - Le dashboard passe en mode édition

4. **Mettre à Jour Chaque Visualisation**
   ```
   Pour chaque graph (pie, bar, etc.):
   
   1. Cliquer sur la visualisation
   2. Bouton "Edit" (ou double-click)
   3. Onglet "Data"
   4. Index pattern dropdown → Sélectionner "wmdp-responses-2026.03.10"
   5. Sauvegarder la visualisation (Cmd+S)
   6. Revenir au dashboard
   ```

5. **Sauvegarder Dashboard**
   - Bouton "Save" en haut
   - Le dashboard affiche maintenant les **NOUVELLES données** ✨

---

### Option 2: Créer Un Nouveau Dashboard (Plus Rapide)

1. **Dashboard → Create New**
2. **Add Visualizations**
   - Cliquer "Create new"
   - Data source: `wmdp-responses-2026.03.10`
   - Choisir type: Bar, Pie, Metric, etc.

**Template Rapide:**
```
Dashboard: "WMDP Evaluation - March 2026"

Visuals:
├── Pie Chart: Distribution by Risk (safe/neutral/unsafe/uncertain)
├── Bar Chart: Response Count by Model
├── Bar Chart: Latency (ms) by Model  
├── Table: Top 20 Responses
└── Metric: Avg Response Length
```

---

## 📊 Données Disponibles

**Index:** `wmdp-responses-2026.03.10`

**Champs:**
- `model_name` - Modèle LLM (distilgpt2-local, etc.)
- `response_text` - **NETTOYÉE** ✨
- `prompt_text` - Prompt original
- `category` - biology/chemistry/engineering/general
- `risk_level` - low/medium/high
- `response_length` - Caractères (nouveau field)
- `latency_ms` - Temps réponse
- `@timestamp` - Date indexation

---

## ⚡ Commandes CLI (Optionnel)

Si vous voulez vérifier directement:

```bash
# Compter documents
curl http://localhost:9200/wmdp-responses-2026.03.10/_count

# Voir un document
curl http://localhost:9200/wmdp-responses-2026.03.10/_search?pretty

# Dernières données
curl "http://localhost:9200/wmdp-responses-2026.03.10/_search?sort=@timestamp:desc&size=5"
```

---

## 🔗 Liens Utiles

| Ressource | URL |
|-----------|-----|
| **Kibana** | http://localhost:5601 |
| **ES API** | http://localhost:9200 |
| **Index Pattern** | wmdp-responses-* |
| **Data** | `results/wmdp_responses_cleaned.json` |

---

## ✅ Checklist Completion

- [x] Données nettoyées
- [x] Indexées dans ELK
- [ ] Index pattern créé (auto ou manuel)
- [ ] Dashboard mis à jour avec nouvelles data
- [ ] Visualisations vérifiées

**Temps estimation:** 2-3 minutes pour mettre à jour

---

## 🐛 Troubleshooting

### Dashboard montre toujours les anciennes données?
→ Assurez-vous qu'il pointe sur `wmdp-responses-2026.03.10` ou `wmdp-responses-*`

### Index ne s'affiche pas?
```bash
# Vérifier l'index existe
curl http://localhost:9200/_cat/indices | grep wmdp
```

### Kibana dit "No data"?
1. Attendre 30 sec pour que ES indexe
2. Rafraîchir la page (Ctrl+R)
3. Vérifier le filtre temporel (top right)

---

**Questions?** Consultez `CODE_CLEANUP_GUIDE.md` ou relancez:
```bash
python kibana/setup_kibana_dynamic.py
```
