# Architecture Code - Guide Nettoyage ✨

## 📋 État Actuel (Avant Nettoyage)

### ✅ Fichiers Actifs (Pipeline Principale)

**src/wmdp_pipeline.py** (523 lignes)
- ➜ Entry point principal
- Import: `llm_clients.MODEL_CONFIGS`, `prompt_runner`, `response_annotator`, `wmdp_analyzer`

**src/prompt_runner.py**
- ➜ Lance modèles LLM + récupère réponses
- Import: `llm_clients.LLMClientFactory`

**src/llm_clients.py** (591 lignes) 
- ➜ Clients LLM (Mistral, GPT, Claude, TransformersClient local)
- ⚠️  TransformersClient = client local pour modèles transformers

**src/response_annotator.py**
- ➜ Annotation automatique réponses WMDP

**src/wmdp_analyzer.py**
- ➜ Analyse statistique, rapport final

**src/elk_logger.py**
- ➜ Logging ELK, indexation Elasticsearch

**src/elk_setup.py**
- ➜ Setup indices ELK au démarrage

### ⚠️  Fichiers Redondants

**src/hf_client.py** (350 lignes)
- ❌ HuggingFaceLocalClient = quasi identique à TransformersClient
- ❌ Utilisé uniquement par scripts de test (`simple_hf_test.py`, `diagnostic_test.py`)
- 💡 **Action**: Supprimer + migrer tests vers `llm_clients.TransformersClient`

### 🗑️ Supprimés Récemment

- ✅ `diagnostic.py` - script de vérification obsolète
- ✅ `test_openai_api.py` - test API OpenAI abandonné

---

## 🎯 Recommandations Nettoyage

### Phase 1: Consolidation (FACILE)
```python
# Option 1: Supprimer hf_client.py
# - Remplacer imports dans tests:
#   from hf_client import HuggingFaceLocalClient
#   ➜ from llm_clients import TransformersClient as HuggingFaceLocalClient

# Option 2: Fusionner intelligemment
# - Garder hf_client.py comme "alias" léger
# - Point vers llm_clients.TransformersClient
```

### Phase 2: Code Cleanup (MOYEN)
```python
# Supprimer imports/code inutilisé:
- Mistral API client (mlx_chat_client.send_message_llm)
- GPT client (dépendance deprecated openai)
- Claude via API (très cher, pas used)
- Garder uniquement: TransformersClient + HF API (fallback)
```

### Phase 3: Structure Résultats (FAIT)
```ini
✅ Archive anciens fichiers
✅ Garder présent: wmdp_responses_[DATE].json + rapport
✅ ELK stocke tout (no local files needed)
```

---

## 🏗️ Nouvelle Structure Proposée (Futur)

```
src/
├── __init__.py          ← Package init
├── wmdp_pipeline.py     ← Main entry (pas de changement)
├── prompt_runner.py     ← Orchestration (pas de changement)
├── response_annotator.py    ← Annotations (pas de changement)
├── wmdp_analyzer.py     ← Analyse (pas de changement)
├── elk_logger.py        ← ELK logging (pas de changement)
├── elk_setup.py         ← Setup ELK (pas de changement)
├── llm_clients.py       ← Clients (NETTOYER: supprimer Mistral/GPT/Claude)
└── [hf_client.py → SUPPRIMER]

Résumé:
- 5 fichiers core stables
- 1 fichier clients (à simplifier)
- 0 redondance (après suppression hf_client)
```

---

## 📊 Recommandation Finale

**Pour maintenant :**
1. ✅ Archivage résultats ancien → **FAIT**
2. ✅ Suppression scripts test obsolètes → **FAIT**
3. ⏳ Supprimer hf_client.py (facile, gain minuscule)
4. ⏳ Simplifier llm_clients.py (plus tôt ou tard)

**Impact:**
- Gain: -1 fichier redondant, -350 lignes code inutile
- Perte: Zéro (tout est dans llm_clients.py déjà)
- Risque: Très faible (bien documenté)

