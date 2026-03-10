#!/usr/bin/env python3
"""
Test d'intégration HF + ELK
Exécute le pipeline WMDP avec HuggingFace local et ELK logging
"""

import sys
from pathlib import Path
import logging
import json
from datetime import datetime

# Setup path
BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / 'src'))

# Load environment
from dotenv import load_dotenv
load_dotenv(BASE / '.env')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import components
from prompt_runner import PromptRunner
from wmdp_analyzer import WMDPAnalyzer

def main():
    logger.info("="*70)
    logger.info("🚀 WMDP Pipeline Test: HuggingFace Local + ELK")
    logger.info("="*70)
    
    # Setup directories
    output_dir = BASE / "results"
    output_dir.mkdir(exist_ok=True)
    
    # Initialize runner
    logger.info("\n📌 Initializing PromptRunner...")
    runner = PromptRunner(
        dataset_path=str(BASE / "data" / "wmdp_prompts.json"),
        output_dir=str(output_dir),
        log_dir=str(BASE / "logs")
    )
    
    # Load dataset
    logger.info("\n📚 Loading dataset...")
    dataset_file = BASE / "data" / "wmdp_prompts.json"
    if not dataset_file.exists():
        logger.warning(f"Dataset not found at {dataset_file}")
        logger.info("Using example dataset instead...")
        dataset_file = BASE / "data" / "wmdp_prompts_example.json"
    
    num_loaded = runner.load_dataset(str(dataset_file))
    logger.info(f"✅ Loaded {num_loaded} prompts")
    
    # Run on multiple HF local models to get diverse data
    logger.info("\n🤗 Running prompts on HuggingFace (multiple local models)...")
    logger.info("This will test 4 different small local models (will take ~5-10 minutes)...\n")
    
    # Use small models that work locally (distilgpt2, gpt2, opt-125m, etc)
    models_to_test = [
        "distilgpt2-local",      # Smallest & fastest (82M parameters)
        "gpt2-local",            # Small model (124M parameters)
        "opt-125m-local",        # Meta's OPT family (125M parameters)
        "pythia-70m-local"       # EleutherAI Pythia (70M parameters)
    ]
    all_responses = []
    
    for model in models_to_test:
        logger.info(f"\n🚀 Testing with model: {model}")
        try:
            responses = runner.run_prompts(
                model_name=model,
                max_prompts=15,  # Test with 15 prompts per model (~60 total)
                delay_between_calls=0.5
            )
            all_responses.extend(responses)
            logger.info(f"✅ Generated {len(responses)} responses from {model}")
        except Exception as e:
            logger.warning(f"⚠️  Failed to test {model}: {e}")
            continue
    
    responses = all_responses
    
    if not responses:
        logger.error("❌ No responses generated")
        return 1
    
    logger.info(f"\n✅ Generated {len(responses)} responses")
    
    # 🔴 ANNOTER LES REPONSES (IMPORTANT!)
    logger.info("\n🏷️  Annotating responses with WMDP criteria...")
    try:
        from response_annotator import ResponseAnnotator
        annotator = ResponseAnnotator()
        annotated_responses = []
        
        for response in responses:
            annotation = annotator.annotate(
                prompt_text=response.prompt_text,
                response_text=response.response_text,
                model_name=response.model_name,
                prompt_risk_level=response.prompt_risk_level,
                prompt_category=response.prompt_category,
                prompt_id=response.prompt_id
            )
            # Merge annotation into response
            response_dict = {
                "prompt_id": response.prompt_id,
                "prompt_text": response.prompt_text,
                "prompt_category": response.prompt_category,
                "prompt_risk_level": response.prompt_risk_level,
                "model_name": response.model_name,
                "response_text": response.response_text,
                "latency_ms": response.latency_ms,
                "response_behavior": annotation.annotation.response_behavior.value,
                "compliance_level": annotation.annotation.compliance_level.value,
                "harmfulness_level": annotation.annotation.harmfulness_level.value,
                "timestamp": datetime.now().isoformat()
            }
            annotated_responses.append(response_dict)
        
        logger.info(f"✅ Annotated {len(annotated_responses)} responses")
        
    except Exception as e:
        logger.warning(f"⚠️  Annotation failed: {e}. Continuing with unannotated responses...")
        annotated_responses = [
            {
                "prompt_id": r.prompt_id,
                "prompt_text": r.prompt_text,
                "model_name": r.model_name,
                "response_text": r.response_text,
                "latency_ms": r.latency_ms,
                "response_behavior": "unannotated",
                "timestamp": datetime.now().isoformat()
            }
            for r in responses
        ]
    
    # Save responses
    logger.info("\n💾 Saving responses...")
    output_file = runner.save_responses(responses)
    logger.info(f"✅ Responses saved to: {output_file}")
    
    # Basic analysis
    logger.info("\n📊 Basic Statistics:")
    avg_latency = sum(r.latency_ms for r in responses) / len(responses)
    logger.info(f"  • Average latency: {avg_latency:.0f}ms")
    logger.info(f"  • Total prompts: {len(responses)}")
    logger.info(f"  • Models tested: {set(r.model_name for r in responses)}")
    
    # Try ELK logging
    logger.info("\n📮 Attempting ELK logging...")
    try:
        from elk_logger import ELKLogger
        elk_logger = ELKLogger()
        
        for i, response_dict in enumerate(annotated_responses, 1):
            # Log collection event (response) with annotations
            elk_logger.log_collection_event({
                "timestamp": response_dict["timestamp"],
                "model_name": response_dict["model_name"],
                "prompt_id": response_dict["prompt_id"],
                "prompt_text": response_dict["prompt_text"],
                "response_text": response_dict["response_text"],
                "latency_ms": response_dict["latency_ms"],
                "response_behavior": response_dict.get("response_behavior", "unknown"),
                "compliance_level": response_dict.get("compliance_level", "unknown"),
                "harmfulness_level": response_dict.get("harmfulness_level", "unknown"),
                "prompt_category": response_dict.get("prompt_category", "unknown"),
                "prompt_risk_level": response_dict.get("prompt_risk_level", "unknown"),
                "status": "success"
            })
        
            logger.debug(f"  [✅] {response_dict['prompt_id']} → {response_dict.get('response_behavior', 'unknown')}")
        
        logger.info(f"✅ Logged {len(annotated_responses)} responses to ELK")
        
        # Query ELK to confirm
        logger.info("\n🔍 Querying ELK to confirm logging...")
        from elasticsearch import Elasticsearch
        es = Elasticsearch(["http://localhost:9200"])
        result = es.search(
            index="wmdp-collection-*",
            body={"size": 0, "track_total_hits": True}
        )
        total = result["hits"]["total"]["value"]
        logger.info(f"✅ ELK confirmed: {total} total documents in wmdp-collection indices")
        
    except Exception as e:
        logger.warning(f"⚠️  ELK logging failed: {e}")
    
    logger.info("\n" + "="*70)
    logger.info("🎉 Test completed successfully!")
    logger.info("="*70)
    logger.info("\nNext steps:")
    logger.info("1. Open Kibana: http://localhost:5601")
    logger.info("2. Create index pattern: wmdp-*")
    logger.info("3. View dashboard for real-time data")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
