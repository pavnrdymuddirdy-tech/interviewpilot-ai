import os
import json
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI

load_dotenv(Path(__file__).resolve().parents[1] / '.env')
app = FastAPI(title='InterviewPilot AI')
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:5173'], allow_credentials=False, allow_methods=['*'], allow_headers=['*'])
client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY', ''))

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.websocket('/ws/interview')
async def interview(ws: WebSocket):
    # Local development only: add authentication and origin checks before deployment.
    await ws.accept()
    try:
        while True:
            payload = await ws.receive_json()
            question = str(payload.get('question', '')).strip()[:4000]
            mode = payload.get('mode', 'practice')
            consent = payload.get('consent', False)
            if not question:
                await ws.send_json({'type': 'error', 'message': 'Question is required'})
                continue
            if mode not in ('practice', 'live'):
                await ws.send_json({'type': 'error', 'message': 'Invalid mode'})
                continue
            if mode == 'live' and consent is not True:
                await ws.send_json({'type': 'error', 'message': 'Live assistance requires confirmed permission'})
                continue
            system = ('You are a helpful mock interview coach. Give concise, accurate answers and practical coaching.' if mode == 'practice' else 'You are a disclosed, permission-based interview assistant. Provide concise, accurate suggestions. Never claim to be the candidate.')
            try:
                stream = await client.chat.completions.create(
                    model=os.getenv('OPENAI_MODEL', 'gpt-4.1-mini'),
                    messages=[{'role': 'system', 'content': system}, {'role': 'user', 'content': question}],
                    stream=True, max_tokens=350,
                )
                async for part in stream:
                    token = part.choices[0].delta.content if part.choices else None
                    if token:
                        await ws.send_json({'type': 'token', 'text': token})
                await ws.send_json({'type': 'done'})
            except Exception:
                await ws.send_json({'type': 'error', 'message': 'AI request failed. Check API key, model and network.'})
    except WebSocketDisconnect:
        pass
