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
api_key = os.getenv("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=api_key) if api_key else None

@app.get('/health')
def health():
    return {'status': 'ok'}
def get_demo_answer(question):
    q = question.lower()

    if 'python' in q:
        return (
            "Python is a high-level programming language. "
            "It is used for web development, automation, "
            "data science, and artificial intelligence.\n\n"
            "Interview Tip: Mention Python's readability "
            "and give a practical example."
        )
    elif 'react' in q:
        return (
            "React is a JavaScript library used to build "
            "interactive user interfaces.\n\n"
            "Interview Tip: Explain components, props, and state."
        )
    elif 'javascript' in q:
        return (
            "JavaScript is a programming language used "
            "to make websites interactive.\n\n"
            "Interview Tip: Explain how JavaScript works "
            "with HTML and CSS."
        )
    elif 'html' in q:
        return (
            "HTML stands for HyperText Markup Language. "
            "It is used to structure web pages.\n\n"
            "Interview Tip: Explain HTML tags and elements."
        )
    elif 'css' in q:
        return (
            "CSS stands for Cascading Style Sheets. "
            "It is used to style HTML web pages, "
            "including colors, fonts, and layouts.\n\n"
            "Interview Tip: Explain CSS selectors, "
            "Flexbox, and Grid."
        )
    elif 'sql' in q:
        return (
            "SQL stands for Structured Query Language. "
            "It is used to store, retrieve, and manage "
            "data in relational databases.\n\n"
            "Interview Tip: Explain SELECT, INSERT, "
            "UPDATE, DELETE, and JOIN."
        )    
    elif 'yourself' in q or 'introduce' in q:
        return (
            "Sample Answer: My name is [Your Name]. "
            "I am interested in software development. "
            "I enjoy learning new technologies and "
            "building projects.\n\n"
            "Interview Tip: Mention your skills, "
            "projects, and career goals."
        )

    else:
        return (
            "Free Demo Mode is active!\n\n"
            "This is a sample interview response. "
            "Try asking: What is Python? "
            "What is JavaScript? "
            "Or Tell me about yourself."
        )
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
            # Free Demo Mode
            if mode == 'practice':
                answer = get_demo_answer(question)
                await ws.send_json({'type': 'token', 'text': answer})
                await ws.send_json({'type': 'done'})
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
