# InterviewPilot AI — Starter MVP

## Prerequisites
Python 3.11+, Node.js 20+, an OpenAI API key.

## Backend (terminal 1)
```bash
cd backend
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Windows: copy .env.example .env
# Edit .env with your API key
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Web (terminal 2)
```bash
cd frontend
npm install
npm run dev
```
Open http://127.0.0.1:5173

## Desktop (terminal 3; keep first two terminals running)
```bash
cd desktop
npm install
npm start
```

## Current capabilities
- Practice and permission-confirmed live mode
- Token-by-token LLM streaming over WebSocket
- Browser speech recognition (browser/OS dependent)
- Browser speech synthesis
- Electron desktop shell

## Not yet production-ready
- Authentication, rate limiting, persisted consent, data retention policy, audit logs
- Real-time streaming audio STT, VAD, barge-in, interruption handling
- PostgreSQL/Redis, automated evaluation, resume ingestion
- Desktop packaging, signed builds, CSP hardening, production API transport (WSS)
- Latency benchmarking and 3-second SLO validation

The microphone demo uses browser speech recognition and only submits after recognition completes. It is not a continuous low-latency voice streaming implementation. Live mode consent checkbox is a UI acknowledgement, not independently verified consent. Do not deploy it for real interviews without additional controls.
