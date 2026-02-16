# 🚀 ELK INFRASTRUCTURE SETUP GUIDE

**Status**: Ready to Deploy  
**Date**: 2026-02-15  

---

## 📋 Prérequis

- Docker & Docker-Compose installés
- Port 9200 (Elasticsearch), 5601 (Kibana), 5432 (PostgreSQL), 6379 (Redis) disponibles
- 4GB RAM minimum

---

## 🚀 LANCEMENT RAPIDE

### Étape 1: Marrer l'infrastructure ELK

```bash
# Terminal 1: Infrastructure (ELK + PostgreSQL + Redis)
cd hackaton_project
docker-compose -f docker/docker-compose-elk.yml up -d

# Attendre que tout soit prêt (~30s)
sleep 30

# Vérifier la santé du cluster
curl http://localhost:9200/_cluster/health
```

**Résultat attendu**:
```json
{
  "cluster_name": "docker-cluster",
  "status": "green",
  "timed_out": false,
  "number_of_nodes": 1,
  "number_of_data_nodes": 1,
  "active_primary_shards": 0,
  "active_shards": 0
}
```

### Étape 2: Modifier le pipeline pour utiliser ELK

Les fichiers suivants sont **prêts à l'emploi**:
- ✅ `src/elk_logger.py` - Logger centralisé
- ✅ `src/elk_setup.py` - Initialisation des indices
- ✅ `src/hf_client.py` - Client Hugging Face
- ✅ `docker/docker-compose-elk.yml` - Infrastructure

### Étape 3: Initialiser les indices Elasticsearch

```bash
python src/elk_setup.py
```

**Résultat attendu**:
```
✅ Created index template: wmdp-template
✅ Created index: wmdp-collection-2026.02.15
✅ Created index: wmdp-annotation-2026.02.15
✅ Created index: wmdp-analysis-2026.02.15
```

### Étape 4: Accéder à Kibana

Ouvrir dans le navigateur:
```
http://localhost:5601
```

**Première visite**:
1. Cliquer "Explore independently"
2. Créer index pattern: `wmdp-*`
3. Time field: `@timestamp`

---

## 🔧 MODIFICATION DU PIPELINE (Intégration)

Pour intégrer ELK au pipeline existant, modifier `src/wmdp_pipeline.py`:

```python
# Ajouter au début
from elk_logger import get_elk_logger
from datetime import datetime

# Dans main():
elk_logger = get_elk_logger(es_host="elasticsearch:9200")

# Phase 1 - Collection
for response in responses:
    elk_logger.log_collection_event({
        "timestamp": datetime.now().isoformat(),
        "model_name": model_name,
        "prompt_id": response.prompt_id,
        "latency_ms": response.latency,
        "token_count": response.token_count,
        "status": "success"
    })

# Phase 2 - Annotation
for annotation in annotations:
    elk_logger.log_annotation_event({
        "timestamp": datetime.now().isoformat(),
        "response_id": annotation.id,
        "response_behavior": annotation.behavior,
        "compliance_level": annotation.compliance,
        "harmfulness_level": annotation.harmfulness,
    })

# Phase 3 - Analysis
elk_logger.log_analysis_event({
    "timestamp": datetime.now().isoformat(),
    "run_id": run_id,
    "total_responses": len(responses),
    "avg_latency_ms": avg_latency,
    "models_tested": models,
    "safety_score": safety_score,
    "compliance_rate": compliance_rate,
})
```

---

## 📊 ACCÉDER AUX DONNÉES

### Via API Elasticsearch

```bash
# Lister tous les indices
curl http://localhost:9200/_cat/indices

# Chercher les événements de collection
curl -X POST http://localhost:9200/wmdp-collection-*/_search -H "Content-Type: application/json" -d '{
  "query": {
    "match_all": {}
  },
  "size": 10
}'

# Statistiques par modèle
curl -X POST http://localhost:9200/wmdp-collection-*/_search -H "Content-Type: application/json" -d '{
  "aggs": {
    "models": {
      "terms": {
        "field": "model_name",
        "size": 10
      }
    }
  }
}'
```

### Via Python

```python
from elk_logger import get_elk_logger

logger = get_elk_logger(es_host="localhost:9200")

# Récupérer statistiques
stats = logger.get_stats(days_back=7)
print(stats)

# Chercher événements
events = logger.query_events(event_type="collection", limit=100)
for event in events:
    print(event)
```

---

## 🤖 INTÉGRER HUGGING FACE

Les modèles HF sont **prêts à être utilisés**.

### Utiliser un modèle Llama localement

```python
from hf_client import get_hf_client

# Modèle local
client = get_hf_client(
    model_name="llama-2-7b",
    use_api=False,
    device="cuda"  # ou "cpu"
)

response = client.generate_response(
    prompt="What is machine learning?",
    max_tokens=512,
    temperature=0.7
)
print(response)

# Info du modèle
info = client.get_model_info()
print(info)
```

### Via HF Inference API (Cloud)

```python
import os

client = get_hf_client(
    model_name="llama-2-7b",
    api_key=os.getenv("HF_API_KEY"),
    use_api=True  # Utiliser l'API
)

response = client.generate_response(prompt="Your prompt here")
```

---

## 🛠️ UTILITAIRES

### Vérifier la santé ELK

```bash
# Terminal
python -c "from elk_logger import get_elk_logger; logger = get_elk_logger(); print(logger.health_check())"
```

### Voir les statistiques

```python
from elk_logger import get_elk_logger

logger = get_elk_logger()
stats = logger.get_stats()

print(f"Total Collections: {stats['total_collections']}")
print(f"Avg Latency: {stats['avg_latency_ms']:.2f}ms")
print(f"Models: {stats['models_used']}")
print(f"Errors: {stats['error_count']}")
```

### Nettoyer les données

```bash
# Supprimer tous les indices WMDP
curl -X DELETE http://localhost:9200/wmdp-*

# Supprimer les données PostgreSQL
docker exec wmdp-postgres psql -U wmdp_user -d wmdp_annotations -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
```

---

## 📈 DASHBOARDS KIBANA

### Créer un Dashboard Simple

1. **Add Visualization** → Line Chart
   - Index: `wmdp-collection-*`
   - Metrics: Average of `latency_ms`
   - Buckets: Date histogram of `timestamp`
   - Interval: 5 minutes

2. **Add Visualization** → Pie Chart
   - Index: `wmdp-collection-*`
   - Metrics: Count
   - Buckets: Terms of `model_name`

3. **Save as Dashboard**

---

## 🐛 TROUBLESHOOTING

### Elasticsearch ne démarre pas

```bash
# Vérifier les logs
docker logs wmdp-elasticsearch

# Problème commun: Manque de mémoire
# Solution: Augmenter SWAP ou réduire heap size dans docker-compose-elk.yml
```

### Kibana ne se connecte pas à ES

```bash
# Vérifier la URL
http://localhost:5601/

# Vérifier ES health
curl http://localhost:9200/_cluster/health

# Redémarrer Kibana
docker restart wmdp-kibana
```

### Les logs ne s'affichent pas

```python
# Vérifier que ELKLogger est bien initié
from elk_logger import get_elk_logger
logger = get_elk_logger()

# Tester un log
logger.log_collection_event({
    "timestamp": "2026-02-15T10:00:00Z",
    "model_name": "test",
    "status": "success"
})

# Vérifier dans Kibana
# Aller à Discover > Sélectionner wmdp-* > Chercher "model_name: test"
```

---

## ✅ CHECKLIST DÉPLOIEMENT

- [ ] Docker-compose lancé avec `up -d`
- [ ] Elasticsearch healthy (green status)
- [ ] Kibana accessible sur port 5601
- [ ] Indices créés avec `elk_setup.py`
- [ ] Pipeline modifié avec intégration ELK
- [ ] Au moins 1 run exécuté pour confirmer les logs
- [ ] Dashboard créé dans Kibana
- [ ] PostgreSQL accessible sur port 5432
- [ ] Redis accessible sur port 6379

---

## 📚 RESSOURCES

- 📖 [Elasticsearch Docs](https://www.elastic.co/guide/en/elasticsearch/reference/8.5/index.html)
- 📖 [Kibana Docs](https://www.elastic.co/guide/en/kibana/8.5/index.html)
- 📖 [Transformers Docs](https://huggingface.co/docs/transformers)
- 📖 [HF Inference API](https://huggingface.co/docs/hub/guides/inference)

---

**Status**: ✅ Ready to Deploy  
**Next**: Execute Phase 1, monitor in Kibana, optimize 🚀
