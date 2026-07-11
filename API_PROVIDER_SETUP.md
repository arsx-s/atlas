# Atlas API Provider Setup

## Supported Provider Contracts

- OpenAI
- Anthropic
- Google Gemini
- Ollama
- DeepSeek
- Tavily
- Brave Search

## Environment Variables

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GOOGLE_API_KEY`
- `DEEPSEEK_API_KEY`
- `OLLAMA_BASE_URL`
- `TAVILY_API_KEY`
- `BRAVE_API_KEY`
- `ATLAS_RUNTIME_MODE`
- `ATLAS_LOCAL_MODE_ENABLED`

## Notes

- Provider routing is controlled by the backend configuration layer.
- Local mode should prefer Ollama and local embeddings.
- Cloud mode should prefer remote providers with explicit API keys.
