"""
Module pour l'interaction avec différentes API de LLMs
Support: OpenAI (GPT), Anthropic (Claude), Mistral, Hugging Face
Version compatible avec wmdp_pipeline.py
"""

import os
import time
import logging
from typing import Dict, List, Optional, Tuple
from abc import ABC, abstractmethod

# Imports conditionnels pour éviter les erreurs si packages non installés
try:
    from mistralai import Mistral
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False
    logging.warning("mistralai non installé")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("openai non installé")

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logging.warning("anthropic non installé")

try:
    from huggingface_hub import InferenceClient
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    InferenceClient = None
    logging.warning("huggingface_hub non installé")

logger = logging.getLogger(__name__)


class LLMClient(ABC):
    """Classe abstraite pour les clients LLM"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialiser le client
        
        Args:
            api_key: Clé API (optionnelle, peut être lue depuis env)
        """
        self.api_key = api_key
        self.total_tokens = 0
        self.total_calls = 0
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Tuple[str, Dict]:
        """
        Générer une réponse
        
        Args:
            prompt: Le prompt utilisateur
            system_prompt: Prompt système optionnel
            max_tokens: Nombre maximum de tokens
            temperature: Température de génération
            
        Returns:
            Tuple (réponse, métadonnées)
        """
        pass
    
    def get_stats(self) -> Dict:
        """Obtenir les statistiques d'utilisation"""
        return {
            "total_calls": self.total_calls,
            "total_tokens": self.total_tokens
        }


class MistralClient(LLMClient):
    """Client pour les modèles Mistral"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "mistral-small-latest"
    ):
        if not MISTRAL_AVAILABLE:
            raise ImportError("mistralai package non installé. Installez avec: pip install mistralai")
        
        super().__init__(api_key or os.getenv("MISTRAL_API_KEY"))
        self.model = model
        self.client = Mistral(api_key=self.api_key)
        logger.info(f"MistralClient initialisé avec le modèle {model}")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Tuple[str, Dict]:
        """Générer une réponse avec Mistral"""
        start_time = time.time()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.complete(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            self.total_calls += 1
            tokens_used = response.usage.total_tokens if hasattr(response.usage, 'total_tokens') else \
                         (response.usage.prompt_tokens + response.usage.completion_tokens)
            self.total_tokens += tokens_used
            
            latency = (time.time() - start_time) * 1000
            
            metadata = {
                "model": self.model,
                "tokens": tokens_used,
                "latency_ms": latency,
                "finish_reason": response.choices[0].finish_reason
            }
            
            return response.choices[0].message.content, metadata
            
        except Exception as e:
            logger.error(f"Erreur Mistral: {str(e)}")
            raise


class GPTClient(LLMClient):
    """Client pour les modèles GPT (OpenAI)"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4-turbo-preview"
    ):
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package non installé. Installez avec: pip install openai")
        
        super().__init__(api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.client = OpenAI(api_key=self.api_key)
        logger.info(f"GPTClient initialisé avec le modèle {model}")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Tuple[str, Dict]:
        """Générer une réponse avec GPT"""
        start_time = time.time()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            self.total_calls += 1
            self.total_tokens += response.usage.total_tokens
            
            latency = (time.time() - start_time) * 1000
            
            metadata = {
                "model": self.model,
                "tokens": response.usage.total_tokens,
                "latency_ms": latency,
                "finish_reason": response.choices[0].finish_reason
            }
            
            return response.choices[0].message.content, metadata
            
        except Exception as e:
            logger.error(f"Erreur GPT: {str(e)}")
            raise


class ClaudeClient(LLMClient):
    """Client pour Claude (Anthropic)"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022"
    ):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package non installé. Installez avec: pip install anthropic")
        
        super().__init__(api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.model = model
        self.client = Anthropic(api_key=self.api_key)
        logger.info(f"ClaudeClient initialisé avec le modèle {model}")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Tuple[str, Dict]:
        """Générer une réponse avec Claude"""
        start_time = time.time()
        
        try:
            kwargs = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            if system_prompt:
                kwargs["system"] = system_prompt
            
            response = self.client.messages.create(**kwargs)
            
            self.total_calls += 1
            self.total_tokens += response.usage.input_tokens + response.usage.output_tokens
            
            latency = (time.time() - start_time) * 1000
            
            metadata = {
                "model": self.model,
                "tokens": response.usage.input_tokens + response.usage.output_tokens,
                "latency_ms": latency,
                "stop_reason": response.stop_reason
            }
            
            return response.content[0].text, metadata
            
        except Exception as e:
            logger.error(f"Erreur Claude: {str(e)}")
            raise


class HuggingFaceClient(LLMClient):
    """Client pour les modèles Hugging Face (Inference API / Inference Endpoints)"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    ):
        if not HF_AVAILABLE or InferenceClient is None:
            raise ImportError(
                "huggingface_hub non installé. Installez avec: pip install huggingface_hub"
            )
        token = api_key or os.getenv("HUGGINGFACE_TOKEN") or os.getenv("HF_TOKEN")
        super().__init__(token)
        self.model = model
        self.client = InferenceClient(token=token)
        logger.info(f"HuggingFaceClient initialisé avec le modèle {model}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Tuple[str, Dict]:
        """Générer une réponse via l'API Hugging Face (chat_completion), avec retry sur erreurs réseau."""
        start_time = time.time()
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        max_retries = 3
        base_delay = 2.0
        last_error = None

        for attempt in range(max_retries):
            try:
                response = self.client.chat_completion(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                self.total_calls += 1
                content = response.choices[0].message.content or ""
                usage = getattr(response, "usage", None)
                if usage and hasattr(usage, "total_tokens"):
                    tokens_used = usage.total_tokens
                elif usage:
                    tokens_used = getattr(usage, "prompt_tokens", 0) + getattr(
                        usage, "completion_tokens", 0
                    )
                else:
                    tokens_used = 0
                self.total_tokens += tokens_used
                latency = (time.time() - start_time) * 1000
                finish_reason = getattr(response.choices[0], "finish_reason", "stop")
                metadata = {
                    "model": self.model,
                    "tokens": tokens_used,
                    "latency_ms": latency,
                    "finish_reason": finish_reason
                }
                return content, metadata
            except Exception as e:
                last_error = e
                # Retry sur erreurs réseau / connexion
                is_retryable = (
                    "Connection" in type(e).__name__
                    or "ProtocolError" in type(e).__name__
                    or "timeout" in str(e).lower()
                    or "aborted" in str(e).lower()
                )
                if is_retryable and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.warning(
                        f"Hugging Face tentative {attempt + 1}/{max_retries} échouée: {e}. "
                        f"Nouvelle tentative dans {delay:.0f}s..."
                    )
                    time.sleep(delay)
                else:
                    logger.error(f"Erreur Hugging Face: {str(e)}")
                    raise
        raise last_error


class LLMClientFactory:
    """Factory pour créer les clients LLM appropriés"""
    
    @staticmethod
    def create_client(
        provider: str,
        model: Optional[str] = None,
        api_key: Optional[str] = None
    ) -> LLMClient:
        """
        Créer un client LLM
        
        Args:
            provider: Fournisseur (gpt, claude, mistral)
            model: Nom du modèle spécifique (optionnel)
            api_key: Clé API (optionnel)
            
        Returns:
            Instance de LLMClient appropriée
        """
        provider = provider.lower()
        
        if provider == "gpt" or provider == "openai":
            return GPTClient(api_key=api_key, model=model or "gpt-4-turbo-preview")
        
        elif provider == "claude" or provider == "anthropic":
            return ClaudeClient(api_key=api_key, model=model or "claude-3-5-sonnet-20241022")
        
        elif provider == "mistral":
            return MistralClient(api_key=api_key, model=model or "mistral-small-latest")
        
        elif provider == "huggingface" or provider == "hf":
            return HuggingFaceClient(api_key=api_key, model=model or "meta-llama/Meta-Llama-3-8B-Instruct")
        
        else:
            raise ValueError(f"Fournisseur non supporté: {provider}")


# Configurations de modèles recommandées
MODEL_CONFIGS = {
    "mistral-small": {
        "provider": "mistral",
        "model": "mistral-small-latest",
        "max_tokens": 4096,
        "temperature": 0.7
    },
    "mistral-medium": {
        "provider": "mistral",
        "model": "mistral-medium-latest",
        "max_tokens": 4096,
        "temperature": 0.7
    },
    "gpt-4": {
        "provider": "gpt",
        "model": "gpt-4-turbo-preview",
        "max_tokens": 4096,
        "temperature": 0.7
    },
    "gpt-3.5": {
        "provider": "gpt",
        "model": "gpt-3.5-turbo",
        "max_tokens": 4096,
        "temperature": 0.7
    },
    "claude-3-opus": {
        "provider": "claude",
        "model": "claude-3-opus-20240229",
        "max_tokens": 4096,
        "temperature": 0.7
    },
    "claude-3-sonnet": {
        "provider": "claude",
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 4096,
        "temperature": 0.7
    },
    "llama-3-8b": {
        "provider": "huggingface",
        "model": "meta-llama/Meta-Llama-3-8B-Instruct",
        "max_tokens": 4096,
        "temperature": 0.7
    },
    "zephyr-7b": {
        "provider": "huggingface",
        "model": "HuggingFaceH4/zephyr-7b-beta",
        "max_tokens": 4096,
        "temperature": 0.7
    },
    "mistral-7b-hf": {
        "provider": "huggingface",
        "model": "mistralai/Mistral-7B-Instruct-v0.2",
        "max_tokens": 4096,
        "temperature": 0.7
    }
}


if __name__ == "__main__":
    # Test des clients disponibles
    print("Test des clients LLM disponibles\n")
    
    # Test Mistral si disponible
    if MISTRAL_AVAILABLE:
        try:
            print("=== Test Mistral ===")
            mistral_client = LLMClientFactory.create_client("mistral")
            response, metadata = mistral_client.generate(
                "Bonjour, peux-tu te présenter en une phrase ?",
                max_tokens=100
            )
            print(f"Réponse: {response}")
            print(f"Métadonnées: {metadata}")
            print(f"Stats: {mistral_client.get_stats()}\n")
        except Exception as e:
            print(f"Erreur Mistral: {e}\n")
    else:
        print("⚠️  Mistral non disponible (package non installé)\n")
    
    # Test Hugging Face si disponible
    if HF_AVAILABLE:
        try:
            print("=== Test Hugging Face ===")
            hf_client = LLMClientFactory.create_client("huggingface", model="HuggingFaceH4/zephyr-7b-beta")
            response, metadata = hf_client.generate(
                "Hello, say one short sentence about yourself.",
                max_tokens=80
            )
            print(f"Réponse: {response}")
            print(f"Métadonnées: {metadata}")
            print(f"Stats: {hf_client.get_stats()}\n")
        except Exception as e:
            print(f"Erreur Hugging Face: {e}\n")
    else:
        print("⚠️  Hugging Face non disponible (pip install huggingface_hub)\n")
    
    print("Tests terminés")