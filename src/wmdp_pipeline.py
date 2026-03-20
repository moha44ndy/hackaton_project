#!/usr/bin/env python3
"""
Pipeline Complet d'Évaluation WMDP
Orchestration de toute la chaîne: Dataset → Prompts → Réponses → Annotation → Analyse

Conforme aux Phases 1, 2 et 3A du projet
"""

import argparse
import logging
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# Charger .env à la racine du projet (pour HUGGINGFACE_TOKEN, etc.) en exécution locale
try:
    from dotenv import load_dotenv
    _env_file = Path(__file__).resolve().parent.parent / ".env"
    if _env_file.exists():
        load_dotenv(_env_file)
except ImportError:
    pass

from hackaton_project.src.prompt_runner import PromptRunner
from hackaton_project.src.response_annotator import AnnotationManager
from hackaton_project.src.wmdp_analyzer import WMDPAnalyzer
from hackaton_project.src.llm_clients import MODEL_CONFIGS
import os

# ELK logger (initialized in main)
ELK_LOGGER = None
try:
    from hackaton_project.src.elk_logger import get_elk_logger
except Exception:
    get_elk_logger = None

# Racine projet (parent de src/) pour exécution locale
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
# Docker : sous Windows on est toujours "local"; sous Linux /app/results indique Docker
_IN_DOCKER = sys.platform != "win32" and Path("/app/results").exists()
# Chemins : Docker (/app/...) ou local (répertoires sous la racine projet)
_log_dir = Path("/app/logs") if _IN_DOCKER else _PROJECT_ROOT / "logs"
_log_dir.mkdir(parents=True, exist_ok=True)
_log_file = _log_dir / "wmdp_pipeline.log"
_default_output_dir = "/app/results" if _IN_DOCKER else str(_PROJECT_ROOT / "results")
# Dataset par défaut : data/wmdp_prompts.json
_default_dataset = None
_candidate = _PROJECT_ROOT / "data" / "wmdp_prompts.json" if not _IN_DOCKER else Path("/app/data/wmdp_prompts.json")
if _candidate.exists():
    _default_dataset = str(_candidate)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(_log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parser les arguments de ligne de commande"""
    parser = argparse.ArgumentParser(
        description="Pipeline complet d'évaluation WMDP des modèles de langage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:

  # Évaluation complète (prompts → annotation → analyse)
  python wmdp_pipeline.py --models mistral-small --full-pipeline
  
  # Seulement collecter les réponses
  python wmdp_pipeline.py --models gpt-4 claude-3-sonnet --collect-only
  
  # Seulement annoter des réponses existantes
  python wmdp_pipeline.py --annotate-only --responses results/responses_20260120.json
  
  # Seulement analyser des annotations existantes
  python wmdp_pipeline.py --analyze-only --annotations results/annotations_20260120.json
        """
    )
    
    # Modèles à évaluer
    parser.add_argument(
        '--models',
        nargs='+',
        choices=list(MODEL_CONFIGS.keys()),
        help='Modèles à évaluer'
    )
    
    # Dataset
    parser.add_argument(
        '--dataset',
        type=str,
        default=_default_dataset,
        help='Chemin vers le dataset WMDP JSON (défaut: data/wmdp_prompts.json si présent, sinon prompts intégrés)'
    )
    
    # Modes d'exécution
    parser.add_argument(
        '--full-pipeline',
        action='store_true',
        help='Exécuter le pipeline complet: collection → annotation → analyse'
    )
    
    parser.add_argument(
        '--collect-only',
        action='store_true',
        help='Collecter uniquement les réponses des modèles'
    )
    
    parser.add_argument(
        '--annotate-only',
        action='store_true',
        help='Annoter uniquement un fichier de réponses existant'
    )
    
    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='Analyser uniquement un fichier d\'annotations existant'
    )
    
    # Fichiers d'entrée pour modes partiels
    parser.add_argument(
        '--responses',
        type=str,
        help='Fichier de réponses pour --annotate-only'
    )
    
    parser.add_argument(
        '--annotations',
        type=str,
        help='Fichier d\'annotations pour --analyze-only'
    )
    
    # Paramètres de génération
    parser.add_argument(
        '--temperature',
        type=float,
        default=0.7,
        help='Température de génération (défaut: 0.7)'
    )
    
    parser.add_argument(
        '--max-tokens',
        type=int,
        default=1000,
        help='Nombre maximum de tokens par réponse (défaut: 1000)'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        help='Délai entre les appels API en secondes (défaut: 1.0)'
    )
    
    parser.add_argument(
        '--max-prompts',
        type=int,
        default=None,
        metavar='N',
        help='Limiter à N premiers prompts (pour tests rapides, ex: --max-prompts 5)'
    )
    
    # Répertoires
    parser.add_argument(
        '--output-dir',
        type=str,
        default=_default_output_dir,
        help='Répertoire de sortie (défaut: /app/results en Docker, sinon results/)'
    )
    
    return parser.parse_args()


def run_collection_phase(
    runner: PromptRunner,
    models: list,
    temperature: float,
    max_tokens: int,
    delay: float,
    max_prompts: Optional[int] = None
) -> str:
    """
    Phase 1: Collection des réponses
    
    Returns:
        Chemin du fichier de réponses
    """
    logger.info("\n" + "="*60)
    logger.info("PHASE 1: COLLECTION DES RÉPONSES")
    logger.info("="*60)
    
    all_responses = []
    
    for model in models:
        logger.info(f"\n🤖 Évaluation du modèle: {model}")
        
        responses = runner.run_prompts(
            model_name=model,
            temperature=temperature,
            max_tokens=max_tokens,
            delay_between_calls=delay,
            max_prompts=max_prompts
        )
        
        all_responses.extend(responses)
        
        logger.info(f"✅ {len(responses)} réponses collectées pour {model}")
    
    # Sauvegarder toutes les réponses
    responses_file = runner.save_responses()
    
    # Log events to ELK (per response)
    try:
        if ELK_LOGGER:
            for resp in all_responses:
                try:
                    ELK_LOGGER.log_collection_event({
                        "timestamp": resp.timestamp,
                        "model_name": resp.model_name,
                        "prompt_id": resp.prompt_id,
                        "latency_ms": resp.latency_ms,
                        "token_count": resp.tokens_used or 0,
                        "status": "success"
                    })
                except Exception:
                    # Do not break pipeline for logging errors
                    logger.debug("ELK log error for collection event")
    except Exception:
        pass
    logger.info(f"\n✅ Phase 1 terminée: {len(all_responses)} réponses totales")
    logger.info(f"📁 Fichier: {responses_file}")
    
    return responses_file


def run_annotation_phase(responses_file: str) -> str:
    """
    Phase 2: Annotation des réponses
    
    Args:
        responses_file: Chemin vers le fichier de réponses
        
    Returns:
        Chemin du fichier d'annotations
    """
    logger.info("\n" + "="*60)
    logger.info("PHASE 2: ANNOTATION DES RÉPONSES")
    logger.info("="*60)
    
    manager = AnnotationManager()
    
    # Annoter les réponses
    count = manager.annotate_responses_file(responses_file)
    
    # Sauvegarder les annotations
    annotations_file = manager.save_annotations()
    
    # Log annotation events to ELK
    try:
        if ELK_LOGGER:
            for a in manager.annotations:
                try:
                    ELK_LOGGER.log_annotation_event({
                        "timestamp": a.annotation.annotation_timestamp,
                        "response_id": a.response_id,
                        "response_behavior": a.annotation.response_behavior.value,
                        "compliance_level": a.annotation.compliance_level.value,
                        "harmfulness_level": a.annotation.harmfulness_level.value,
                        "annotator_id": a.annotation.annotator_id
                    })
                except Exception:
                    logger.debug("ELK log error for annotation event")
    except Exception:
        pass
    logger.info(f"\n✅ Phase 2 terminée: {count} annotations créées")
    logger.info(f"📁 Fichier: {annotations_file}")
    
    return annotations_file


def run_analysis_phase(annotations_file: str, output_dir: str):
    """
    Phase 3: Analyse des résultats
    
    Args:
        annotations_file: Chemin vers le fichier d'annotations
        output_dir: Répertoire de sortie
        
    Returns:
        Chemin du fichier d'analyse
    """
    logger.info("\n" + "="*60)
    logger.info("PHASE 3: ANALYSE DES RÉSULTATS")
    logger.info("="*60)
    
    analyzer = WMDPAnalyzer(annotations_file)
    
    # Générer et afficher le rapport
    report = analyzer.generate_comparative_report()
    logger.info("\n" + report)
    
    # Sauvegarder un rapport lisible (Markdown)
    reports_dir = Path('/app/data/rapports') if _IN_DOCKER else _PROJECT_ROOT / "data" / "rapports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_file = reports_dir / f"wmdp_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        # Le rapport généré est du texte structuré (utilise des en-têtes '##'), on l'enregistre tel quel
        f.write(report)
    logger.info(f"💾 Rapport markdown sauvegardé: {report_file}")

    # Exporter l'analyse complète
    analysis_file = Path(output_dir) / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    analyzer.export_analysis(str(analysis_file))
    
    logger.info(f"\n✅ Phase 3 terminée")
    logger.info(f"📁 Fichiers: {analysis_file} | {report_file}")

    # Log analysis summary to ELK
    try:
        if ELK_LOGGER:
            global_stats = analyzer.generate_global_statistics()
            by_model = analyzer.analyze_by_model()
            models_tested = list(by_model.keys())
            # average safety score across models
            scores = [v.get('metrics', {}).get('safety_score', 0) for v in by_model.values()]
            safety_score_avg = sum(scores) / len(scores) if scores else 0
            total = global_stats.get('total_responses', 0)
            total_compliances = global_stats.get('key_metrics', {}).get('total_compliances', 0)
            compliance_rate = (total_compliances / total) if total > 0 else 0

            try:
                ELK_LOGGER.log_analysis_event({
                    "timestamp": datetime.now().isoformat(),
                    "run_id": Path(analysis_file).stem,
                    "total_responses": int(total),
                    "avg_latency_ms": 0,
                    "models_tested": models_tested,
                    "safety_score": float(safety_score_avg),
                    "compliance_rate": float(compliance_rate)
                })
            except Exception:
                logger.debug("ELK log error for analysis event")
    except Exception:
        pass
    
    return str(analysis_file), report_file


def save_evaluation_finale(
    analysis_file: str,
    report_file: Path,
    responses_file: str,
    annotations_file: str,
    models_used: list,
    dataset_path: Optional[str],
) -> Path:
    """
    Enregistrer le rapport d'évaluation finale (JSON consolidé) selon la logique du projet WMDP.
    Un seul fichier par run : métadonnées + analyse globale + par modèle + par niveau de risque.
    """
    reports_dir = report_file.parent
    with open(analysis_file, 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    
    # Enrichir avec le contexte du run (dataset, modèles, chemins)
    risk_levels_in_dataset = []
    total_prompts_dataset = 0
    if dataset_path and Path(dataset_path).exists():
        try:
            with open(dataset_path, 'r', encoding='utf-8') as f:
                dataset = json.load(f)
            from collections import Counter
            rl = Counter(p.get('risk_level', 'unknown') for p in dataset)
            risk_levels_in_dataset = [{"risk_level": k, "count": v} for k, v in sorted(rl.items())]
            total_prompts_dataset = len(dataset)
        except Exception:
            pass
    
    evaluation_finale = {
        "projet": "WMDP - Évaluation éthique et sécuritaire des LLMs",
        "type": "rapport_evaluation_finale",
        "timestamp": datetime.now().isoformat(),
        "run": {
            "models_evalués": models_used,
            "dataset": dataset_path or "default",
            "total_prompts_dataset": total_prompts_dataset,
            "niveaux_risque_couverts": risk_levels_in_dataset,
            "fichiers": {
                "reponses": responses_file,
                "annotations": annotations_file,
                "analyse": analysis_file,
                "rapport_md": str(report_file),
            },
        },
        "analyse": analysis,
        "synthese": {
            "total_reponses_analysees": analysis.get("total_annotations", 0),
            "metriques_globales": analysis.get("global_statistics", {}).get("key_metrics", {}),
            "modeles": list(analysis.get("by_model", {}).keys()),
        },
    }
    
    out_path = reports_dir / f"wmdp_evaluation_finale_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(evaluation_finale, f, indent=2, ensure_ascii=False)
    logger.info(f"📋 Rapport d'évaluation finale enregistré: {out_path}")
    return out_path


def main():
    """Fonction principale"""
    args = parse_arguments()
    
    logger.info("="*60)
    logger.info("PIPELINE D'ÉVALUATION WMDP")
    logger.info("="*60)
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    # Initialize ELK logger (if available)
    try:
        if get_elk_logger:
            elk_host = os.getenv('ELK_HOST', 'http://localhost:9200')
            elk_enabled = os.getenv('ELK_ENABLED', '1') != '0'
            globals()['ELK_LOGGER'] = get_elk_logger(es_host=elk_host, enabled=elk_enabled)
            logger.info(f"ELK logger initialized (host={elk_host}, enabled={elk_enabled})")
    except Exception:
        logger.warning("ELK logger not available")
    
    # Déterminer le mode d'exécution
    if args.analyze_only:
        # Mode: Analyse uniquement
        if not args.annotations:
            logger.error("❌ --annotations requis pour --analyze-only")
            return 1
        
        run_analysis_phase(args.annotations, args.output_dir)  # returns (analysis_file, report_file)
    
    elif args.annotate_only:
        # Mode: Annotation uniquement
        if not args.responses:
            logger.error("❌ --responses requis pour --annotate-only")
            return 1
        
        annotations_file = run_annotation_phase(args.responses)
        
        # Optionnel: lancer l'analyse ensuite
        logger.info("\n💡 Voulez-vous analyser les annotations maintenant?")
        logger.info(f"Utilisez: python wmdp_pipeline.py --analyze-only --annotations {annotations_file}")
    
    elif args.collect_only or args.full_pipeline:
        # Mode: Collection (et éventuellement suite du pipeline)
        if not args.models:
            logger.error("❌ --models requis pour la collection")
            return 1
        
        # Initialiser le runner
        runner = PromptRunner(
            dataset_path=args.dataset,
            output_dir=args.output_dir
        )
        
        # Charger le dataset
        runner.load_dataset(args.dataset)
        
        # Phase 1: Collection
        responses_file = run_collection_phase(
            runner=runner,
            models=args.models,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            delay=args.delay,
            max_prompts=args.max_prompts
        )
        
        if not responses_file or not Path(responses_file).exists():
            logger.error("❌ Aucune réponse collectée (vérifiez les clés API, ex. HUGGINGFACE_TOKEN). Pipeline arrêté.")
            return 1
        
        if args.full_pipeline:
            # Phase 2: Annotation
            annotations_file = run_annotation_phase(responses_file)
            
            # Phase 3: Analyse
            analysis_file, report_file = run_analysis_phase(annotations_file, args.output_dir)
            
            # Rapport d'évaluation finale (JSON consolidé, logique projet WMDP)
            save_evaluation_finale(
                analysis_file=analysis_file,
                report_file=report_file,
                responses_file=responses_file,
                annotations_file=annotations_file,
                models_used=args.models,
                dataset_path=args.dataset,
            )
            
            logger.info("\n" + "="*60)
            logger.info("✅ PIPELINE COMPLET TERMINÉ AVEC SUCCÈS")
            logger.info("="*60)
        else:
            logger.info("\n💡 Pour annoter les réponses:")
            logger.info(f"python wmdp_pipeline.py --annotate-only --responses {responses_file}")
    
    else:
        logger.error("❌ Vous devez spécifier un mode d'exécution:")
        logger.error("  --full-pipeline : Pipeline complet")
        logger.error("  --collect-only : Collection uniquement")
        logger.error("  --annotate-only : Annotation uniquement")
        logger.error("  --analyze-only : Analyse uniquement")
        logger.error("\nUtilisez --help pour plus d'informations")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())