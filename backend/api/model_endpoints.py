# api/model_endpoints.py
from fastapi import APIRouter, HTTPException
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
import litellm
from config.config_manager import ConfigManager, ProviderModel

router = APIRouter()
config_manager = ConfigManager()

class ModelInfo(BaseModel):
    id: str
    display_name: Optional[str] = None
    max_output_tokens: int
    suggested_max_tokens: int
    max_input_tokens: Optional[int] = None
    source: str


class ProviderInfo(BaseModel):
    name: str
    models: List[ModelInfo]
    is_configured: bool


def _to_model_info(model: ProviderModel) -> ModelInfo:
    return ModelInfo(
        id=model.id,
        display_name=model.display_name,
        max_output_tokens=model.max_output_tokens,
        suggested_max_tokens=model.suggested_max_tokens,
        max_input_tokens=model.max_input_tokens,
        source=model.source,
    )

@router.get("/providers", response_model=List[ProviderInfo])
async def list_providers():
    """Get list of all available providers and their status"""
    providers = []
    for provider in config_manager.get_available_providers():
        config = config_manager.get_provider_config(provider)
        providers.append(ProviderInfo(
            name=provider,
            models=[_to_model_info(model) for model in config.available_models] if config else [],
            is_configured=config_manager.is_provider_configured(provider)
        ))
    return providers

@router.get("/providers/{provider}/models", response_model=List[ModelInfo])
async def list_provider_models(provider: str):
    """Get available models for a specific provider"""
    if not config_manager.is_provider_configured(provider):
        raise HTTPException(status_code=404, detail=f"Provider {provider} not configured")
    return [_to_model_info(model) for model in config_manager.get_available_models(provider)]

class CompletionRequest(BaseModel):
    provider: str
    model: str
    messages: List[Dict[str, str]]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000

class CompletionResponse(BaseModel):
    response: str
    usage: Dict[str, Any]


def _serialize_usage(usage: Any) -> Dict[str, Any]:
    if usage is None:
        return {}
    if isinstance(usage, dict):
        return usage
    if hasattr(usage, "model_dump"):
        return usage.model_dump()
    if hasattr(usage, "dict"):
        return usage.dict()
    return {}

@router.post("/chat/completions", response_model=CompletionResponse)
async def create_completion(request: CompletionRequest):
    """Create a chat completion using the specified provider and model"""
    if not config_manager.is_provider_configured(request.provider):
        raise HTTPException(status_code=404, detail=f"Provider {request.provider} not configured")

    available_models = {
        model.id: model for model in config_manager.get_available_models(request.provider)
    }
    selected_model = available_models.get(request.model)
    if selected_model is None:
        raise HTTPException(status_code=400, detail=f"Model {request.model} not available for provider {request.provider}")

    requested_max_tokens = request.max_tokens or selected_model.suggested_max_tokens
    if requested_max_tokens < 1:
        raise HTTPException(status_code=400, detail="max_tokens must be at least 1")
    if requested_max_tokens > selected_model.max_output_tokens:
        raise HTTPException(
            status_code=400,
            detail=(
                f"max_tokens {requested_max_tokens} exceeds the selected model hard max "
                f"of {selected_model.max_output_tokens}"
            ),
        )

    try:
        # Get provider credentials
        credentials = config_manager.get_provider_credentials(request.provider)
        
        # Configure litellm for the provider
        litellm.set_verbose = True
        
        # Make the API call
        response = await litellm.acompletion(
            model=f"{request.provider}/{request.model}",
            messages=request.messages,
            temperature=request.temperature,
            max_tokens=requested_max_tokens,
            **credentials
        )
        
        return CompletionResponse(
            response=response.choices[0].message.content,
            usage=_serialize_usage(getattr(response, "usage", None))
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@router.get("/health")
async def health_check():
    """Check if the model service is healthy"""
    return {
        "status": "healthy",
        "configured_providers": config_manager.get_available_providers()
    }
