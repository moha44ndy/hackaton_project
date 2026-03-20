# Résultats WMDP - Architecture Stockage

## 📁 Structure

```
results/
├── wmdp_responses_[DATE].json      ← Réponses LLM actuelles
├── WMDP_Report.json                ← Rapport d'analyse final
├── annotations/                    ← Annotations WMDP par modèle
│   └── [model_name]/
│       └── annotations_[DATE].json
└── archive/                        ← Résultats historiques (>7 jours)
    ├── wmdp_responses_*.json
    ├── analysis_*.json
    └── OLD_RUNS/
```

## 📊 Fichiers Actuels

- **wmdp_responses_20260305_225228.json** (57 KB)
  - Dernière exécution du test des modèles locaux
  - Contient réponses brutes + métadonnées
  
- **WMDP_Report.json** (5.6 KB)
  - Rapport final d'analyse

- **archive/** 
  - Tous les résultats historiques
  - Utilisés pour comparaison/historique uniquement

## 🔄 Pipeline Stockage

1. **Exécution** → `prompt_runner.py`
   - Charge dataset (`data/wmdp_prompts.json`)
   - Lance modèles LLM
   
2. **Résultats bruts** → `results/wmdp_responses_[DATE].json`
   - Sauvegarde immédiate

3. **Annotation** → `response_annotator.py`
   - Analyse sécurité WMDP

4. **Archivage auto** (>7 jours)
   - Les fichiers anciens → `archive/`

## 💡 Dans la Pipeline

- Elasticsearch: Tous les events logging
- PostgreSQL: Annotations structurées
- Redis: Cache résultats temps réel
- Fichiers JSON: Sauvegarde persistante

## 🧹 Nettoyage Récent

- ✅ 8 fichiers historiques archivés
- ✅ Scripts obsolètes supprimés
- ✅ Structure simplifiée et claire
