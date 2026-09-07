from __future__ import annotations

import json
import os
from typing import Any

from fastapi import HTTPException
from pydantic import BaseModel, Field

from agent_service import app, OLLAMA_MODEL, SESSIONS, fallback_answer
from unifers_knowledge import UNIFERS_KNOWLEDGE

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
                max_output_tokens=1800,
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
    return {
        "mode": "local_fallback",
        "results": (
            "Live prospect research requires GEMINI_API_KEY for Google Search. "
            "The local agent is still working, but it will not fabricate company or contact data. "
            "Use /chat for Unifers knowledge and set GEMINI_API_KEY to enable live research."
        ),
    }


@app.get("/capabilities")
def capabilities() -> dict[str, Any]:
    return {
        "chat": True,
        "conversation_memory": True,
        "unifers_knowledge": True,
        "local_ollama": True,
        "live_google_research": bool(GEMINI_API_KEY),
        "prospect_research": True,
        "api_docs": "/docs",
        "model": OLLAMA_MODEL,
    }
