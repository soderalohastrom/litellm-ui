import { useEffect, useState } from 'react';
import { AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';
import { Alert, AlertDescription } from './Alert';

type Provider = {
  name: string;
  models: ProviderModel[];
  is_configured: boolean;
};

type ProviderModel = {
  id: string;
  display_name?: string | null;
  max_output_tokens: number;
  suggested_max_tokens: number;
  max_input_tokens?: number | null;
  source: string;
};

type ModelSelectorProps = {
  onModelChange: (selection: {
    provider: string;
    model: string;
    suggestedMaxTokens: number;
    maxOutputTokens: number;
  }) => void;
};

const ModelSelector = ({ onModelChange }: ModelSelectorProps) => {
  const [providers, setProviders] = useState<Provider[]>([]);
  const [selectedProvider, setSelectedProvider] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const selectedProviderInfo = providers.find(provider => provider.name === selectedProvider);
  const selectedModelInfo = selectedProviderInfo?.models.find(model => model.id === selectedModel);

  useEffect(() => {
    void fetchProviders();
  }, []);

  const fetchProviders = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/providers');
      if (!response.ok) {
        throw new Error('Failed to fetch providers');
      }
      const data: Provider[] = await response.json();
      setProviders(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch providers');
    } finally {
      setLoading(false);
    }
  };

  const handleProviderChange = async (providerId: string) => {
    setSelectedProvider(providerId);
    setSelectedModel('');
    
    if (providerId) {
      try {
        const response = await fetch(`/api/providers/${providerId}/models`);
        if (!response.ok) {
          throw new Error('Failed to fetch models');
        }
        const models: ProviderModel[] = await response.json();
        setProviders(previousProviders =>
          previousProviders.map(provider =>
            provider.name === providerId ? { ...provider, models } : provider,
          ),
        );
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch models');
      }
    }
  };

  useEffect(() => {
    if (selectedProvider && selectedModel) {
      const selectedModelInfo = providers
        .find(provider => provider.name === selectedProvider)
        ?.models.find(model => model.id === selectedModel);

      if (selectedModelInfo) {
        onModelChange({
          provider: selectedProvider,
          model: selectedModel,
          suggestedMaxTokens: selectedModelInfo.suggested_max_tokens,
          maxOutputTokens: selectedModelInfo.max_output_tokens,
        });
      }
    }
  }, [selectedProvider, selectedModel, onModelChange]);

  if (loading) {
    return (
      <div className="loading-row">
        <Loader2 className="icon icon--spin" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="icon icon--small" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="field-group">
        <label htmlFor="provider">Provider</label>
        <select
          id="provider"
          value={selectedProvider}
          onChange={e => void handleProviderChange(e.target.value)}
          className="select-input"
        >
          <option value="">Select a provider</option>
          {providers.map((provider) => (
            <option 
              key={provider.name} 
              value={provider.name}
              disabled={!provider.is_configured}
            >
              {provider.name} {!provider.is_configured && '(Not Configured)'}
            </option>
          ))}
        </select>
      </div>

      <div className="field-group">
        <label htmlFor="model">Model</label>
        <select
          id="model"
          value={selectedModel}
          onChange={e => setSelectedModel(e.target.value)}
          className="select-input"
          disabled={!selectedProvider}
        >
          <option value="">Select a model</option>
          {selectedProvider && 
            selectedProviderInfo?.models.map((model) => (
                <option key={model.id} value={model.id}>
                  {model.display_name ?? model.id}
                </option>
              ))}
        </select>
      </div>

      {selectedModelInfo && (
        <div className="model-metadata-card">
          <div className="model-metadata-card__header">
            <strong>{selectedModelInfo.display_name ?? selectedModelInfo.id}</strong>
            <span className="metadata-pill">
              {selectedModelInfo.source.includes('api') ? 'Live' : 'Fallback'}
            </span>
          </div>
          <div className="metadata-grid">
            <div>
              <span className="metadata-label">Model ID</span>
              <span>{selectedModelInfo.id}</span>
            </div>
            <div>
              <span className="metadata-label">Suggested max</span>
              <span>{selectedModelInfo.suggested_max_tokens.toLocaleString()}</span>
            </div>
            <div>
              <span className="metadata-label">Hard max output</span>
              <span>{selectedModelInfo.max_output_tokens.toLocaleString()}</span>
            </div>
            <div>
              <span className="metadata-label">Max input</span>
              <span>
                {selectedModelInfo.max_input_tokens
                  ? selectedModelInfo.max_input_tokens.toLocaleString()
                  : 'Not surfaced'}
              </span>
            </div>
          </div>
        </div>
      )}

      {selectedProvider && selectedModel && (
        <div className="status-row">
          <CheckCircle2 className="icon icon--small" />
          <span>
            Provider and model selected
            {selectedModelInfo
              ? ` · suggested max ${selectedModelInfo.suggested_max_tokens.toLocaleString()} / hard max ${selectedModelInfo.max_output_tokens.toLocaleString()}`
              : ''}
          </span>
        </div>
      )}
    </div>
  );
};

export default ModelSelector;
