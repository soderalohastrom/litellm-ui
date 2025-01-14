# LiteLLM UI Interface

A modern web interface for interacting with multiple LLM providers through LiteLLM. This application provides a unified interface for managing different LLM providers and models, with easy configuration and extensible architecture.

## Project Overview

This project provides:
- A React-based frontend with a modern chat interface
- A FastAPI backend for LiteLLM integration
- Support for multiple LLM providers (OpenAI, Anthropic, Azure, etc.)
- Dynamic model selection based on provider
- Environment-based configuration management

### Directory Structure

```
litellm-ui/
├── backend/
│   ├── api/
│   │   ├── __init__.py          # API router initialization
│   │   └── model_endpoints.py   # Model and provider endpoints
│   ├── config/
│   │   ├── __init__.py          # Config module initialization
│   │   └── config_manager.py    # Environment and provider configuration
│   ├── main.py                  # FastAPI application entry point
│   └── requirements.txt         # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ModelSelector.tsx     # Provider/Model selection component
│   │   │   └── LightLLMInterface.tsx # Main chat interface component
│   │   └── App.tsx                   # Root React component
│   ├── package.json             # Node.js dependencies and scripts
│   └── tsconfig.json           # TypeScript configuration
├── .env.example                # Environment variables template
└── README.md                   # Project documentation
```

## Setup Instructions

### Backend Setup

1. Create and activate a Python virtual environment:
```bash
cd backend
python -m venv venv

# On Unix/macOS
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Required dependencies:
- fastapi==0.104.1
- uvicorn==0.24.0
- python-dotenv==1.0.0
- litellm==1.10.1
- pydantic==2.4.2
- python-multipart==0.0.6

3. Configure environment variables:
```bash
cp .env.example .env
```

4. Start the FastAPI server:
```bash
uvicorn main:app --reload --port 8000
```

The backend API will be available at `http://localhost:8000`

### Frontend Setup

1. Install Node.js dependencies:
```bash
cd frontend
npm install
```

Key dependencies:
- React 18
- TypeScript
- Vite
- Tailwind CSS
- Lucide React (icons)
- Radix UI components

2. Configure environment variables:
```bash
cp .env.example .env
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Environment Configuration

Edit the `.env` file with your provider credentials. Available provider configurations include:
- OpenAI (`OPENAI_API_KEY`)
- Anthropic (`ANTHROPIC_API_KEY`)
- Azure OpenAI (`AZURE_API_KEY`, `AZURE_API_BASE`, `AZURE_API_VERSION`)
- AWS Bedrock (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`)
- Cohere (`COHERE_API_KEY`)
- Hugging Face (`HUGGINGFACE_API_KEY`)
- Replicate (`REPLICATE_API_KEY`)
- Together AI (`TOGETHER_API_KEY`)
- AI21 (`AI21_API_KEY`)
- And more (see .env.example for full list)

### Development Workflow

1. Backend Development:
- API endpoints are in `backend/api/`
- Configuration management in `backend/config/`
- Add new routes to `backend/api/__init__.py`
- FastAPI automatic docs at `http://localhost:8000/docs`

2. Frontend Development:
- Components in `frontend/src/components/`
- TypeScript for type safety
- Tailwind CSS for styling
- Vite for fast development
- React Dev Tools for debugging

## Tech Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **LiteLLM**: Unified interface for multiple LLM providers
- **Pydantic**: Data validation using Python type annotations
- **python-dotenv**: Environment variable management
- **uvicorn**: ASGI server implementation

### Frontend
- **React 18**: UI library with hooks and functional components
- **TypeScript**: Static typing for JavaScript
- **Vite**: Next-generation frontend tooling
- **Tailwind CSS**: Utility-first CSS framework
- **Radix UI**: Unstyled, accessible UI components
- **Lucide React**: Beautiful and consistent icons

## Component Details

### Frontend Components

1. `LightLLMInterface.tsx`
   - Main chat interface with real-time messaging
   - Message history management with TypeScript interfaces
   - Settings modal with provider configuration
   - Comprehensive error handling and loading states
   - Responsive design with Tailwind CSS
   - Temperature and max length controls

2. `ModelSelector.tsx`
   - Dynamic provider and model selection
   - Real-time configuration status display
   - Error handling with user feedback
   - Loading states for API interactions
   - Accessible form controls
   - Type-safe event handling

## Future Improvements

1. Authentication and User Management
   - Add user authentication
   - Implement role-based access control
   - Save user preferences and chat history

2. Enhanced Chat Features
   - Message threading
   - Code syntax highlighting
   - File upload/download support
   - Markdown rendering

3. Provider Management
   - Provider usage analytics
   - Cost tracking
   - Rate limiting
   - Quota management

4. UI Enhancements
   - Dark mode support
   - Customizable themes
   - Mobile optimization
   - Keyboard shortcuts

5. Performance Optimizations
   - Message streaming
   - Response caching
   - Load balancing
   - Connection pooling

6. Development Features
   - Test coverage
   - CI/CD pipeline
   - Docker support
   - Monitoring and logging

## API Endpoints

### Provider Management
- `GET /api/providers` - List available providers
- `GET /api/providers/{provider}/models` - List models for provider

### Chat
- `POST /api/chat/completions` - Create chat completion
- `GET /api/health` - Health check endpoint

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

---

*Note: This is a starter template and may need modifications based on specific requirements and use cases.*