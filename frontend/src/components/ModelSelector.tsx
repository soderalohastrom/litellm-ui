import React, { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle2, Loader2 } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';

const ModelSelector = ({ onModelChange }) => {
  const [providers, setProviders] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchProviders();
  }, []);

  const fetchProviders = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/providers');
      if (!response.ok) {
        throw new Error('Failed to fetch providers');
      }
      const data = await response.json();
      setProviders(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleProviderChange = async (providerId) => {
    setSelectedProvider(providerId);
    setSelectedModel('');
    
    if (providerId) {
      try {
        const response = await fetch(`/api/providers/${providerId}/models`);
        if (!response.ok) {
          throw new Error('Failed to fetch models');
        }
        const models = await response.json();
        const provider = providers.find(p => p.name === providerId);
        if (provider) {
          provider.models = models;
        }
      } catch (err) {
        setError(err.message);
      }
    }
  };

  useEffect(() => {
    if (selectedProvider && selectedModel) {
      onModelChange({
        provider: selectedProvider,
        model: selectedModel
      });
    }
  }, [selectedProvider, selectedModel, onModelChange]);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-4">
        <Loader2 className="w-6 h-6 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Provider
        </label>
        <select
          value={selectedProvider}
          onChange={(e) => handleProviderChange(e.target.value)}
          className="w-full p-2 border rounded-md bg-white"
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

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Model
        </label>
        <select
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
          className="w-full p-2 border rounded-md bg-white"
          disabled={!selectedProvider}
        >
          <option value="">Select a model</option>
          {selectedProvider && 
            providers
              .find(p => p.name === selectedProvider)
              ?.models.map((model) => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))}
        </select>
      </div>

      {selectedProvider && selectedModel && (
        <div className="flex items-center gap-2 text-sm text-green-600">
          <CheckCircle2 className="h-4 w-4" />
          <span>Provider and model selected</span>
        </div>
      )}
    </div>
  );
};

export default ModelSelector;