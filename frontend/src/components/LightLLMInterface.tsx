import React, { useState, useEffect } from 'react';
import { Send, Settings, Loader } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import ModelSelector from './ModelSelector';

const LightLLMInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [settings, setSettings] = useState({
    provider: '',
    model: '',
    temperature: 0.7,
    maxLength: 1000
  });
  
  const [settingsOpen, setSettingsOpen] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    setLoading(true);
    setError(null);

    try {
      // Add user message to chat
      const newMessage = {
        role: 'user',
        content: input,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, newMessage]);
      setInput('');

      // Make API call
      const response = await fetch('/api/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          provider: settings.provider,
          model: settings.model,
          messages: [...messages, newMessage].map(msg => ({
            role: msg.role,
            content: msg.content
          })),
          temperature: settings.temperature,
          max_tokens: settings.maxLength
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response from the model');
      }

      const data = await response.json();
      
      // Add assistant response to chat
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toISOString()
      }]);
    } catch (err) {
      setError('Failed to get response: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto p-4">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">LightLLM Chat</h1>
        <button 
          onClick={() => setSettingsOpen(true)}
          className="p-2 rounded hover:bg-gray-100"
        >
          <Settings className="w-6 h-6" />
        </button>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive" className="mb-4">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Settings Modal */}
      {settingsOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-6 rounded-lg w-96">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Settings</h2>
              <button
                onClick={() => setSettingsOpen(false)}
                className="p-1 hover:bg-gray-100 rounded"
              >
                ✕
              </button>
            </div>
            
            <ModelSelector
              onModelChange={({ provider, model }) => {
                setSettings(prev => ({
                  ...prev,
                  provider,
                  model
                }));
              }}
            />
            
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Temperature
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={settings.temperature}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  temperature: parseFloat(e.target.value)
                }))}
                className="w-full"
              />
              <div className="text-sm text-gray-500 text-center">
                {settings.temperature}
              </div>
            </div>
            
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Length
              </label>
              <input
                type="number"
                value={settings.maxLength}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  maxLength: parseInt(e.target.value)
                }))}
                className="w-full p-2 border rounded"
              />
            </div>
            
            <button
              onClick={() => setSettingsOpen(false)}
              className="mt-6 w-full bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
            >
              Save Settings
            </button>
          </div>
        </div>
      )}

      {/* Chat Messages */}
      <div className="flex-1 overflow-auto mb-4 space-y-4 p-4 border rounded-lg">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            <div
              className={`max-w-3/4 p-3 rounded-lg ${
                message.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100'
              }`}
            >
              {message.content}
              <div className="text-xs mt-1 opacity-70">
                {new Date(message.timestamp).toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-center items-center">
            <Loader className="w-6 h-6 animate-spin" />
          </div>
        )}
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          className="flex-1 p-2 border rounded"
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="p-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
        >
          <Send className="w-6 h-6" />
        </button>
      </form>
    </div>
  );
};

export default LightLLMInterface;