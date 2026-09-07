from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from typing import Dict, List
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from unifers_knowledge import UNIFERS_KNOWLEDGE

APP_NAME = "Unifers AI"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:4b")
MAX_HISTORY = 20

SYSTEM_PROMPT = f"""You are Unifers AI, a sales intelligence assistant for Unifers.ai.
Answer the user's exact question first. Use the supplied public knowledge as the source for Unifers specific facts.
Never invent pricing, customers, features, integrations, people, emails, phone numbers, funding, job titles, buying signals or completed actions.
Separate verified facts from inference. If information is not verified, say so.
For prospecting, optimize for ICP fit, relevance, timing, confidence and next action, not lead volume.
Keep answers practical, concise and easy to scan.

UNIFERS PUBLIC KNOWLEDGE:
{json.dumps(UNIFERS_KNOWLEDGE, ensure_ascii=False)}
"""

app = FastAPI(
    title=APP_NAME,
    version="1.0.0",
    description="Local first Unifers sales intelligence agent. Uses Ollama when available and a deterministic knowledge fallback when it is not.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSIONS: Dict[str, List[dict]] = {}


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    session_id: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    model: str
    suggestions: List[str] = []


def fallback_answer(question: str) -> str:
    q = question.lower().strip()
    products = UNIFERS_KNOWLEDGE["products"]
    if "what is unifers" in q or "what does unifers" in q:
        return "Unifers.ai is a sales discovery and outreach automation platform that helps revenue teams discover contacts, enrich prospect data, verify information and move from discovery to outreach. Its public product areas include " + ", ".join(products) + "."
    if "product" in q and "unifers" in q:
        return "Unifers product areas:\n\n" + "\n".join(f"• {p}" for p in products)
    if "data enrichment" in q:
        return "Data Enrichment turns partial prospect or company records into richer profiles. The public knowledge describes information such as emails, phone numbers and social links. Current pricing and exact limits are not verified here."
    if "linkedin contact finder" in q or "contact finder" in q:
        return "LinkedIn Contact Finder is designed to find verified business contact information from LinkedIn prospects. The public knowledge describes email and phone lookup, bulk enrichment and export workflows. Treat detailed coverage and marketing accuracy claims as public product claims, not independent guarantees."
    if "linkedin extension" in q:
        return "LinkedIn Extension is a browser based workflow for working with prospect information while browsing LinkedIn. It is useful when LinkedIn is part of prospect discovery and research."
    if "api" in q or "apis" in q:
        return "Unifers provides APIs for programmatic prospect and contact intelligence workflows. Publicly described capabilities include LinkedIn profile enrichment, verified contact information, REST APIs, SDK support, webhooks, OpenAPI and Swagger specifications, and a sandbox environment."
    if "warmup" in q:
        return "Email Warmup focuses on building and maintaining sender reputation for outbound email. Publicly described capabilities include automated warmup, gradual ramping, read emulation and placement monitoring."
    if "deliverability" in q:
        return "Email Deliverability focuses on outbound email infrastructure, inbox delivery and sender health. Publicly described capabilities include bounce protection, domain health monitoring, throttling, load balancing and SPF, DKIM and DMARC support."
    if "prospect" in q or "icp" in q:
        return "For better prospecting, start with a precise ICP, identify the relevant persona, find a credible timing signal, verify company and contact data, score fit and timing, then personalize the next action. More leads are not automatically better leads."
    if "next step" in q or "what should i do" in q:
        return "The next step is to verify relevance, identify the strongest current signal, decide why the prospect should care now, select the right channel, personalize the message and track the result."
    return "I can help with Unifers products, prospecting, ICP design, buying signals, enrichment, LinkedIn workflows, APIs, email infrastructure and sales next actions. Ask me a specific question and I will answer it directly."


def suggestions(question: str) -> List[str]:
    q = question.lower()
    if "prospect" in q or "icp" in q:
        return ["Build an ICP", "What buying signals should I use?", "How should I score prospects?"]
    if "api" in q:
        return ["Who should use the API?", "What does the API provide?", "Compare API and LinkedIn Extension"]
    if "linkedin" in q:
        return ["What does Contact Finder do?", "What can Unifers enrich?", "What should I verify before outreach?"]
    if "email" in q or "warmup" in q or "deliverability" in q:
        return ["Explain Email Warmup", "Explain Deliverability", "How are they different?"]
    return ["What products does Unifers offer?", "How can I find better prospects?", "What should I do next?"]


def ollama_chat(history: List[dict]) -> str | None:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history[-MAX_HISTORY:])
    payload = json.dumps({"model": OLLAMA_MODEL, "messages": messages, "stream": False, "options": {"temperature": 0.2}}).encode()
    request = urllib.request.Request(OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            data = json.loads(response.read().decode("utf-8"))
        answer = data.get("message", {}).get("content", "").strip()
        return answer or None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
        return None


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return HTML_PAGE


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": APP_NAME, "ollama_model": OLLAMA_MODEL}


@app.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest) -> ChatResponse:
    session_id = body.session_id or str(uuid4())
    history = SESSIONS.setdefault(session_id, [])
    history.append({"role": "user", "content": body.message.strip()})
    answer = ollama_chat(history)
    model = f"ollama:{OLLAMA_MODEL}" if answer else "local-knowledge-fallback"
    if not answer:
        answer = fallback_answer(body.message)
    history.append({"role": "assistant", "content": answer})
    SESSIONS[session_id] = history[-MAX_HISTORY:]
    return ChatResponse(session_id=session_id, answer=answer, model=model, suggestions=suggestions(body.message))


@app.delete("/sessions/{session_id}")
def clear_session(session_id: str) -> dict:
    SESSIONS.pop(session_id, None)
    return {"status": "cleared", "session_id": session_id}


HTML_PAGE = r'''<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Unifers AI</title>
<style>
:root{font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif;color:#111827;background:#f7f9fc}*{box-sizing:border-box}body{margin:0}.shell{max-width:1050px;margin:auto;min-height:100vh;display:flex;flex-direction:column;padding:28px 22px}.top{display:flex;align-items:center;gap:12px}.logo{width:42px;height:42px;border:1px solid #e2e7ee;border-radius:13px;padding:7px;background:white}.name{font-weight:800}.sub{font-size:12px;color:#8a94a3;margin-top:2px}.hero{text-align:center;padding:70px 10px 34px}.hero h1{font-size:52px;letter-spacing:-2.8px;margin:15px 0 8px}.hero p{color:#6b7788;margin:0}.chips{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-top:22px}.chip{border:1px solid #dce3ec;background:white;border-radius:999px;padding:10px 14px;cursor:pointer}.chat{flex:1}.msg{display:flex;margin:16px 0}.msg.user{justify-content:flex-end}.bubble{max-width:78%;padding:14px 16px;border-radius:18px;white-space:pre-wrap;line-height:1.5}.user .bubble{background:#111827;color:white}.assistant .bubble{background:white;border:1px solid #e2e7ee}.composer{position:sticky;bottom:0;background:linear-gradient(transparent,#f7f9fc 20%);padding:25px 0 5px}.box{display:flex;background:white;border:1px solid #dce3ec;border-radius:18px;padding:8px;box-shadow:0 12px 30px rgba(15,23,42,.07)}textarea{border:0;outline:0;resize:none;flex:1;padding:12px;font:inherit;min-height:46px}.send{border:0;border-radius:13px;background:#111827;color:white;padding:0 19px;cursor:pointer}.status{font-size:11px;color:#8a94a3;text-align:center;margin-top:8px}.suggestions{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0 20px}.suggestions button{border:1px solid #dce3ec;background:white;border-radius:12px;padding:8px 11px;cursor:pointer}@media(max-width:650px){.hero h1{font-size:40px}.bubble{max-width:90%}}
</style></head>
<body><main class="shell"><header class="top"><img class="logo" src="https://unifers.ai/favicon.ico"><div><div class="name">Unifers AI</div><div class="sub">Sales Intelligence Assistant</div></div></header>
<section class="hero" id="hero"><img class="logo" src="https://unifers.ai/favicon.ico"><h1>Unifers AI</h1><p>Ask about products, prospects, APIs and sales intelligence.</p><div class="chips"><button class="chip" onclick="ask('What does Unifers do?')">Understand Unifers</button><button class="chip" onclick="ask('What products does Unifers offer?')">Explore products</button><button class="chip" onclick="ask('How can I find better prospects?')">Find prospects</button></div></section>
<section class="chat" id="chat"></section><section class="composer"><div class="box"><textarea id="input" placeholder="Ask Unifers AI anything..." onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();send()}"></textarea><button class="send" onclick="send()">Send</button></div><div class="status" id="status">Local agent ready</div></section></main>
<script>
let sid=localStorage.getItem('unifers_session')||null;
function esc(s){return s.replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))}
function add(role,text,sugs=[]){const c=document.getElementById('chat');const d=document.createElement('div');d.className='msg '+role;d.innerHTML='<div class="bubble">'+esc(text)+'</div>';c.appendChild(d);if(role==='assistant'&&sugs.length){const x=document.createElement('div');x.className='suggestions';sugs.forEach(v=>{const b=document.createElement('button');b.textContent=v;b.onclick=()=>ask(v);x.appendChild(b)});c.appendChild(x)}window.scrollTo(0,document.body.scrollHeight)}
async function ask(text){document.getElementById('hero').style.display='none';document.getElementById('input').value=text;await send()}
async function send(){const el=document.getElementById('input');const text=el.value.trim();if(!text)return;el.value='';document.getElementById('hero').style.display='none';add('user',text);document.getElementById('status').textContent='Thinking...';try{const r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text,session_id:sid})});if(!r.ok)throw new Error(await r.text());const d=await r.json();sid=d.session_id;localStorage.setItem('unifers_session',sid);add('assistant',d.answer,d.suggestions);document.getElementById('status').textContent='Using '+d.model}catch(e){add('assistant','The agent could not process that request. Check the terminal for the server error.');document.getElementById('status').textContent='Connection error'}}
</script></body></html>'''
