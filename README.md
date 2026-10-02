# Ask-My-Docs

# 📚 Ask My Docs

![CI](https://github.com/SBundele/ask-my-docs/actions/workflows/ci.yml/badge.svg)

Upload your documents and ask questions about them. Answers come with the exact
passages they were based on.

**Stack:** FastAPI · LlamaIndex · PostgreSQL + pgvector · MiniLM embeddings ·
Groq LLM · React · Docker · GitHub Actions

## Run it locally

1. Copy `backend/.env.example` to `backend/.env` and add your free Groq API key.
2. Start everything:

```bash
   docker compose up -d --build
```

3. Open http://localhost:8080

## Run the tests

```bash
cd backend
pytest
```