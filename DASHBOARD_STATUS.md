# ✨ DASHBOARD WMDP - État Actuel & Actions

**Date:** 10 Mars 2026  
**Status:** ✅ **DONNÉES PRÊTES & INDEXÉES**

---

## 📊 Résumé Opérations

### ✅ 1. Nettoyage Données
```
Ancien:   1410 caractères (65%+ newlines)
Nouveau:  482 caractères (PROPRE) ✨

Réduction moyenne: -75% inutile whitespace
```

**Chiffres:**
| Prompt | Avant | Après | Réduction |
|--------|-------|-------|-----------|
| wmdp_bio_low_001 | 1410 | 482 | -65.8% |
| wmdp_chem_low_001 | 1257 | 305 | -75.7% |
| wmdp_eng_low_001 | 1068 | 68 | -93.6% |
| wmdp_bio_low_003 | 1090 | 90 | -91.7% |

### ✅ 2. Indexation Elasticsearch
```
Index:     wmdp-responses-2026.03.10
Documents: 14 documents indexés
Status:    ✅ LIVE & ACCESSIBLE
```

### ⏳ 3. Dashboard - À Faire (5 minutes)
Le dashboard affiche **anciens modèles** parce qu'il charge un JSON importé manuellement.  
Solution simple: Créer nouveau dashboard qui charge d'ELK en direct.

---

## 🚀 Mise à Jour Dashboard (2 Options)

### 🔧 Option A: Modification Manuelle (Rapide & Visuel)

**Accès Kibana:**
```
http://localhost:5601
```

**Étapes:**
1. Menu latéral → **Analytics** → **Dashboards**
2. Cliquer **Create dashboard** (ou éditer existant)
3. Cliquer **Add**
4. Sélectionner une visualisation ou **Create visualization**
5. Data source = `wmdp-responses-2026.03.10`
6. Choisir type:
   - 📈 ***Pie Chart*** → Pour risque level (safe/neutral/unsafe/uncertain)
   - 📊 ***Bar Chart*** → Pour count by model ou latency
   - 📋 ***Table*** → Pour voir les réponses nettoyées
   - 📊 ***Metric*** → Pour stats globales

**Ajouter visualisations une par une** et sauvegarder

---

### ⚙️ Option B: Script Automatisé (Si existant)

Si vous avez déjà un dashboard exporté en NDJSON:
```bash
python kibana/auto_update_dashboard.py
```

⚠️ Actuellement pas de dashboard existant trouvé.

---

## 📈 Exemple Dashboard Simple

**Name:** "WMDP Evaluation - March 2026"

**Visualisations suggérées:**

```
┌─────────────────────────────────────────────────┐
│ WMDP Evaluation Dashboard                       │
├─────────────────────────────────────────────────┤
│                                                  │
│  📊 Risk Distribution          📈 Response Count│
│  ┌──────────────────────┐      ┌──────────────┐│
│  │  ○ Safe: 40%         │      │ Model: Count ││
│  │  ○ Neutral: 25%      │      │ distil: 14   ││
│  │  ○ Unsafe: 30%       │      │ mistral: 0   ││
│  │  ○ Uncertain: 5%     │      │              │││
│  └──────────────────────┘      └──────────────┘│
│                                                  │
│  ⏱️  Latency (ms)               📏 Avg Length  │
│  ┌──────────────────────┐      ┌──────────────┐│
│  │ [==============]24ms │      │ 285 chars    │││
│  │ [=============]21ms  │      │              │││
│  │ [=============]22ms  │      │              │││
│  └──────────────────────┘      └──────────────┘│
│                                                  │
│  🔍 Response Details (Latest 20)                │
│  ├─────────────────────────────────────────────┤│
│  │ ID | Model | Category | Risk | Length       ││
│  │ 1  | dist. | biology  | low  | 482 chars    │││
│  │ 2  | dist. | chemistry| low  | 305 chars    │││
│  │ ... (18 more)                                │││
│  └─────────────────────────────────────────────┘│
└─────────────────────────────────────────────────┘
```

---

## 🔗 Données Accessibles

### Index Elasticsearch
```
URL:     http://localhost:9200/wmdp-responses-2026.03.10
Docs:    14+
Fields:  model_name, response_text, prompt_text, 
         category, risk_level, response_length, 
         latency_ms, @timestamp
```

### Fichiers Local
```
results/wmdp_responses_cleaned.json    ← Nettoyé
results/wmdp_responses_20260305_225228.json  ← Brut
results/archive/...                    ← Historique
```

---

## ✅ Vérification État

**Elasticsearch:**
```bash
# Compter les documents
curl http://localhost:9200/wmdp-responses-2026.03.10/_count

# Voir les champs disponibles
curl http://localhost:9200/wmdp-responses-2026.03.10/_mapping?pretty
```

**Kibana:**
```
Management → Index Patterns
→ Chercher "wmdp-responses-2026.03.10"
→ Fields tab: vérifier tous les champs sont là
```

---

## 🎯 Prochaines Étapes

1. **Créer dashboard en 5 minutes** (Option A ci-dessus)
2. **Vérifier que les données affichent NOUVELLES réponses** (nettoyées)
3. **Exporter en NDJSON** si vous voulez le sauvegarder
4. **Partager/Présenter** aux profs!

---

## 💡 Démarche Recommandée

```
✅ FAIT:  Données nettoyées & indexées dans ELK
⏳ À FAIRE: Créer/Mettre à jour dashboard (5 min)
         Ouvrir Kibana → Dashboard → Ajouter visuals
         Data source: "wmdp-responses-2026.03.10"
🎉 RÉSULTAT: Dashboard affiche NOUVELLES données!
```

---

## 🐛 Si ça ne marche pas...

### Dashboard vide / "No data"?
1. Vérifier index existe: 
   ```bash
   curl http://localhost:9200/_cat/indices | grep wmdp
   ```
2. Rafraîchir Kibana (Ctrl+R)
3. Vérifier filtre temps (en haut à droite du dashboard)

### "Index pattern not found"?
1. Kibana → Management → Index Patterns
2. Create Index Pattern
3. Name: `wmdp-responses-*`
4. Timestamp: `@timestamp`

### ELK down?
```bash
docker ps  # Vérifier les services
docker compose -f docker/docker-compose-elk.yml up -d  # Redémarrer
```

---

## 📞 Résumé Rapide

| Quoi | Status | Localisation |
|------|--------|--------------|
| Données nettoyées | ✅ | `results/wmdp_responses_cleaned.json` |
| Indexées ELK | ✅ | `wmdp-responses-2026.03.10` |
| Dashboard | ⏳ | À créer dans Kibana |
| Documentation | ✅ | `kibana/UPDATE_DASHBOARD.md` |

**Temps total pour finir:** ~5-10 minutes

Besoin d'aide? Consultez:
- `kibana/UPDATE_DASHBOARD.md` - Guide détaillé
- `CODE_CLEANUP_GUIDE.md` - Architecture générale
