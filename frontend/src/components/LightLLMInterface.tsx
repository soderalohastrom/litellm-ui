import { FormEvent, useState } from 'react';
import { Send, Settings, Loader } from 'lucide-react';
import { Alert, AlertDescription } from './Alert';
import ModelSelector from './ModelSelector';

type ChatMessage = {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
};

type SettingsState = {
  provider: string;
  model: string;
  temperature: number;
  maxLength: number;
  maxOutputTokens: number | null;
};

type CompletionResponse = {
  response: string;
};

const clampMaxTokens = (value: number, hardMax: number | null) => {
  const safeValue = Number.isFinite(value) ? Math.max(1, Math.floor(value)) : 1;
  return hardMax ? Math.min(safeValue, hardMax) : safeValue;
};

const LightLLMInterface = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [settings, setSettings] = useState<SettingsState>({
    provider: '',
    model: '',
    temperature: 0.7,
    maxLength: 1000,
    maxOutputTokens: null,
  });

  const [settingsOpen, setSettingsOpen] = useState(false);

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!input.trim()) return;
    if (!settings.provider || !settings.model) {
      setError('Choose a provider and model before sending a message.');
      return;
    }

    const clampedMaxTokens = clampMaxTokens(settings.maxLength, settings.maxOutputTokens);
    if (clampedMaxTokens !== settings.maxLength) {
      setSettings(prev => ({
        ...prev,
        maxLength: clampedMaxTokens,
      }));
    }

    setLoading(true);
    setError(null);

    try {
      // Add user message to chat
      const newMessage: ChatMessage = {
        role: 'user',
        content: input,
        timestamp: new Date().toISOString(),
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
          max_tokens: clampedMaxTokens
        }),
      });

      if (!response.ok) {
        const errorBody = await response.json().catch(() => null);
        throw new Error(errorBody?.detail ?? 'Failed to get response from the model');
      }

      const data: CompletionResponse = await response.json();
      
      // Add assistant response to chat
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      setError('Failed to get response: ' + message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <div className="chat-card">
        <div className="chat-card__header">
          <div>
            <p className="eyebrow">Multi-provider chat</p>
            <h1>LiteLLM Chat</h1>
            <p className="subtle-text">
              Send prompts through a single UI and swap providers/models in one place.
            </p>
          </div>
          <button
            type="button"
          onClick={() => setSettingsOpen(true)}
          className="icon-button"
          aria-label="Open settings"
        >
          <Settings className="icon" />
        </button>
        </div>

        {error && (
          <Alert variant="destructive">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {settingsOpen && (
          <div className="modal-backdrop" onClick={() => setSettingsOpen(false)}>
            <div className="modal-card" onClick={event => event.stopPropagation()}>
              <div className="modal-card__header">
                <div>
                  <p className="eyebrow">Configuration</p>
                  <h2>Settings</h2>
                </div>
                <button
                  type="button"
                  onClick={() => setSettingsOpen(false)}
                  className="icon-button"
                  aria-label="Close settings"
                >
                  ✕
                </button>
              </div>

              <ModelSelector
                onModelChange={({ provider, model, suggestedMaxTokens, maxOutputTokens }) => {
                  setSettings(prev => ({
                    ...prev,
                    provider,
                    model,
                    maxLength: suggestedMaxTokens,
                    maxOutputTokens,
                  }));
                }}
              />

              <div className="field-group">
                <label htmlFor="temperature">Temperature</label>
                <input
                  id="temperature"
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={settings.temperature}
                  onChange={e =>
                    setSettings(prev => ({
                      ...prev,
                      temperature: parseFloat(e.target.value),
                    }))
                  }
                />
                <div className="field-helper">{settings.temperature.toFixed(1)}</div>
              </div>

              <div className="field-group">
                <label htmlFor="maxLength">Max tokens</label>
                <input
                  id="maxLength"
                  type="number"
                  min="1"
                  value={settings.maxLength}
                  onChange={e =>
                    setSettings(prev => ({
                      ...prev,
                      maxLength: clampMaxTokens(
                        Number.parseInt(e.target.value, 10) || 1000,
                        prev.maxOutputTokens,
                      ),
                    }))
                  }
                />
                {settings.maxOutputTokens ? (
                  <div className="field-helper">
                    Auto-clamped to the model hard max of {settings.maxOutputTokens.toLocaleString()}.
                  </div>
                ) : null}
              </div>

              <button
                type="button"
                onClick={() => setSettingsOpen(false)}
                className="primary-button"
              >
                Save settings
              </button>
            </div>
          </div>
        )}

        <div className="message-list">
          {messages.length === 0 && (
            <div className="empty-state">
              <p>No messages yet.</p>
              <span>Open settings, pick a provider/model, then start chatting.</span>
            </div>
          )}
          {messages.map((message, index) => (
            <div
              key={`${message.timestamp}-${index}`}
              className={`message-row message-row--${message.role}`}
            >
              <div className={`message-bubble message-bubble--${message.role}`}>
                <div>{message.content}</div>
                <div className="message-meta">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
          {loading && (
            <div className="loading-row">
              <Loader className="icon icon--spin" />
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="composer">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Type your message..."
            className="composer__input"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="primary-button composer__submit"
          >
            <Send className="icon" />
          </button>
        </form>

        <div className="footer-note">
          <span>
            Active target:{' '}
            {settings.provider && settings.model
              ? `${settings.provider} / ${settings.model}`
              : 'not configured'}
          </span>
          {settings.maxOutputTokens ? (
            <span>{` · suggested ${settings.maxLength.toLocaleString()} / hard max ${settings.maxOutputTokens.toLocaleString()} tokens`}</span>
          ) : null}
        </div>
      </div>
    </div>
  );
};

export default LightLLMInterface;
