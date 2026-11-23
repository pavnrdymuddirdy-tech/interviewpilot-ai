import { useRef, useState } from 'react';

type SpeechResult = { results: ArrayLike<ArrayLike<{ transcript: string }>> };
type SpeechRecognizer = { lang: string; continuous: boolean; interimResults: boolean; onresult: ((event: SpeechResult) => void) | null; onerror: (() => void) | null; start: () => void; stop: () => void };
type SpeechConstructor = new () => SpeechRecognizer;

export default function App() {
  const [mode, setMode] = useState<'practice' | 'live'>('practice');
  const [consent, setConsent] = useState(false);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [status, setStatus] = useState('Ready');
  const [voiceEnabled, setVoiceEnabled] = useState(false);
  const socket = useRef<WebSocket | null>(null);
  const recognition = useRef<SpeechRecognizer | null>(null);

  function ask(text = question) {
    if (!text.trim()) return;
    if (mode === 'live' && !consent) { setStatus('Confirm interviewer permission first'); return; }
    socket.current?.close();
    setAnswer('');
    setStatus('Connecting…');
    const ws = new WebSocket('wss://interviewpilot-ai-backend-yrte.onrender.com/ws/interview');
    socket.current = ws;
    ws.onopen = () => { setStatus('AI responding…'); ws.send(JSON.stringify({ question: text, mode, consent })); };
    ws.onmessage = event => {
      const message = JSON.parse(event.data);
      if (message.type === 'token') setAnswer(previous => previous + message.text);
      if (message.type === 'done') setStatus('Completed');
      if (message.type === 'error') setStatus(message.message);
    };
    ws.onerror = () => setStatus('Connection failed — is backend running?');
  }

  function listen() {
    const browser = window as Window & { SpeechRecognition?: SpeechConstructor; webkitSpeechRecognition?: SpeechConstructor };
    const Recognition = browser.SpeechRecognition || browser.webkitSpeechRecognition;
    if (!Recognition) { setStatus('Speech recognition unavailable in this browser'); return; }
    recognition.current?.stop();
    const rec = new Recognition();
    recognition.current = rec;
    rec.lang = 'en-IN';
    rec.continuous = false;
    rec.interimResults = false;
    rec.onresult = event => { const text = event.results[0][0].transcript; setQuestion(text); setStatus('Voice captured'); };
    rec.onerror = () => setStatus('Microphone permission or recognition error');
    rec.start();
    setStatus('Listening…');
  }

  function speak() {
    if (!('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(answer);
    utterance.lang = 'en-IN';
    window.speechSynthesis.speak(utterance);
  }

  return <main className="container">
    <header><h1>InterviewPilot AI</h1><p>Practice interviews and permission-based live assistance</p></header>
    <section className="panel"><h2>Interview Mode</h2><div className="buttons">
      <button className={mode === 'practice' ? 'active' : ''} onClick={() => { setMode('practice'); socket.current?.close(); }}>Practice</button>
      <button className={mode === 'live' ? 'active' : ''} onClick={() => { setMode('live'); socket.current?.close(); }}>Permitted Live</button>
    </div>
    {mode === 'live' && <div className="notice"><strong>AI ASSISTANCE ACTIVE — DISCLOSE TO PARTICIPANTS</strong><label><input type="checkbox" checked={consent} onChange={e => setConsent(e.target.checked)} /> I confirm the interviewer permits AI assistance.</label></div>}
    </section>
    <section className="panel"><h2>Question</h2><textarea value={question} onChange={e => setQuestion(e.target.value)} placeholder="Type a question or use your microphone" rows={4}/>
      <div className="buttons"><button onClick={listen}>🎤 Voice Input</button><button className="primary" onClick={() => ask()}>Ask AI</button></div>
      <p className="status">Status: {status}</p></section>
    <section className="panel"><h2>Streaming AI Response</h2><div className="answer">{answer || 'Your AI response will appear here…'}</div><div className="buttons"><button onClick={speak} disabled={!answer}>🔊 Read Answer</button><button onClick={() => window.speechSynthesis?.cancel()}>Stop Voice</button></div></section>
    <footer>Local development demo. No production authentication or persistent history yet.</footer>
  </main>;
}
