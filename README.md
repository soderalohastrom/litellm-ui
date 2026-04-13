# LiteLLM UI Interface

A small full-stack chat app for talking to multiple LLM providers through
LiteLLM from one web interface.

## What it does

- shows a chat UI in the browser
- lists configured providers from the backend
- lists available models for the chosen provider
- sends chat messages to LiteLLM through a FastAPI API
- keeps provider credentials in environment variables instead of frontend code

## Current architecture

```text
frontend (React + TypeScript + Vite)
  -> calls /api/providers
  -> calls /api/providers/:provider/models
  -> calls /api/chat/completions

backend (FastAPI + LiteLLM)
  -> loads provider credentials from .env
  -> validates provider/model selection
  -> forwards the request to LiteLLM
```

## Project structure

```text
litellm-ui/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   └── model_endpoints.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── config_manager.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Alert.tsx
│   │   │   ├── LightLLMInterface.tsx
│   │   │   └── ModelSelector.tsx
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── styles.css
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── .env.example
└── README.md
```

## Quick start

### 1. Configure environment variables

From the repo root:

```bash
cp .env.example .env
```

Then add at least one real provider key, for example:

```env
OPENAI_API_KEY=your-key-here
```

### 2. Start the backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Backend URLs:

- API root: `http://localhost:8000/`
- docs: `http://localhost:8000/docs`

### 3. Start the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:

- app: `http://localhost:5173`

The Vite dev server proxies `/api/*` to `http://localhost:8000`.

## Supported provider configuration

The backend currently detects providers by environment variables and exposes
hardcoded model lists for them.

Examples:

- OpenAI: `OPENAI_API_KEY`
- Anthropic: `ANTHROPIC_API_KEY`
- Azure OpenAI: `AZURE_API_KEY`, `AZURE_API_BASE`, `AZURE_API_VERSION`
- AWS Bedrock: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`
- Cohere: `COHERE_API_KEY`
- Hugging Face: `HUGGINGFACE_API_KEY`
- Replicate: `REPLICATE_API_KEY`
- Together: `TOGETHER_API_KEY`
- AI21: `AI21_API_KEY`
- Groq: `GROQ_API_KEY`
- NLP Cloud: `NLP_CLOUD_API_KEY`
- Cloudflare: `CLOUDFLARE_API_KEY`, `CLOUDFLARE_ACCOUNT_ID`
- IBM: `IBM_CLOUD_API_KEY`, `IBM_CLOUD_URL`

See `.env.example` for the current full list.

## API endpoints

### Provider endpoints

- `GET /api/providers`
- `GET /api/providers/{provider}/models`

### Chat endpoints

- `POST /api/chat/completions`
- `GET /api/health`

## Frontend notes

- built with React 18 + TypeScript
- styled with plain CSS in `frontend/src/styles.css`
- no Tailwind setup is required for the current scaffold

## Backend notes

- built with FastAPI
- uses LiteLLM async completion calls
- loads provider config at startup via `ConfigManager`

## Verification used for this scaffold

- `python3 -m compileall backend`
- frontend production build via `npm run build`
- backend import smoke test in a temporary virtualenv

## Known limitations

- no authentication or saved chat history
- no streaming responses yet
- model lists are hardcoded, not dynamically fetched from providers
- no automated test suite yet

## Future improvements

- streaming chat responses
- markdown/code rendering
- persisted conversations
- auth and multi-user support
- usage/cost tracking
- Docker and CI setup

## License

MIT
