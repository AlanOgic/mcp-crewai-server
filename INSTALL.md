# Installation Guide

## Quick Install

### 1. Clone Repository
```bash
git clone https://github.com/your-username/mcp-crewai-server.git
cd mcp-crewai-server
```

### 2. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

**Option A: Full Installation (Recommended)**
```bash
pip install -r requirements.txt
```

**Option B: Minimal Installation**
```bash
pip install -r requirements-minimal.txt
```

**Option C: Development Installation**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 4. Set Environment Variables

Copy the example environment file:
```bash
cp .env.template .env
```

Edit `.env` and add your API keys:
```bash
# For Claude models
ANTHROPIC_API_KEY=your_anthropic_api_key

# For GPT models  
OPENAI_API_KEY=your_openai_api_key

# For Groq models
GROQ_API_KEY=your_groq_api_key

# For Google Gemini
GOOGLE_API_KEY=your_google_api_key

# For web search (optional)
BRAVE_API_KEY=your_brave_search_api_key
```

### 5. Install Ollama (Optional - for local models)

**macOS:**
```bash
brew install ollama
ollama serve
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
```

**Pull some models:**
```bash
ollama pull mistral:latest
ollama pull qwen2.5-coder:32b
ollama pull codellama:7b
```

### 6. Run the Server

```bash
python main.py
```

## Requirements Files

- **`requirements.txt`**: Complete installation with all features
- **`requirements-minimal.txt`**: Basic functionality only
- **`requirements-dev.txt`**: Development tools (testing, linting, etc.)

## Supported Python Versions

- Python 3.9+
- Recommended: Python 3.13 (specified in `.python-version`)

## Supported LLM Providers

✅ **Ollama** (Local, Free)
- Any model you have installed locally
- Automatic detection of installed models

✅ **Anthropic Claude**
- claude-3-5-sonnet-20241022
- claude-3-5-haiku-20241022  
- claude-3-opus-20240229
- Real-time pricing: $0.8-$75 per million tokens

✅ **OpenAI**
- gpt-4o, gpt-4o-mini
- o1-pro, o3-mini
- gpt-4-turbo, gpt-3.5-turbo
- Real-time pricing: $0.15-$600 per million tokens

✅ **Google Gemini**
- gemini-2.0-flash
- gemini-1.5-pro, gemini-1.5-flash
- Real-time pricing: $0.1-$5 per million tokens

✅ **Groq** (Fast inference)
- llama-3.1-70b, llama-3.1-8b
- mixtral-8x7b, gemma-7b
- Real-time pricing: $0.05-$0.79 per million tokens

## Features

🔥 **Real API Models**: Shows actual available models with current pricing
📊 **Token Tracking**: Real-time token usage and cost calculation  
🦙 **Ollama Auto-Detection**: Automatically finds your installed local models
🧬 **Agent Evolution**: Autonomous agent improvement and adaptation
⚡ **Multiple Providers**: Switch between any supported LLM provider
💰 **Cost Transparency**: See exact costs before and during execution

## Troubleshooting

**Ollama Issues:**
```bash
# Check if Ollama is running
ollama ps

# Start Ollama service
ollama serve

# Check available models
ollama list
```

**API Key Issues:**
```bash
# Verify environment variables
echo $ANTHROPIC_API_KEY
echo $OPENAI_API_KEY
```

**Dependency Issues:**
```bash
# Check for conflicts
pip check

# Reinstall from scratch
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```