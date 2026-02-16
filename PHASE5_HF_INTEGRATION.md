# 🤖 PHASE 5: HUGGING FACE INTEGRATION COMPLÈTE

## 📋 CHECKLIST D'INTÉGRATION

### Étape 1: Vérifier Configuration HF
- [ ] HF_API_KEY défini dans `.env` (si utilisation API mode)
- [ ] Modèles disponibles localement ou via API
- [ ] Test `hf_client.py` en standalone

### Étape 2: Modifier `prompt_runner.py`
Ajouter support HuggingFace:

```python
from hf_client import get_hf_client

# Dans la fonction main() ou run():
hf_client = get_hf_client(
    model_name="llama-2-7b",  # ou autre modèle
    use_api=False,  # False = local, True = API
    device="cuda"  # ou "cpu"
)

# Pour chaque prompt:
for prompt in prompts:
    response = hf_client.generate_response(
        prompt=prompt.text,
        max_tokens=512,
        temperature=0.7
    )
    # Stocker response pour annotation
```

### Étape 3: Modifier `response_annotator.py`
- [ ] Parser les réponses HF
- [ ] Extraire métadonnées (latency, tokens, etc.)
- [ ] Format compatible ELK logger

### Étape 4: Test Pipeline Complet
```bash
cd hackaton_project
python src/wmdp_pipeline.py --model llama-2 --num-prompts 10
```

Vérifier:
- ✅ Pipeline s'exécute sans erreurs
- ✅ ELK logger enregistre les événements
- ✅ Événements visibles dans Kibana Discover

### Étape 5: Validator Kibana
1. Ouvrir http://localhost:5601/app/dashboards/wmdp-overview-dashboard
2. Les visualisations se mettent à jour avec nouvelles données
3. Tous les graphiques affichent les données en live

---

## 🔗 COORDINATION AVEC TON AMI (HF TEAM)

### Tâches de votre côté:
1. **Test `hf_client.py` en standalone**
   ```bash
   cd src
   python -c "from hf_client import get_hf_client; c = get_hf_client('gpt2'); print(c.generate_response('Hello'))"
   ```

2. **Choix du modèle** (décider avec l'équipe):
   - `llama-2-7b`: bon équilibre, ~7GB RAM
   - `mistral-7b`: plus rapide, ~7GB RAM
   - `gpt2`: très léger, ~500MB RAM (pour tests)

3. **Paramètres de génération**:
   ```python
   {
       "max_tokens": 512,
       "temperature": 0.7,
       "top_p": 0.9,
       "repetition_penalty": 1.2
   }
   ```

4. **Mode API vs Local**:
   - **Local**: Besoin GPU/CPU puissant, plus rapide, gratuit
   - **API**: Besoin HF token, plus lent, fiable

---

## 📊 DONNÉES ATTENDUES DANS KIBANA

Après exécution du pipeline complet avec HF:

### Dans `wmdp-collection-*`:
```json
{
  "timestamp": "2026-02-16T15:30:00Z",
  "model_name": "llama-2-7b",
  "prompt_id": "p1",
  "latency_ms": 2500.5,
  "token_count": 450,
  "status": "success",
  "response_behavior": "safe"
}
```

### Dans `wmdp-annotation-*`:
```json
{
  "timestamp": "2026-02-16T15:30:10Z",
  "response_id": "r1",
  "response_behavior": "safe|unsafe|neutral",
  "compliance_level": 0.95,
  "harmfulness_level": 0.1
}
```

### Dans `wmdp-analysis-*`:
```json
{
  "timestamp": "2026-02-16T15:31:00Z",
  "run_id": "run_20260216_153000",
  "total_responses": 100,
  "avg_latency_ms": 2450.3,
  "models_tested": ["llama-2-7b"],
  "safety_score": 0.92,
  "compliance_rate": 0.95
}
```

---

## 🚀 QUICK START SCRIPT

Pour testing rapide après intégration HF:

```bash
# 1. Se positionner
cd /path/to/hackaton_project

# 2. Vérifier que ES/Kibana sont running
curl http://localhost:9200/_cluster/health

# 3. Lancer le pipeline
python src/wmdp_pipeline.py --model gpt2 --num-prompts 5

# 4. Checker les logs
curl http://localhost:9200/wmdp-collection-*/_search?size=5

# 5. Ouvrir Kibana
open http://localhost:5601/app/dashboards/wmdp-overview-dashboard
```

---

## 🐛 TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| "CUDA not available" | Utiliser `device="cpu"` ou installer PyTorch GPU |
| "Model not found" | Télécharger: `python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('llama-2-7b')"` |
| "Elasticsearch timeout" | Vérifier que ES est running: `docker ps \| grep elasticsearch` |
| "Kibana shows no data" | Vérifier que ELK logger s'initialise sans erreur |
| "Latency très lent" | Normal si CPU: GPU 100x plus rapide |

---

## 📞 COMMUNICATION

**Slack/Discord Format pour ton ami**:

> "Yo, on a l'ELK et Kibana up. Branche HF dans `prompt_runner.py` et teste. Params de base:
> - Model: gpt2 pour test (rapide), sinon llama-2 ou mistral
> - Mode: local (mais besoin GPU/CPU decent)
> - Fais `python src/wmdp_pipeline.py --model gpt2 --num-prompts 5`
> - Depois check Kibana pour voir si les données arrivent"

---

## ✅ SUCCESS CRITERIA

Quand on dit "c'est done":

1. ✅ `python src/wmdp_pipeline.py` s'exécute sans erreur avec HF
2. ✅ Données apparaissent dans `wmdp-collection-*` index
3. ✅ Kibana dashboard se met à jour avec nouvelles données
4. ✅ Latencies, tokens, models affichés correctement
5. ✅ Les 3 visualisations montrent des patterns clairs

---

**ETA**: 1-2 jours (dépend de config HF)

