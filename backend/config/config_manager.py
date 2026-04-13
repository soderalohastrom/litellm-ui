# config_manager.py
from typing import Dict, Optional, List
import os
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv
from pydantic import BaseModel
from functools import lru_cache
from copy import deepcopy


class ProviderModel(BaseModel):
    id: str
    display_name: Optional[str] = None
    max_output_tokens: int
    suggested_max_tokens: int
    max_input_tokens: Optional[int] = None
    source: str = "static"

class ProviderConfig(BaseModel):
    api_key: str
    api_base: Optional[str] = None
    api_version: Optional[str] = None
    region: Optional[str] = None
    account_id: Optional[str] = None
    available_models: List[ProviderModel] = []


OPENAI_CURATED_MODELS = [
    ProviderModel(
        id="gpt-5.4",
        display_name="GPT-5.4",
        max_output_tokens=128000,
        suggested_max_tokens=8192,
        source="openai_docs",
    ),
    ProviderModel(
        id="gpt-5.4-mini",
        display_name="GPT-5.4 mini",
        max_output_tokens=128000,
        suggested_max_tokens=4096,
        source="openai_docs",
    ),
    ProviderModel(
        id="gpt-5.4-nano",
        display_name="GPT-5.4 nano",
        max_output_tokens=128000,
        suggested_max_tokens=2048,
        source="openai_docs",
    ),
    ProviderModel(
        id="gpt-4.1",
        display_name="GPT-4.1",
        max_output_tokens=32768,
        suggested_max_tokens=8192,
        max_input_tokens=1047576,
        source="openai_docs",
    ),
    ProviderModel(
        id="gpt-4o-mini",
        display_name="GPT-4o mini",
        max_output_tokens=16384,
        suggested_max_tokens=4096,
        max_input_tokens=128000,
        source="openai_docs",
    ),
]

ANTHROPIC_CURATED_MODEL_IDS = [
    "claude-sonnet-4-6",
    "claude-opus-4-6",
    "claude-sonnet-4-5-20250929",
    "claude-haiku-4-5-20251001",
    "claude-opus-4-5-20251101",
]

ANTHROPIC_FALLBACK_MODELS = [
    ProviderModel(
        id="claude-sonnet-4-6",
        display_name="Claude Sonnet 4.6",
        max_output_tokens=128000,
        suggested_max_tokens=8192,
        max_input_tokens=1000000,
        source="anthropic_api_snapshot",
    ),
    ProviderModel(
        id="claude-opus-4-6",
        display_name="Claude Opus 4.6",
        max_output_tokens=128000,
        suggested_max_tokens=8192,
        max_input_tokens=1000000,
        source="anthropic_api_snapshot",
    ),
    ProviderModel(
        id="claude-sonnet-4-5-20250929",
        display_name="Claude Sonnet 4.5",
        max_output_tokens=64000,
        suggested_max_tokens=8192,
        max_input_tokens=1000000,
        source="anthropic_api_snapshot",
    ),
    ProviderModel(
        id="claude-haiku-4-5-20251001",
        display_name="Claude Haiku 4.5",
        max_output_tokens=64000,
        suggested_max_tokens=4096,
        max_input_tokens=200000,
        source="anthropic_api_snapshot",
    ),
    ProviderModel(
        id="claude-opus-4-5-20251101",
        display_name="Claude Opus 4.5",
        max_output_tokens=64000,
        suggested_max_tokens=8192,
        max_input_tokens=200000,
        source="anthropic_api_snapshot",
    ),
]

class ConfigManager:
    def __init__(self):
        load_dotenv()
        self.provider_configs = self._load_provider_configs()
        self._initialize_model_lists()
        self._refresh_priority_provider_models()

    def _load_provider_configs(self) -> Dict[str, ProviderConfig]:
        configs = {}
        
        # OpenAI
        if os.getenv('OPENAI_API_KEY'):
            configs['openai'] = ProviderConfig(
                api_key=os.getenv('OPENAI_API_KEY'),
                available_models=deepcopy(OPENAI_CURATED_MODELS)
            )

        # Anthropic
        if os.getenv('ANTHROPIC_API_KEY'):
            configs['anthropic'] = ProviderConfig(
                api_key=os.getenv('ANTHROPIC_API_KEY'),
                available_models=deepcopy(ANTHROPIC_FALLBACK_MODELS)
            )

        # Azure
        if os.getenv('AZURE_API_KEY'):
            configs['azure'] = ProviderConfig(
                api_key=os.getenv('AZURE_API_KEY'),
                api_base=os.getenv('AZURE_API_BASE'),
                api_version=os.getenv('AZURE_API_VERSION'),
                available_models=[
                    ProviderModel(
                        id='azure-gpt-3.5',
                        display_name='Azure GPT-3.5',
                        max_output_tokens=4096,
                        suggested_max_tokens=2048,
                    ),
                    ProviderModel(
                        id='azure-gpt-4',
                        display_name='Azure GPT-4',
                        max_output_tokens=8192,
                        suggested_max_tokens=4096,
                    ),
                ]
            )

        # AWS
        if os.getenv('AWS_ACCESS_KEY_ID'):
            configs['aws'] = ProviderConfig(
                api_key=os.getenv('AWS_ACCESS_KEY_ID'),
                api_base=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region=os.getenv('AWS_REGION'),
                available_models=[
                    ProviderModel(
                        id='amazon.titan-text-express-v1',
                        display_name='Amazon Titan Text Express',
                        max_output_tokens=8192,
                        suggested_max_tokens=2048,
                    ),
                    ProviderModel(
                        id='anthropic.claude-v2',
                        display_name='Anthropic Claude v2 (Bedrock)',
                        max_output_tokens=4096,
                        suggested_max_tokens=2048,
                    ),
                ]
            )

        # Cohere
        if os.getenv('COHERE_API_KEY'):
            configs['cohere'] = ProviderConfig(
                api_key=os.getenv('COHERE_API_KEY'),
                available_models=[
                    ProviderModel(
                        id='command',
                        display_name='Cohere Command',
                        max_output_tokens=4096,
                        suggested_max_tokens=2048,
                    ),
                    ProviderModel(
                        id='command-light',
                        display_name='Cohere Command Light',
                        max_output_tokens=4096,
                        suggested_max_tokens=1024,
                    ),
                ]
            )

        # Other providers with simple API key
        provider_mapping = {
            'huggingface': ('HUGGINGFACE_API_KEY', [
                ProviderModel(
                    id='meta-llama/Llama-2-70b-chat-hf',
                    display_name='Llama 2 70B Chat',
                    max_output_tokens=4096,
                    suggested_max_tokens=2048,
                )
            ]),
            'replicate': ('REPLICATE_API_KEY', [
                ProviderModel(
                    id='replicate/llama-2-70b-chat',
                    display_name='Replicate Llama 2 70B Chat',
                    max_output_tokens=4096,
                    suggested_max_tokens=2048,
                )
            ]),
            'together': ('TOGETHER_API_KEY', [
                ProviderModel(
                    id='togethercomputer/llama-2-70b-chat',
                    display_name='Together Llama 2 70B Chat',
                    max_output_tokens=4096,
                    suggested_max_tokens=2048,
                ),
                ProviderModel(
                    id='togethercomputer/falcon-40b-instruct',
                    display_name='Together Falcon 40B Instruct',
                    max_output_tokens=4096,
                    suggested_max_tokens=2048,
                ),
                ProviderModel(
                    id='togethercomputer/CodeLlama-34b',
                    display_name='Together CodeLlama 34B',
                    max_output_tokens=4096,
                    suggested_max_tokens=2048,
                ),
            ]),
            'ai21': ('AI21_API_KEY', [
                ProviderModel(
                    id='j2-ultra',
                    display_name='AI21 J2 Ultra',
                    max_output_tokens=4096,
                    suggested_max_tokens=2048,
                ),
                ProviderModel(
                    id='j2-mid',
                    display_name='AI21 J2 Mid',
                    max_output_tokens=4096,
                    suggested_max_tokens=2048,
                ),
                ProviderModel(
                    id='j2-light',
                    display_name='AI21 J2 Light',
                    max_output_tokens=4096,
                    suggested_max_tokens=1024,
                ),
            ]),
            'groq': ('GROQ_API_KEY', [
                ProviderModel(
                    id='mixtral-8x7b-32768',
                    display_name='Groq Mixtral 8x7B',
                    max_output_tokens=32768,
                    suggested_max_tokens=4096,
                ),
                ProviderModel(
                    id='llama2-70b-4096',
                    display_name='Groq Llama2 70B',
                    max_output_tokens=4096,
                    suggested_max_tokens=2048,
                ),
            ]),
            'nlpcloud': ('NLP_CLOUD_API_KEY', [
                ProviderModel(
                    id='dolphin',
                    display_name='NLP Cloud Dolphin',
                    max_output_tokens=4096,
                    suggested_max_tokens=2048,
                ),
                ProviderModel(
                    id='chatdolphin',
                    display_name='NLP Cloud ChatDolphin',
                    max_output_tokens=4096,
                    suggested_max_tokens=2048,
                ),
            ])
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
                available_models=[
                    ProviderModel(
                        id='@cf/meta/llama-2-7b-chat-int8',
                        display_name='Cloudflare Llama 2 7B',
                        max_output_tokens=4096,
                        suggested_max_tokens=2048,
                    )
                ]
            )

        if os.getenv('IBM_CLOUD_API_KEY'):
            configs['ibm'] = ProviderConfig(
                api_key=os.getenv('IBM_CLOUD_API_KEY'),
                api_base=os.getenv('IBM_CLOUD_URL'),
                available_models=[
                    ProviderModel(
                        id='ibm/granite-13b-chat-v1',
                        display_name='IBM Granite 13B Chat',
                        max_output_tokens=4096,
                        suggested_max_tokens=2048,
                    )
                ]
            )

        return configs

    def _initialize_model_lists(self):
        """Ensure all providers have their available_models list initialized"""
        for config in self.provider_configs.values():
            if not config.available_models:
                config.available_models = []

    def _refresh_priority_provider_models(self) -> None:
        if 'openai' in self.provider_configs:
            live_openai_models = self._fetch_openai_models()
            if live_openai_models:
                self.provider_configs['openai'].available_models = live_openai_models

        if 'anthropic' in self.provider_configs:
            live_anthropic_models = self._fetch_anthropic_models()
            if live_anthropic_models:
                self.provider_configs['anthropic'].available_models = live_anthropic_models

    def _fetch_json(self, url: str, headers: Dict[str, str]) -> Dict:
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)

    def _fetch_openai_models(self) -> List[ProviderModel]:
        config = self.provider_configs.get('openai')
        if not config:
            return []

        try:
            payload = self._fetch_json(
                'https://api.openai.com/v1/models',
                {'Authorization': f'Bearer {config.api_key}'},
            )
            available_ids = {item['id'] for item in payload.get('data', [])}
            return [
                model.model_copy(update={'source': 'openai_api+docs'})
                for model in OPENAI_CURATED_MODELS
                if model.id in available_ids
            ]
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, KeyError, json.JSONDecodeError):
            return []

    def _fetch_anthropic_models(self) -> List[ProviderModel]:
        config = self.provider_configs.get('anthropic')
        if not config:
            return []

        headers = {
            'x-api-key': config.api_key,
            'anthropic-version': '2023-06-01',
        }

        try:
            payload = self._fetch_json('https://api.anthropic.com/v1/models', headers)
            available_ids = {item['id'] for item in payload.get('data', [])}
            models: List[ProviderModel] = []

            for model_id in ANTHROPIC_CURATED_MODEL_IDS:
                if model_id not in available_ids:
                    continue
                detail = self._fetch_json(f'https://api.anthropic.com/v1/models/{model_id}', headers)
                suggested_max_tokens = 4096 if 'haiku' in model_id else 8192
                models.append(
                    ProviderModel(
                        id=detail['id'],
                        display_name=detail.get('display_name'),
                        max_output_tokens=detail.get('max_tokens', 4096),
                        suggested_max_tokens=min(suggested_max_tokens, detail.get('max_tokens', suggested_max_tokens)),
                        max_input_tokens=detail.get('max_input_tokens'),
                        source='anthropic_api',
                    )
                )

            return models
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, KeyError, json.JSONDecodeError):
            return []

    @lru_cache()
    def get_available_providers(self) -> List[str]:
        """Return list of configured providers"""
        return list(self.provider_configs.keys())

    def get_provider_config(self, provider: str) -> Optional[ProviderConfig]:
        """Get configuration for a specific provider"""
        return self.provider_configs.get(provider)

    def get_available_models(self, provider: str) -> List[ProviderModel]:
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
