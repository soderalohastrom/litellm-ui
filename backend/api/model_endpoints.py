# api/model_endpoints.py
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional
from pydantic import BaseModel
import litellm
from config_manager import ConfigManager, ProviderConfig

router = APIRouter()
config_manager = ConfigManager()

class ModelInfo(BaseModel):
    provider: str
    model_id: str
    display_name: Optional[str] = None

class ProviderInfo(BaseModel):
    name: str
    models: List[str]
    is_configured: bool

@router.get("/providers", response_model=List[ProviderInfo])
async def list_providers():
    """Get list of all available providers and their status"""
    providers = []
    for provider in config_manager.get_available_providers():
        config = config_manager.get_provider_config(provider)
        providers.append(ProviderInfo(
            name=provider,
            models=config.available_models if config else [],
            is_configured=config_manager.is_provider_configured(provider)
        ))
    return providers

@router.get("/providers/{provider}/models", response_model=List[str])
async def list_provider_models(provider: str):
    """Get available models for a specific provider"""
    if not config_manager.is_provider_configured(provider):
        raise HTTPException(status_code=404, detail=f"Provider {provider} not configured")
    return config_manager.get_available_models(provider)

class CompletionRequest(BaseModel):
    provider: str
    model: str
    messages: List[Dict[str, str]]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000

class CompletionResponse(BaseModel):
    response: str
    usage: Dict[str, int]

@router.post("/chat/completions", response_model=CompletionResponse)
async def create_completion(request: CompletionRequest):
    """Create a chat completion using the specified provider and model"""
    if not config_manager.is_provider_configured(request.provider):
        raise HTTPException(status_code=404, detail=f"Provider {request.provider} not configured")

    if request.model not in config_manager.get_available_models(request.provider):
        raise HTTPException(status_code=400, detail=f"Model {request.model} not available for provider {request.provider}")

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
            max_tokens=request.max_tokens,
            **credentials
        )
        
        return CompletionResponse(
            response=response.choices[0].message.content,
            usage=response.usage.dict() if response.usage else {}
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