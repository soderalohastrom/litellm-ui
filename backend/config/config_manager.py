# config_manager.py
from typing import Dict, Optional, List
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from functools import lru_cache

class ProviderConfig(BaseModel):
    api_key: str
    api_base: Optional[str] = None
    api_version: Optional[str] = None
    region: Optional[str] = None
    account_id: Optional[str] = None
    available_models: List[str] = []

class ConfigManager:
    def __init__(self):
        load_dotenv()
        self.provider_configs = self._load_provider_configs()
        self._initialize_model_lists()

    def _load_provider_configs(self) -> Dict[str, ProviderConfig]:
        configs = {}
        
        # OpenAI
        if os.getenv('OPENAI_API_KEY'):
            configs['openai'] = ProviderConfig(
                api_key=os.getenv('OPENAI_API_KEY'),
                available_models=['gpt-3.5-turbo', 'gpt-4']
            )

        # Anthropic
        if os.getenv('ANTHROPIC_API_KEY'):
            configs['anthropic'] = ProviderConfig(
                api_key=os.getenv('ANTHROPIC_API_KEY'),
                available_models=['claude-instant-1', 'claude-2']
            )

        # Azure
        if os.getenv('AZURE_API_KEY'):
            configs['azure'] = ProviderConfig(
                api_key=os.getenv('AZURE_API_KEY'),
                api_base=os.getenv('AZURE_API_BASE'),
                api_version=os.getenv('AZURE_API_VERSION'),
                available_models=['azure-gpt-3.5', 'azure-gpt-4']
            )

        # AWS
        if os.getenv('AWS_ACCESS_KEY_ID'):
            configs['aws'] = ProviderConfig(
                api_key=os.getenv('AWS_ACCESS_KEY_ID'),
                api_base=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region=os.getenv('AWS_REGION'),
                available_models=['amazon.titan-text-express-v1', 'anthropic.claude-v2']
            )

        # Cohere
        if os.getenv('COHERE_API_KEY'):
            configs['cohere'] = ProviderConfig(
                api_key=os.getenv('COHERE_API_KEY'),
                available_models=['command', 'command-light']
            )

        # Other providers with simple API key
        provider_mapping = {
            'huggingface': ('HUGGINGFACE_API_KEY', ['meta-llama/Llama-2-70b-chat-hf']),
            'replicate': ('REPLICATE_API_KEY', ['replicate/llama-2-70b-chat']),
            'together': ('TOGETHER_API_KEY', [
                'togethercomputer/llama-2-70b-chat',
                'togethercomputer/falcon-40b-instruct',
                'togethercomputer/CodeLlama-34b'
            ]),
            'ai21': ('AI21_API_KEY', ['j2-ultra', 'j2-mid', 'j2-light']),
            'groq': ('GROQ_API_KEY', ['mixtral-8x7b-32768', 'llama2-70b-4096']),
            'nlpcloud': ('NLP_CLOUD_API_KEY', ['dolphin', 'chatdolphin'])
        }

        for provider, (env_key, models) in provider_mapping.items():
            if os.getenv(env_key):
                configs[provider] = ProviderConfig(
                    api_key=os.getenv(env_key),
                    available_models=models
                )

        # Special cases for providers with multiple credentials
        if os.getenv('CLOUDFLARE_API_KEY'):
            configs['cloudflare'] = ProviderConfig(
                api_key=os.getenv('CLOUDFLARE_API_KEY'),
                account_id=os.getenv('CLOUDFLARE_ACCOUNT_ID'),
                available_models=['@cf/meta/llama-2-7b-chat-int8']
            )

        if os.getenv('IBM_CLOUD_API_KEY'):
            configs['ibm'] = ProviderConfig(
                api_key=os.getenv('IBM_CLOUD_API_KEY'),
                api_base=os.getenv('IBM_CLOUD_URL'),
                available_models=['ibm/granite-13b-chat-v1']
            )

        return configs

    def _initialize_model_lists(self):
        """Ensure all providers have their available_models list initialized"""
        for config in self.provider_configs.values():
            if not config.available_models:
                config.available_models = []

    @lru_cache()
    def get_available_providers(self) -> List[str]:
        """Return list of configured providers"""
        return list(self.provider_configs.keys())

    def get_provider_config(self, provider: str) -> Optional[ProviderConfig]:
        """Get configuration for a specific provider"""
        return self.provider_configs.get(provider)

    def get_available_models(self, provider: str) -> List[str]:
        """Get available models for a specific provider"""
        config = self.get_provider_config(provider)
        return config.available_models if config else []

    def is_provider_configured(self, provider: str) -> bool:
        """Check if a provider is properly configured"""
        return provider in self.provider_configs

    def get_provider_credentials(self, provider: str) -> Dict:
        """Get credentials for a specific provider in the format expected by litellm"""
        config = self.get_provider_config(provider)
        if not config:
            return {}

        credentials = {"api_key": config.api_key}
        
        if config.api_base:
            credentials["api_base"] = config.api_base
        if config.api_version:
            credentials["api_version"] = config.api_version
        if config.region:
            credentials["region"] = config.region
        if config.account_id:
            credentials["account_id"] = config.account_id

        return credentials