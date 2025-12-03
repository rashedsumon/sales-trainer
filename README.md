# AI Sales Training Platform (Streamlit prototype)

This repository is a prototype for an AI-driven sales training platform where salespeople can practice realistic, low-latency conversations with an AI prospect (cold calls, discovery, negotiation, objection handling, closing, etc).

## Features
- Text-based and audio (upload) interactions.
- Persona-driven prospect behavior (friendly, skeptical, rushed, etc).
- Example objection set (e.g. "I’m not interested", "Send me an email", "We don’t have budget", "We already use another vendor").
- Simple scoring engine for outcome, confidence, and objection handling.
- Data downloader using `kagglehub` (as requested).
- Extendable adapters for LLM, STT, and TTS providers.

## File structure
(see project root for complete list)

## Quick start (local)
1. Ensure Python 3.11.0 is installed.
2. Create virtualenv:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
