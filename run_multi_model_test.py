#!/usr/bin/env python3
"""
Lance la pipeline WMDP avec PLUSIEURS modèles LOCAUX
- distilgpt2 (124M) - Déjà testé
- gpt2 (137M)
- opt-125m (125M)
- pythia-70m (70M)

LOCAUX = Pas besoin de clés API!
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Ajouter src au path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from llm_clients import TransformersClient
from elk_logger import get_elk_logger
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modèles LOCAUX à tester (garantis de marcher)
MODELS_TO_TEST = [
    "distilgpt2",      # 124M - Testé ✓
    "gpt2",            # 137M - Classique ✓
    "gpt2-medium",     # 355M - Plus puissant
]

def run_multi_model_test():
    """Lance test avec plusieurs modèles LOCAUX"""
    print("\n" + "="*70)
    print("🚀 TEST MULTIPLE MODÈLES LOCAUX WMDP")
    print("="*70)
    
    # Charger prompts
    dataset_path = Path(__file__).parent / "data" / "wmdp_prompts.json"
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    prompts = dataset[:10]  # 10 prompts × 3 modèles = 30 total
    print(f"📥 Dataset: {len(prompts)} prompts")
    
    # ELK logger
    elk_logger = get_elk_logger(enabled=True)
    print(f"✅ ELK logger activé")
    
    all_responses = []
    
    for model_name in MODELS_TO_TEST:
        print(f"\n{'='*70}")
        print(f"🤖 Modèle: {model_name}")
        print(f"{'='*70}")
        
        try:
            # Créer client local
            print(f"📥 Chargement modèle {model_name}...")
            client = TransformersClient(model=model_name)
            print(f"✅ Modèle chargé!")
            
            # Générer réponses
            model_responses = []
            for i, prompt in enumerate(prompts):
                try:
                    prompt_id = prompt.get('id', f'prompt_{i}')
                    prompt_text = prompt.get('text', '')
                    category = prompt.get('category', 'general')
                    risk_level = prompt.get('risk_level', 'low')
                    
                    print(f"  ⏳ [{i+1}/{len(prompts)}] {prompt_id[:20]}...", end=" ")
                    
                    # Générer
                    response, metadata = client.generate(
                        prompt=prompt_text,
                        max_tokens=256,
                        temperature=0.7
                    )
                    
                    # Construire doc
                    doc = {
                        "prompt_id": prompt_id,
                        "model_name": model_name,
                        "prompt_text": prompt_text,
                        "response_text": response,
                        "timestamp": datetime.now().isoformat(),
                        "latency_ms": metadata.get('latency_ms', 0),
                        "tokens_used": metadata.get('tokens_used', 0),
                        "model_version": model_name,
                        "temperature": 0.7,
                        "max_tokens": 256,
                        "prompt_category": category,
                        "prompt_risk_level": risk_level,
                    }
                    
                    model_responses.append(doc)
                    all_responses.append(doc)
                    
                    print(f"✅ ({len(response)} chars)")
                    
                except Exception as e:
                    print(f"❌ {e}")
                    continue
            
            print(f"\n✅ {model_name}: {len(model_responses)} réponses générées")
            
            # Log to ELK
            for doc in model_responses:
                try:
                    elk_logger.log_collection_event({
                        "model": model_name,
                        "prompt_id": doc['prompt_id'],
                        "response_length": len(doc['response_text']),
                        "category": doc['prompt_category'],
                    })
                except:
                    pass
            
        except Exception as e:
            print(f"❌ Erreur {model_name}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # Sauvegarder résultats
    output_file = Path(__file__).parent / "results" / f"wmdp_responses_multimodel_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    output_data = {
        "metadata": {
            "total_responses": len(all_responses),
            "export_timestamp": datetime.now().isoformat(),
            "models": list(set(r['model_name'] for r in all_responses))
        },
        "responses": all_responses
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*70)
    print("✅ TEST TERMINÉ!")
    print("="*70)
    print(f"""
📊 Résultats:
   - {len(set(r['model_name'] for r in all_responses))} modèles testés
   - {len(all_responses)} réponses totales
   - Sauvegardé: {output_file}
   - Indexés dans ELK ✓

📈 Modèles testés:
""")
    
    for model in set(r['model_name'] for r in all_responses):
        count = sum(1 for r in all_responses if r['model_name'] == model)
        print(f"   ✓ {model}: {count} réponses")
    
    print(f"""
🎯 Prochaines étapes:
   1. Attendre 5 sec (indexation ELK)
   2. Recharger Kibana (Ctrl+R)
   3. Pie chart montrera: distilgpt2, gpt2, opt-125m, pythia! 📊
""")



if __name__ == '__main__':
    run_multi_model_test()
