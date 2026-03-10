"""
Script de diagnostic pour le projet WMDP
Vérifie que tout est correctement configuré
"""

import sys
import os

def check_python_version():
    """Vérifier la version de Python"""
    print("🐍 Version Python:")
    print(f"   {sys.version}")
    
    version_info = sys.version_info
    if version_info.major == 3 and version_info.minor >= 8:
        print("   ✅ Version compatible (>= 3.8)")
        return True
    else:
        print("   ❌ Version incompatible (nécessite >= 3.8)")
        return False

def check_packages():
    """Vérifier les packages installés"""
    print("\n📦 Packages installés:")
    
    packages = {
        "mistralai": "Mistral AI",
        "openai": "OpenAI",
        "anthropic": "Anthropic",
        "huggingface_hub": "Hugging Face Hub",
        "pandas": "Pandas",
        "numpy": "NumPy"
    }
    
    all_ok = True
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"   ✅ {name} ({package})")
        except ImportError:
            print(f"   ❌ {name} ({package}) - MANQUANT")
            all_ok = False
    
    return all_ok

def check_mistral_import():
    """Vérifier spécifiquement l'import Mistral"""
    print("\n🔍 Test d'import Mistral:")
    
    try:
        from mistralai import Mistral
        print("   ✅ Import principal: from mistralai import Mistral")
        
        # Tester l'ancien import qui causait l'erreur
        try:
            from mistralai.models.chat_completion import ChatMessage
            print("   ⚠️  Ancien import fonctionne (version ancienne?)")
        except (ImportError, ModuleNotFoundError):
            print("   ✅ Ancien import échoue (version récente - NORMAL)")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Erreur d'import: {e}")
        return False

def check_env_variables():
    """Vérifier les variables d'environnement"""
    print("\n🔑 Variables d'environnement:")
    
    env_vars = {
        "MISTRAL_API_KEY": "Mistral AI",
        "OPENAI_API_KEY": "OpenAI",
        "ANTHROPIC_API_KEY": "Anthropic",
        "HUGGINGFACE_TOKEN": "Hugging Face (ou HF_TOKEN)",
    }
    
    found = 0
    for var, name in env_vars.items():
        value = os.environ.get(var)
        if value:
            print(f"   ✅ {name}: {value[:10]}...")
            found += 1
        else:
            print(f"   ⚠️  {name}: NON DÉFINIE")
    
    return found > 0

def check_directories():
    """Vérifier la structure des répertoires"""
    print("\n📁 Structure du projet:")
    
    required_dirs = [
        "/app/data",
        "/app/results",
        "/app/logs"
    ]
    
    all_ok = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"   ✅ {dir_path}")
        else:
            print(f"   ❌ {dir_path} - MANQUANT")
            all_ok = False
    
    return all_ok

def suggest_fixes():
    """Suggérer des corrections"""
    print("\n" + "="*60)
    print("💡 CORRECTIONS SUGGÉRÉES")
    print("="*60)
    
    print("""
1. Pour corriger l'erreur Mistral:
   
   ❌ ANCIEN (ne marche plus):
   from mistralai.models.chat_completion import ChatMessage
   
   ✅ NOUVEAU (à utiliser):
   from mistralai import Mistral
   
   # Puis utiliser:
   client = Mistral(api_key="votre_clé")
   response = client.chat.complete(...)

2. Pour mettre à jour mistralai:
   pip install --upgrade mistralai
   
3. Pour configurer les clés API:
   - Créer un fichier .env à la racine du projet
   - Ajouter: MISTRAL_API_KEY=votre_clé_ici
   
4. Structure Docker recommandée:
   docker/
   ├── Dockerfile
   ├── docker-compose.yml
   └── .env
   
   Puis: docker compose up --build
    """)

def main():
    """Fonction principale"""
    print("="*60)
    print("DIAGNOSTIC DE L'ENVIRONNEMENT WMDP")
    print("="*60)
    
    checks = [
        ("Python", check_python_version),
        ("Packages", check_packages),
        ("Import Mistral", check_mistral_import),
        ("Variables ENV", check_env_variables),
        ("Répertoires", check_directories)
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n❌ Erreur lors de {name}: {e}")
            results[name] = False
    
    # Résumé
    print("\n" + "="*60)
    print("📊 RÉSUMÉ")
    print("="*60)
    
    for name, status in results.items():
        icon = "✅" if status else "❌"
        print(f"{icon} {name}")
    
    all_ok = all(results.values())
    
    if not all_ok:
        suggest_fixes()
    else:
        print("\n✅ Tout est configuré correctement!")
        print("Vous pouvez lancer: python test_mistral_api_corrected.py")
    
    return all_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)