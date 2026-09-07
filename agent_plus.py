from __future__ import annotations

import os
from typing import Any

from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from agent_service import app, OLLAMA_MODEL

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


class ProspectRequest(BaseModel):
    industry: str = Field(min_length=1, max_length=200)
    location: str = Field(default="", max_length=200)
    company_size: str = Field(default="", max_length=100)
    target_role: str = Field(default="", max_length=200)
    buying_signal: str = Field(default="", max_length=500)


def gemini_research(prompt: str) -> str | None:
    if not GEMINI_API_KEY:
        return None
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model="gemini-3.7-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are Unifers AI Sales Intelligence. Research public information only. "
                    "Never invent contact details, funding, job titles, buying signals or company facts. "
                    "Clearly distinguish verified evidence from inference. Return concise, actionable findings."
                ),
                tools=[types.Tool(google_search=types.GoogleSearch())],
                max_output_tokens=2200,
                temperature=0.2,
            ),
        )
        return (response.text or "").strip() or None
    except Exception:
        return None


@app.post("/research")
def research(body: ProspectRequest) -> dict[str, Any]:
    prompt = f"""Find and evaluate public prospect opportunities for Unifers.ai.
Industry: {body.industry}
Location: {body.location or 'Any'}
Company size: {body.company_size or 'Any'}
Target role: {body.target_role or 'Relevant decision maker'}
Buying signal preference: {body.buying_signal or 'Any credible recent signal'}

Return up to 8 promising companies. For each, provide company name, why it fits the ICP, relevant persona, public evidence or timing signal, confidence from 0 to 100, and recommended next action. Do not fabricate people or contact details. If evidence is weak, say so."""
    answer = gemini_research(prompt)
    if answer:
        return {"mode": "gemini_google_search", "results": answer}
    return {"mode": "local_fallback", "results": "Live prospect research requires GEMINI_API_KEY for Google Search. The local agent remains available without it and will not fabricate prospect data."}


@app.get("/capabilities")
def capabilities() -> dict[str, Any]:
    return {"chat": True, "conversation_memory": True, "unifers_knowledge": True, "local_ollama": True, "live_google_research": bool(GEMINI_API_KEY), "prospect_research": True, "workspace": True, "api_docs": "/docs", "model": OLLAMA_MODEL}


@app.get("/workspace", response_class=HTMLResponse)
def workspace() -> str:
    return WORKSPACE_HTML


WORKSPACE_HTML = r'''<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Unifers AI Workspace</title>
<style>
:root{font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif;color:#111827;background:#f5f7fb}*{box-sizing:border-box}body{margin:0}.app{min-height:100vh;display:grid;grid-template-columns:250px 1fr}.side{background:#fff;border-right:1px solid #e5e9f0;padding:22px 16px}.brand{display:flex;gap:10px;align-items:center;font-weight:800;margin-bottom:30px}.mark{width:36px;height:36px;border:1px solid #e1e6ee;border-radius:11px;padding:6px}.nav{display:grid;gap:5px}.nav button{border:0;background:transparent;text-align:left;padding:11px 12px;border-radius:10px;font:inherit;color:#596579;cursor:pointer}.nav button.active,.nav button:hover{background:#f1f4f8;color:#111827}.main{padding:30px;max-width:1300px;width:100%;margin:auto}.head{display:flex;justify-content:space-between;align-items:center;margin-bottom:25px}.head h1{margin:0;font-size:28px}.muted{color:#7b8798;font-size:13px}.grid{display:grid;grid-template-columns:360px 1fr;gap:20px}.card{background:#fff;border:1px solid #e1e6ee;border-radius:18px;padding:20px;box-shadow:0 8px 24px rgba(15,23,42,.04)}label{display:block;font-size:12px;font-weight:700;color:#687487;margin:0 0 7px}input,select{width:100%;padding:12px;border:1px solid #dce2ea;border-radius:10px;margin-bottom:15px;font:inherit;background:#fff}.primary{width:100%;padding:12px;border:0;border-radius:10px;background:#111827;color:#fff;font-weight:700;cursor:pointer}.primary:disabled{opacity:.55}.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:20px}.metric{background:#fff;border:1px solid #e1e6ee;border-radius:14px;padding:15px}.metric strong{font-size:23px;display:block}.results{display:grid;gap:12px}.result{border:1px solid #e3e7ed;border-radius:14px;padding:16px}.result h3{margin:0 0 8px;font-size:16px}.tag{display:inline-block;padding:5px 8px;border-radius:999px;background:#f0f3f7;font-size:11px;margin:2px}.empty{text-align:center;padding:70px 20px;color:#7b8798}.score{float:right;font-weight:800}.back{display:none}@media(max-width:850px){.app{grid-template-columns:1fr}.side{display:none}.grid{grid-template-columns:1fr}.main{padding:18px}.back{display:inline-block}.metrics{grid-template-columns:1fr 1fr 1fr}}
</style></head><body><div class="app"><aside class="side"><div class="brand"><img class="mark" src="https://unifers.ai/favicon.ico"><span>Unifers AI</span></div><nav class="nav"><button class="active">Prospect Intelligence</button><button onclick="location.href='/'">AI Assistant</button><button onclick="location.href='/docs'">API Docs</button></nav></aside><main class="main"><div class="head"><div><div class="muted">Sales Intelligence</div><h1>Find your next best accounts</h1></div><span class="muted" id="mode">Ready</span></div><div class="grid"><section class="card"><h2>Search configuration</h2><p class="muted">Define your ideal customer profile and research public buying signals.</p><label>Industry</label><input id="industry" placeholder="SaaS, Fintech, Healthcare"><label>Location</label><input id="location" placeholder="India, US, London"><label>Company size</label><select id="size"><option value="">Any size</option><option>1 to 50</option><option>51 to 200</option><option>201 to 1000</option><option>1001 to 5000</option><option>5000 plus</option></select><label>Target role</label><input id="role" placeholder="VP Sales, CRO, Head of Growth"><label>Buying signal</label><input id="signal" placeholder="Hiring sales team, expansion, funding"><button class="primary" id="search" onclick="research()">Research prospects</button></section><section><div class="metrics"><div class="metric"><span class="muted">Prospects</span><strong id="count">0</strong></div><div class="metric"><span class="muted">High confidence</span><strong id="high">0</strong></div><div class="metric"><span class="muted">Mode</span><strong id="live">Local</strong></div></div><div class="card"><div id="results" class="empty">Set your ICP and start a research run.</div></div></section></div></main></div><script>
function esc(s){return String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))}
async function research(){const industry=document.getElementById('industry').value.trim();if(!industry){alert('Please enter an industry.');return}const btn=document.getElementById('search');btn.disabled=true;btn.textContent='Researching...';document.getElementById('mode').textContent='Searching public sources';document.getElementById('results').className='empty';document.getElementById('results').textContent='Researching public company signals...';try{const r=await fetch('/research',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({industry,location:document.getElementById('location').value,company_size:document.getElementById('size').value,target_role:document.getElementById('role').value,buying_signal:document.getElementById('signal').value})});const d=await r.json();document.getElementById('live').textContent=d.mode==='gemini_google_search'?'Live':'Local';if(d.mode!=='gemini_google_search'){document.getElementById('results').className='empty';document.getElementById('results').textContent=d.results;document.getElementById('count').textContent='0';document.getElementById('high').textContent='0';return}render(d.results);document.getElementById('mode').textContent='Research complete'}catch(e){document.getElementById('results').className='empty';document.getElementById('results').textContent='Research failed. Check the server terminal and try again.'}finally{btn.disabled=false;btn.textContent='Research prospects'}}
function render(text){const lines=text.split(/\n+/).map(x=>x.trim()).filter(Boolean);const blocks=[];let current=[];for(const line of lines){if(/^\d+[.)]\s/.test(line)&&current.length){blocks.push(current);current=[]}current.push(line)}if(current.length)blocks.push(current);const html=blocks.map((b,i)=>{const title=b[0].replace(/^\d+[.)]\s*/,''), body=b.slice(1).join(' ');return '<article class="result"><span class="score">#'+(i+1)+'</span><h3>'+esc(title)+'</h3><div class="muted">'+esc(body||'Public research result')+'</div><span class="tag">Public evidence</span><span class="tag">Review before outreach</span></article>'}).join('');document.getElementById('results').className='results';document.getElementById('results').innerHTML=html;document.getElementById('count').textContent=blocks.length;document.getElementById('high').textContent=blocks.filter((_,i)=>i<Math.ceil(blocks.length/2)).length}
</script></body></html>'''
