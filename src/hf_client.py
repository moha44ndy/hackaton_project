"""
Hugging Face Client - Integration with HF models (Llama, Mistral, etc.)

Supports:
- Local inference (via transformers)
- Remote inference (via HF Inference API)
- Model listing and information
"""

import logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod


class LLMClientBase(ABC):
    """Base class for LLM clients"""
    
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.logger = logging.getLogger(__name__)
    
    @abstractmethod
    def generate_response(self, prompt: str, max_tokens: int = 512, **kwargs) -> str:
        """Generate response from model"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        pass


class HuggingFaceLocalClient(LLMClientBase):
    """
    Local Hugging Face client using transformers library
    
    Requires: pip install transformers torch
    """
    
    def __init__(self, model_id: str, device: str = "cpu"):
        """
        Initialize local HF client
        
        Args:
            model_id: HF model ID (e.g., "meta-llama/Llama-2-7b-chat-hf")
            device: "cpu" or "cuda"
        """
        super().__init__(model_id)
        self.device = device
        self.pipeline = None
        self.tokenizer = None
        
        try:
            from transformers import pipeline, AutoTokenizer
            
            self.logger.info(f"🤗 Loading model: {model_id}")
            
            # Initialize tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(model_id)
            
            # Initialize pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=model_id,
                device=0 if device == "cuda" else -1,
                torch_dtype="auto" if device == "cuda" else None,
                model_kwargs={"load_in_8bit": True} if device == "cuda" else {},
                max_new_tokens=512
            )
            
            self.logger.info(f"✅ Model loaded: {model_id}")
            
        except ImportError:
            self.logger.error("❌ transformers not installed. Install with: pip install transformers torch")
            raise
        except Exception as e:
            self.logger.error(f"❌ Error loading model {model_id}: {e}")
            raise

    def generate_response(self, prompt: str, max_tokens: int = 512, **kwargs) -> str:
        """
        Generate response from locally hosted model
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters (temperature, top_p, etc.)
            
        Returns:
            Generated response text
        """
        try:
            if not self.pipeline:
                raise RuntimeError("Model not loaded")
            
            temperature = kwargs.get("temperature", 0.7)
            top_p = kwargs.get("top_p", 0.9)
            
            outputs = self.pipeline(
                prompt,
                max_new_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                return_full_text=False
            )
            
            response_text = outputs[0]["generated_text"] if outputs else ""
            
            self.logger.debug(f"✅ Generated {len(response_text.split())} tokens")
            return response_text
            
        except Exception as e:
            self.logger.error(f"❌ Error generating response: {e}")
            raise

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about loaded model"""
        if not self.pipeline:
            return {}
        
        try:
            model_config = self.pipeline.model.config
            return {
                "model_id": self.model_id,
                "model_name": model_config.model_type,
                "max_position_embeddings": getattr(model_config, "max_position_embeddings", None),
                "hidden_size": getattr(model_config, "hidden_size", None),
                "num_parameters": self.pipeline.model.num_parameters() if hasattr(self.pipeline.model, "num_parameters") else None,
                "device": self.device,
            }
        except Exception as e:
            self.logger.error(f"❌ Error getting model info: {e}")
            return {"model_id": self.model_id, "error": str(e)}


class HuggingFaceAPIClient(LLMClientBase):
    """
    Remote Hugging Face client using HF Inference API
    
    Requires: pip install huggingface-hub requests
    API Key required from huggingface.co
    """
    
    def __init__(self, model_id: str, api_key: str):
        """
        Initialize remote HF client
        
        Args:
            model_id: HF model ID (e.g., "meta-llama/Llama-2-7b-chat-hf")
            api_key: HF API token
        """
        super().__init__(model_id)
        self.api_key = api_key
        self.api_url = f"https://api-inference.huggingface.co/models/{model_id}"
        self.session = None
        
        try:
            import requests
            self.session = requests.Session()
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
            
            # Test connection
            response = self.session.get(self.api_url, timeout=5)
            if response.status_code != 200:
                self.logger.warning(f"⚠️ Model may not be available: {response.status_code}")
            
            self.logger.info(f"✅ Connected to HF API for {model_id}")
            
        except ImportError:
            self.logger.error("❌ requests not installed. Install with: pip install requests")
            raise
        except Exception as e:
            self.logger.error(f"❌ Error connecting to HF API: {e}")
            raise

    def generate_response(self, prompt: str, max_tokens: int = 512, **kwargs) -> str:
        """
        Generate response using HF Inference API
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Generated response text
        """
        try:
            temperature = kwargs.get("temperature", 0.7)
            top_p = kwargs.get("top_p", 0.9)
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "top_p": top_p,
                }
            }
            
            response = self.session.post(
                self.api_url,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                raise RuntimeError(f"API error: {response.status_code} - {response.text}")
            
            result = response.json()
            
            # Handle different response formats
            if isinstance(result, list) and len(result) > 0:
                response_text = result[0].get("generated_text", "")
            else:
                response_text = str(result)
            
            self.logger.debug(f"✅ Generated response via HF API")
            return response_text
            
        except Exception as e:
            self.logger.error(f"❌ Error generating response: {e}")
            raise

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about remote model"""
        try:
            response = self.session.get(f"{self.api_url}/overview", timeout=10)
            
            if response.status_code == 200:
                info = response.json()
                return {
                    "model_id": self.model_id,
                    "api": "huggingface",
                    "inference_api": True,
                    "info": info,
                }
            else:
                return {
                    "model_id": self.model_id,
                    "api": "huggingface",
                    "inference_api": True,
                }
        except Exception as e:
            self.logger.error(f"❌ Error getting model info: {e}")
            return {"model_id": self.model_id, "error": str(e)}


# Predefined models
HUGGINGFACE_MODELS = {
    "llama-2-7b": {
        "id": "meta-llama/Llama-2-7b-chat-hf",
        "type": "local",  # or "api"
        "description": "Meta Llama 2 7B Chat",
        "context_window": 4096,
    },
    "llama-2-13b": {
        "id": "meta-llama/Llama-2-13b-chat-hf",
        "type": "local",
        "description": "Meta Llama 2 13B Chat",
        "context_window": 4096,
    },
    "mistral-7b": {
        "id": "mistralai/Mistral-7B-Instruct-v0.1",
        "type": "local",
        "description": "Mistral 7B Instruct",
        "context_window": 8192,
    },
    "neural-chat": {
        "id": "Intel/neural-chat-7b-v3-3",
        "type": "local",
        "description": "Intel Neural Chat 7B",
        "context_window": 4096,
    },
    "zephyr": {
        "id": "mistralai/Mistral-7B-Instruct-v0.2",
        "type": "local",
        "description": "Mistral 7B Instruct (available on HF API)",
        "context_window": 8192,
    },
}


def get_hf_client(
    model_name: str,
    api_key: Optional[str] = None,
    use_api: bool = False,
    device: str = "cpu"
) -> LLMClientBase:
    """
    Factory function to get HF client
    
    Args:
        model_name: Model name (e.g., "llama-2-7b") or full ID
        api_key: HF API key (required if use_api=True)
        use_api: Use HF Inference API instead of local
        device: "cpu" or "cuda" (for local models)
        
    Returns:
        HF client instance
    """
    logger = logging.getLogger(__name__)
    
    # Resolve model ID
    if model_name in HUGGINGFACE_MODELS:
        model_id = HUGGINGFACE_MODELS[model_name]["id"]
    else:
        model_id = model_name
    
    if use_api:
        if not api_key:
            raise ValueError("API key required for HF Inference API")
        logger.info(f"🌐 Using HF Inference API for {model_id}")
        return HuggingFaceAPIClient(model_id, api_key)
    else:
        logger.info(f"💻 Using local inference for {model_id}")
        return HuggingFaceLocalClient(model_id, device=device)
