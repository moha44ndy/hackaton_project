#!/usr/bin/env python3
"""
Script: Nettoie les réponses WMDP et les indexe dans ELK
- Supprime newlines/whitespace excessifs
- Envoie à Elasticsearch
- Met à jour les dashboards
"""

import json
import re
from pathlib import Path
from datetime import datetime
from elasticsearch import Elasticsearch
import sys

# Chemins
RESPONSES_FILE = Path(__file__).parent.parent / "results" / "wmdp_responses_20260305_225228.json"
ES_HOST = "http://localhost:9200"

def clean_response_text(text: str) -> str:
    """Nettoie les newlines et whitespace excessifs"""
    # Supprimer plus de 2 newlines consécutifs
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Supprimer les espaces excessifs
    text = re.sub(r' {2,}', ' ', text)
    # Trim
    text = text.strip()
    return text

def load_and_clean_responses() -> dict:
    """Charge et nettoie le fichier de réponses"""
    print(f"📥 Chargement: {RESPONSES_FILE}")
    
    with open(RESPONSES_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ Chargé {data['metadata']['total_responses']} réponses")
    
    # Nettoyer chaque réponse
    for resp in data['responses']:
        original_len = len(resp['response_text'])
        resp['response_text'] = clean_response_text(resp['response_text'])
        cleaned_len = len(resp['response_text'])
        reduction = ((original_len - cleaned_len) / original_len) * 100
        
        if reduction > 10:  # Afficher si réduction > 10%
            print(f"  🧹 {resp['prompt_id']}: -{reduction:.1f}% ({original_len} → {cleaned_len} chars)")
    
    return data

def index_to_elasticsearch(data: dict) -> bool:
    """Indexe les données nettoyées dans ELK"""
    try:
        es = Elasticsearch([ES_HOST])
        
        # Vérifier connexion
        if not es.ping():
            print("❌ ELK non accessible")
            return False
        
        print("✅ ELK connecté")
        
        # Index pattern
        index_name = f"wmdp-responses-{datetime.now().strftime('%Y.%m.%d')}"
        
        # Indexer chaque réponse
        success_count = 0
        for i, resp in enumerate(data['responses']):
            try:
                doc_id = f"{resp['model_name']}-{resp['prompt_id']}"
                
                # Ajouter timestamp et fields pour Kibana
                doc = {
                    **resp,
                    "@timestamp": datetime.fromisoformat(resp['timestamp']).isoformat(),
                    "model": resp['model_name'],
                    "category": resp['prompt_category'],
                    "risk_level": resp['prompt_risk_level'],
                    "response_length": len(resp['response_text']),
                }
                
                result = es.index(index=index_name, id=doc_id, document=doc)
                success_count += 1
                
                if (success_count % 5) == 0:
                    print(f"  📮 {success_count}/{len(data['responses'])} indexés...")
                    
            except Exception as e:
                print(f"⚠️  Erreur doc {resp['prompt_id']}: {e}")
        
        print(f"✅ {success_count}/{len(data['responses'])} réponses indexées dans ELK")
        print(f"   Index: {index_name}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur ELK: {e}")
        return False

def save_cleaned_responses(data: dict):
    """Sauvegarde les données nettoyées"""
    # Créer fichier nettoyé
    clean_file = RESPONSES_FILE.parent / "wmdp_responses_cleaned.json"
    
    with open(clean_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Réponses nettoyées sauvegardées: {clean_file}")

def main():
    print("\n" + "="*70)
    print("🧹 NETTOYAGE & INDEXATION RÉPONSES WMDP")
    print("="*70 + "\n")
    
    try:
        # Charger et nettoyer
        data = load_and_clean_responses()
        
        # Indexer dans ELK
        print("\n📮 Indexation dans Elasticsearch...")
        if index_to_elasticsearch(data):
            
            # Sauvegarder version nettoyée
            print("\n💾 Sauvegarde...")
            save_cleaned_responses(data)
            
            print("\n" + "="*70)
            print("✅ SUCCÈS!")
            print("="*70)
            print("\n📊 Prochaines étapes:")
            print("   1. Aller à Kibana: http://localhost:5601")
            print("   2. Créer index pattern: wmdp-responses-*")
            print("   3. Recharger le dashboard")
            print()
            return 0
        else:
            print("\n❌ Indexation échouée")
            return 1
            
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
