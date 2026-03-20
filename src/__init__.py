"""
WMDP Pipeline - Évaluation de Sécurité LLM
==========================================

Structure:
- prompt_runner.py    : Orchestration prompts + modèles
- response_annotator.py: Annotation automatique des réponses
- wmdp_analyzer.py    : Analyse et statistiques
- elk_logger.py       : Logging ELK 
- hf_client.py        : Clients LLM (HuggingFace locaux)
- wmdp_pipeline.py    : Pipeline complète (main entry point)
"""

__version__ = "3.0"
__author__ = "WMDP Team"
