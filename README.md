# Image Generator Agent

An Agent Stack agent that generates images from text prompts using DALL-E 3 and renders them directly in the chat UI.

## Setup

```bash
uv add openai httpx agentstack-sdk
```

Add to your `.env`:
```
OPENAI_API_KEY=your_key_here
```

## Run

```bash
uv run --env-file .env agent.py
```

## How it works

Calls DALL-E 3 with the user's prompt, uploads the result to Agent Stack's file store, and renders it in chat using the `agentstack://` URL scheme.
