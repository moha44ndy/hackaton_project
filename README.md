# 🔬 Projet WMDP - Évaluation Éthique des LLMs

> **Évaluation de la conformité éthique et sécuritaire des modèles de langage à l'aide du benchmark WMDP (Weapons of Mass Destruction Proxy)**

## 📋 Description

Ce projet de recherche vise à évaluer la robustesse éthique et sécuritaire de différents modèles de langage (GPT-4, Claude, Mistral, Llama) face à des requêtes potentiellement dangereuses, en utilisant le benchmark WMDP.

### Objectifs

1. ✅ Analyser les stratégies de refus des LLMs
2. ✅ Comparer les comportements inter-modèles
3. ✅ Développer une grille d'analyse multicritère
4. ✅ Proposer des recommandations pour améliorer la sûreté

## 🚀 Démarrage Rapide

### Prérequis

- Docker & Docker Compose
- Clés API: Mistral, OpenAI, Anthropic
- Python 3.11+ (si utilisation locale)

### Installation

1. **Cloner le projet**
   ```bash
   git clone [votre-repo]
   cd wmdp-project
   ```

2. **Configurer les clés API**
   ```bash
   cp .env.example .env
   # Éditer .env avec vos clés API
   ```

3. **Construire l'environnement Docker**
   ```bash
   cd docker
   docker compose build
   ```

4. **Tester l'installation**
   ```bash
   docker compose run --rm wmdp-test python /app/diagnostic.py
   ```

## 🔧 Correction du Bug Mistral

### ❌ Erreur Actuelle
```
ModuleNotFoundError: No module named 'mistralai.models.chat_completion'
```

### ✅ Solution

Remplacez dans votre code:

```python
# ❌ ANCIEN (ne fonctionne plus)
from mistralai.models.chat_completion import ChatMessage

# ✅ NOUVEAU
from mistralai import Mistral

client = Mistral(api_key="votre_clé")
response = client.chat.complete(
    model="mistral-small-latest",
    messages=[{"role": "user", "content": "votre message"}]
)
```

**Voir le guide complet**: [GUIDE_DEMARRAGE.md](GUIDE_DEMARRAGE.md)

## 📁 Structure du Projet

```
wmdp-project/
├── 📄 README.md                    # Ce fichier
├── 📄 GUIDE_DEMARRAGE.md          # Guide de démarrage détaillé
├── 📄 METHODOLOGIE_WMDP.md        # Méthodologie de recherche
│
├── 🐳 docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .env                       # Vos clés API (à créer)
│
├── 🧪 src/
│   ├── wmdp_evaluator.py         # Module principal d'évaluation
│   ├── llm_clients.py            # Clients API (GPT, Claude, Mistral)
│   ├── run_wmdp_evaluation.py    # Script d'exécution
│   ├── diagnostic.py             # Vérification environnement
│   └── test_mistral_api_corrected.py  # Test API Mistral
│
├── 📊 data/
│   └── wmdp_prompts.json         # Prompts WMDP (à ajouter)
│
├── 📈 results/                    # Résultats d'évaluation
│
├── 📓 notebooks/                  # Jupyter notebooks pour analyses
│
└── 📝 requirements.txt            # Dépendances Python
```

## 🎯 Utilisation

### 1. Vérifier l'environnement

```bash
docker compose run --rm wmdp-test python /app/diagnostic.py
```

### 2. Tester l'API Mistral

```bash
docker compose run --rm wmdp-test python /app/test_mistral_api_corrected.py
```

### 3. Lancer une évaluation

```bash
# Évaluer un seul modèle
docker compose run --rm wmdp-test python /app/run_wmdp_evaluation.py --models mistral-small

# Évaluer plusieurs modèles
docker compose run --rm wmdp-test python /app/run_wmdp_evaluation.py \
  --models gpt-4 claude-3-sonnet mistral-medium \
  --num-prompts 10 \
  --save-individual
```

### 4. Analyser les résultats (Jupyter)

```bash
docker compose up jupyter
# Aller sur http://localhost:8888
```

## 📊 Exemple de Code

### Évaluation Simple

```python
from wmdp_evaluator import WMDPEvaluator, RiskLevel
from llm_clients import LLMClientFactory

# Initialiser
evaluator = WMDPEvaluator()
client = LLMClientFactory.create_client("mistral")

# Tester un prompt
prompt = "What are safety principles in chemistry labs?"
response, metadata = client.generate(prompt)

# Évaluer
result = evaluator.evaluate_response(
    model_name="mistral-small",
    prompt=prompt,
    response=response,
    risk_level=RiskLevel.LOW,
    category="chemistry"
)

# Générer rapport
report = evaluator.generate_report()
print(report)
```

## 📈 Métriques Évaluées

- **Taux de refus**: % de refus face aux prompts à risque
- **Qualité du refus**: Score 1-5 basé sur clarté, justification, empathie
- **Taux de compliance**: % de réponses problématiques
- **Présence de justification**: % avec explication éthique
- **Détection d'hallucinations**: % de fausses informations
- **Dommages implicites**: % de réponses indirectement dangereuses

## 🧪 Méthodologie

Le projet suit une approche en 3 phases:

### Phase 1: Préparation
- Sélection des modèles
- Chargement dataset WMDP
- Configuration prompts de test

### Phase 2: Évaluation
- Génération des réponses
- Classification des comportements
- Annotation multicritère

### Phase 3: Analyse
- Statistiques quantitatives
- Analyse qualitative
- Visualisations comparatives
- Rédaction rapport scientifique

**Voir détails**: [METHODOLOGIE_WMDP.md](METHODOLOGIE_WMDP.md)

## 🔍 Modèles Supportés

| Modèle | Fournisseur | Status |
|--------|-------------|--------|
| GPT-4 | OpenAI | ✅ |
| GPT-3.5 | OpenAI | ✅ |
| Claude 3 Opus | Anthropic | ✅ |
| Claude 3 Sonnet | Anthropic | ✅ |
| Mistral Small | Mistral AI | ✅ |
| Mistral Medium | Mistral AI | ✅ |
| Llama 3 8B | Hugging Face | ✅ |
| Zephyr 7B | Hugging Face | ✅ |
| Mistral 7B Instruct | Hugging Face | ✅ |

## 📚 Ressources

### Documentation
- [Guide de Démarrage](GUIDE_DEMARRAGE.md) - Installation et correction bugs
- [Méthodologie WMDP](METHODOLOGIE_WMDP.md) - Guide de recherche complet

### Références Académiques
- **Paper WMDP**: [arXiv:2403.03218](https://arxiv.org/abs/2403.03218)
- **GitHub WMDP**: [centerforaisafety/wmdp](https://github.com/centerforaisafety/wmdp)

### APIs
- [Mistral AI](https://docs.mistral.ai/)
- [OpenAI](https://platform.openai.com/docs)
- [Anthropic](https://docs.anthropic.com/)

## 🛠️ Commandes Utiles

```bash
# Diagnostic complet
docker compose run --rm wmdp-test python /app/diagnostic.py

# Test API
docker compose run --rm wmdp-test python /app/test_mistral_api_corrected.py

# Évaluation complète
docker compose run --rm wmdp-test python /app/run_wmdp_evaluation.py --help

# Shell interactif
docker compose run --rm wmdp-test /bin/bash

# Jupyter notebook
docker compose up jupyter

# Voir les logs
docker compose logs -f

# Nettoyer
docker compose down -v
```

## 🤝 Contribution

### Structure du Code

- `wmdp_evaluator.py`: Logique d'évaluation principale
- `llm_clients.py`: Abstraction des APIs
- `run_wmdp_evaluation.py`: Script d'orchestration
- `diagnostic.py`: Vérification environnement

### Ajouter un Nouveau Modèle

1. Créer une classe dans `llm_clients.py`:
```python
class NouveauClient(LLMClient):
    def generate(self, prompt, **kwargs):
        # Implémentation
        pass
```

2. Ajouter dans `MODEL_CONFIGS`:
```python
"nouveau-modele": {
    "provider": "nouveau",
    "model": "modele-v1",
    "max_tokens": 4096
}
```

## ⚠️ Considérations Éthiques

### ✅ Bonnes Pratiques

- Utiliser uniquement le dataset WMDP officiel
- Ne pas créer de vrais prompts dangereux
- Anonymiser les données sensibles
- Documenter méthodologie transparente

### ❌ À Éviter

- Générer réelles instructions dangereuses
- Publier prompts adversaires efficaces
- Tester sans supervision appropriée

## 📝 Livrables du Projet

1. ✅ Code source (ce repository)
2. 📊 Résultats d'évaluation (JSON)
3. 📈 Visualisations comparatives
4. 📄 Rapport scientifique complet
5. 📓 Notebooks d'analyse

## 🐛 Dépannage

### Problème: Erreur Mistral API

**Solution**: Voir [GUIDE_DEMARRAGE.md](GUIDE_DEMARRAGE.md) section "Solution"

### Problème: Clés API invalides

```bash
# Vérifier variables d'environnement
docker compose run --rm wmdp-test env | grep API_KEY
```

### Problème: Erreur Docker

```bash
# Reconstruire l'image
docker compose build --no-cache

# Nettoyer et redémarrer
docker compose down -v
docker compose up --build
```

## 📧 Contact

Pour questions ou suggestions sur le projet:
- Issues GitHub
- Email: [votre-email]

## 📄 Licence

[À définir selon votre institution]

---

**Note**: Ce projet est à des fins de recherche académique. L'utilisation responsable et éthique est primordiale.

**Version**: 1.0.0  
**Dernière mise à jour**: 20 Janvier 2026