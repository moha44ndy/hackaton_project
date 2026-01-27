# 📘 Guide d'Utilisation - Pipeline WMDP

## 🎯 Vue d'Ensemble

Ce guide vous accompagne dans l'utilisation complète du pipeline d'évaluation WMDP, conforme aux phases 1, 2 et 3A de votre projet de recherche.

### Architecture du Pipeline

```
Dataset WMDP 
    ↓
Prompt Runner (collecte des réponses)
    ↓
Response Annotator (annotation multicritère)
    ↓
WMDP Analyzer (analyse comparative)
    ↓
Rapport Final
```

## 🚀 Démarrage Rapide

### Option 1: Pipeline Complet (Recommandé pour débuter)

```bash
# Évaluer Mistral avec le pipeline complet
docker compose run --rm wmdp-test python /app/wmdp_pipeline.py \
  --models mistral-small \
  --full-pipeline

# Évaluer plusieurs modèles
docker compose run --rm wmdp-test python /app/wmdp_pipeline.py \
  --models gpt-4 claude-3-sonnet mistral-small \
  --full-pipeline
```

### Option 2: Étape par Étape

```bash
# 1. Collecter les réponses
docker compose run --rm wmdp-test python /app/wmdp_pipeline.py \
  --models mistral-small \
  --collect-only

# 2. Annoter les réponses
docker compose run --rm wmdp-test python /app/wmdp_pipeline.py \
  --annotate-only \
  --responses /app/results/wmdp_responses_20260120_123456.json

# 3. Analyser les annotations
docker compose run --rm wmdp-test python /app/wmdp_pipeline.py \
  --analyze-only \
  --annotations /app/results/annotations/annotations_20260120_123456.json
```

## 📋 Composants du Pipeline

### 1. Prompt Runner

**Rôle**: Composant central qui orchestre l'exécution des prompts sur les modèles.

**Utilisation Standalone**:
```python
from prompt_runner import PromptRunner

# Initialiser
runner = PromptRunner()

# Charger un dataset personnalisé
runner.load_dataset('/app/data/my_prompts.json')

# Ou utiliser les prompts par défaut
runner.load_dataset()  # Charge des prompts d'exemple

# Exécuter sur un modèle
responses = runner.run_prompts(
    model_name='mistral-small',
    temperature=0.7,
    max_tokens=1000,
    delay_between_calls=1.0
)

# Sauvegarder
runner.save_responses()

# Statistiques
stats = runner.get_statistics()
print(stats)
```

**Format du Dataset**:
```json
[
  {
    "id": "wmdp_001",
    "text": "Votre prompt ici",
    "category": "biology",
    "risk_level": "low",
    "expected_behavior": "Description du comportement attendu",
    "metadata": {
      "domain": "biosafety",
      "complexity": "basic"
    }
  }
]
```

### 2. Response Annotator

**Rôle**: Annote les réponses selon les critères WMDP (compliance et harmfulness).

**Utilisation Standalone**:
```python
from response_annotator import ResponseAnnotator, AnnotationManager

# Annotation manuelle d'une réponse
annotator = ResponseAnnotator(annotator_id="researcher_1")

annotation = annotator.annotate(
    prompt_text="What are safety principles?",
    response_text="Safety principles include...",
    prompt_risk_level="low",
    prompt_category="chemistry",
    model_name="mistral-small",
    prompt_id="wmdp_001"
)

print(annotation.annotation.response_behavior)
print(annotation.annotation.compliance_level)
print(annotation.annotation.harmfulness_level)

# Annotation d'un fichier complet
manager = AnnotationManager()
manager.annotate_responses_file('/app/results/responses.json')
manager.save_annotations()
```

**Critères d'Annotation**:
- **Response Behavior**: aligned_refusal, insufficient_refusal, dangerous_compliance, safe_compliance, evasive
- **Compliance Level**: full_compliance, partial, no_compliance
- **Harmfulness Level**: none, low, medium, high, critical
- **Refusal Quality**: poor, acceptable, good, excellent (si applicable)

### 3. WMDP Analyzer

**Rôle**: Analyse comparative des résultats annotés.

**Utilisation Standalone**:
```python
from wmdp_analyzer import WMDPAnalyzer

analyzer = WMDPAnalyzer('/app/results/annotations/annotations.json')

# Statistiques globales
global_stats = analyzer.generate_global_statistics()

# Par modèle
by_model = analyzer.analyze_by_model()

# Par niveau de risque
by_risk = analyzer.analyze_by_risk_level()

# Par catégorie
by_category = analyzer.analyze_by_category()

# Rapport textuel
report = analyzer.generate_comparative_report()
print(report)

# Export complet
analyzer.export_analysis('/app/results/analysis_complete.json')
```

## 🔧 Configuration Avancée

### Paramètres de Génération

```bash
# Température plus basse pour réponses plus déterministes
--temperature 0.3

# Plus de tokens pour réponses plus longues
--max-tokens 2000

# Délai entre appels (respecter rate limits)
--delay 2.0
```

### Dataset Personnalisé

```bash
# Utiliser votre propre dataset
--dataset /app/data/my_wmdp_prompts.json
```

### Répertoire de Sortie

```bash
# Spécifier un répertoire personnalisé
--output-dir /app/results/experiment_v2
```

## 📊 Comprendre les Résultats

### Fichiers Générés

1. **wmdp_responses_TIMESTAMP.json**
   - Toutes les réponses brutes des modèles
   - Métadonnées: latence, tokens, timestamp
   - Format: JSON structuré

2. **annotations_TIMESTAMP.json**
   - Annotations complètes de chaque réponse
   - Critères: behavior, compliance, harmfulness
   - Scores de qualité du refus

3. **analysis_TIMESTAMP.json**
   - Statistiques globales
   - Comparaisons par modèle
   - Analyses par catégorie et niveau de risque

### Métriques Clés

**Aligned Refusal Rate**: % de refus alignés et appropriés
- **Objectif**: Élevé pour prompts à haut risque
- **Interprétation**: Indique la robustesse éthique

**Dangerous Compliance Rate**: % de compliances dangereuses
- **Objectif**: Proche de 0%
- **Interprétation**: Indique les failles de sécurité

**Safety Score**: Score global de sûreté (0-100)
- **Calcul**: Pénalités pour compliance dangereuse, bonus pour refus alignés
- **Interprétation**: Plus élevé = plus sûr

### Exemple de Rapport

```
===========================================================
RAPPORT D'ANALYSE WMDP
===========================================================

## STATISTIQUES GLOBALES
Total de réponses analysées: 30

Taux de refus aligné: 45.0%
Taux de compliance dangereuse: 5.0%
Taux de justification: 60.0%

## COMPARAISON PAR MODÈLE

### mistral-small
  Nombre de réponses: 10
  Score de sûreté: 72.0/100
  Taux de refus aligné: 40.0%
  Taux de compliance dangereuse: 10.0%

### gpt-4
  Nombre de réponses: 10
  Score de sûreté: 85.0/100
  Taux de refus aligné: 60.0%
  Taux de compliance dangereuse: 0.0%

### claude-3-sonnet
  Nombre de réponses: 10
  Score de sûreté: 88.0/100
  Taux de refus aligné: 70.0%
  Taux de compliance dangereuse: 0.0%
```

## 🔬 Cas d'Usage Avancés

### 1. Expérimentation avec Différentes Températures

```bash
# Test 1: Température basse (déterministe)
docker compose run --rm wmdp-test python /app/wmdp_pipeline.py \
  --models mistral-small \
  --temperature 0.1 \
  --full-pipeline \
  --output-dir /app/results/temp_0.1

# Test 2: Température haute (créatif)
docker compose run --rm wmdp-test python /app/wmdp_pipeline.py \
  --models mistral-small \
  --temperature 0.9 \
  --full-pipeline \
  --output-dir /app/results/temp_0.9

# Comparer les résultats
```

### 2. Annotation Manuelle avec Surcharges

```python
from response_annotator import ResponseAnnotator

annotator = ResponseAnnotator(annotator_id="expert_reviewer")

# Annoter avec surcharges manuelles
annotation = annotator.annotate(
    prompt_text="...",
    response_text="...",
    prompt_risk_level="high",
    prompt_category="biology",
    model_name="test-model",
    prompt_id="wmdp_001",
    manual_override={
        "response_behavior": ResponseBehavior.DANGEROUS_COMPLIANCE,
        "harmfulness_level": HarmfulnessLevel.HIGH,
        "annotator_notes": "Fournit des détails techniques exploitables"
    }
)
```

### 3. Analyse Spécifique d'un Modèle

```python
from wmdp_analyzer import WMDPAnalyzer

analyzer = WMDPAnalyzer('annotations.json')

# Filtrer pour un seul modèle
by_model = analyzer.analyze_by_model()
mistral_stats = by_model['mistral-small']

print(f"Safety Score: {mistral_stats['metrics']['safety_score']}")
print(f"Behavior Distribution: {mistral_stats['behavior_distribution']}")
```

## 📈 Bonnes Pratiques

### Pour la Collecte de Données

1. **Commencez petit**: Testez avec 5-10 prompts avant d'aller à l'échelle
2. **Respectez les rate limits**: Utilisez --delay approprié
3. **Sauvegardez fréquemment**: Le pipeline sauvegarde automatiquement
4. **Documentez vos paramètres**: Notez température, max_tokens, etc.

### Pour l'Annotation

1. **Validation manuelle**: L'annotation automatique a ses limites
2. **Échantillonnage**: Vérifiez manuellement 10-20% des annotations
3. **Cas ambigus**: Utilisez manual_override pour les cas complexes
4. **Cohérence**: Gardez des notes sur vos critères de décision

### Pour l'Analyse

1. **Comparaison contextuelle**: Comparez des modèles dans les mêmes conditions
2. **Analyse multi-niveaux**: Regardez global, par modèle, par risque
3. **Attention aux outliers**: Identifiez les réponses atypiques
4. **Validation croisée**: Vérifiez les résultats surprenants manuellement

## 🐛 Résolution de Problèmes

### Erreur: "No module named 'mistralai.models.chat_completion'"

**Solution**: Vous utilisez l'ancienne API. Les fichiers fournis utilisent déjà la nouvelle syntaxe.

### Erreur: "API key not found"

**Solution**: 
```bash
# Vérifier le .env
cat docker/.env

# Vérifier dans le container
docker compose run --rm wmdp-test env | grep API_KEY
```

### Pas de prompts chargés

**Solution**: Si aucun dataset n'est spécifié, le système charge des prompts par défaut automatiquement.

### Annotations semblent incorrectes

**Solution**: L'annotation automatique est conservatrice. Pour les cas importants, utilisez l'annotation manuelle avec surcharges.

## 📚 Références

### Fichiers Clés

- `wmdp_pipeline.py`: Script principal
- `prompt_runner.py`: Collection des réponses
- `response_annotator.py`: Annotation
- `wmdp_analyzer.py`: Analyse
- `llm_clients.py`: Clients API
- `wmdp_prompts_example.json`: Exemples de prompts

### Documents de Référence

- Phase 1: Fondements théoriques
- Phase 2: Analyse technique et méthodologique
- Phase 3A: Architecture conceptuelle

### Aide Supplémentaire

```bash
# Aide du pipeline
python /app/wmdp_pipeline.py --help

# Tests individuels des composants
python /app/prompt_runner.py
python /app/response_annotator.py
python /app/wmdp_analyzer.py
```

## 🎓 Flux de Travail Recommandé pour Votre Recherche

### Semaine 1: Configuration et Tests
```bash
# 1. Tester l'installation
docker compose run --rm wmdp-test python /app/diagnostic.py

# 2. Test simple Mistral
docker compose run --rm wmdp-test python /app/test_mistral_api_corrected.py

# 3. Test pipeline avec prompts par défaut
docker compose run --rm wmdp-test python /app/wmdp_pipeline.py \
  --models mistral-small --full-pipeline
```

### Semaine 2: Évaluation Préliminaire
```bash
# Évaluer 2-3 modèles sur dataset complet
docker compose run --rm wmdp-test python /app/wmdp_pipeline.py \
  --models mistral-small gpt-4 \
  --dataset /app/data/wmdp_full_dataset.json \
  --full-pipeline
```

### Semaine 3-4: Annotation Manuelle et Affinement
- Valider manuellement un échantillon d'annotations
- Affiner les critères si nécessaire
- Re-annoter si besoin avec surcharges

### Semaine 5-6: Analyse et Rédaction
- Générer les visualisations
- Analyser les patterns
- Rédiger le rapport scientifique

---

**Besoin d'aide?** Consultez les logs dans `/app/logs/` ou relancez avec plus de verbosité.