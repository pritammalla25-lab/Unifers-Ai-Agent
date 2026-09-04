import streamlit as st
from google import genai
from google.genai import types
from unifers_knowledge import UNIFERS_KNOWLEDGE

st.set_page_config(page_title="Unifers AI", page_icon="U", layout="wide", initial_sidebar_state="expanded")

MODEL = "gemini-3.5-flash-lite"

SYSTEM_INSTRUCTION = """
You are Unifers AI, the intelligent B2B Sales Intelligence and Prospecting Agent for Unifers.ai.

Answer the user's actual question first. Do not give generic sales advice when the user asks about a specific Unifers product. Use the supplied Unifers knowledge as the source of truth for Unifers specific claims. If current information is needed, web search may be used only for requests that clearly need current or external information.

Core philosophy: Find -> Understand -> Verify -> Score -> Recommend -> Act -> Learn.

Help with ICP definition, company discovery, decision makers, enrichment, verification, buying signals, prospect scoring, company intelligence, outreach, campaign quality, CRM intelligence and next best actions when the required data is available.

Never invent pricing, customers, features, integrations, people, emails, phone numbers, funding, job titles, buying signals, technology usage, personal information or completed actions. If a field is unavailable, say: I don't have verified information for this field.

Separate verified facts from inference. Buying signals can suggest relevance but do not prove purchase intent. Do not claim an action was sent or completed unless a connected system confirms it.

For simple product questions, answer directly in 3 to 6 short paragraphs or bullets. For comparisons, use a concise table. For prospecting tasks, explain ICP fit, relevance, timing and confidence. If the user's strategy is weak, say so and improve it.

Stay focused on Unifers. For unrelated questions, answer briefly and redirect to Unifers.

UNIFERS KNOWLEDGE:
""" + str(UNIFERS_KNOWLEDGE)


def get_client():
    key = st.secrets.get("GEMINI_API_KEY", "")
    return genai.Client(api_key=key) if key else None


def needs_web(question):
    q = question.lower()
    words = ["latest", "current", "today", "recent", "news", "research", "website", "who is", "how many", "funding"]
    return any(word in q for word in words)


def ask_gemini(client, messages, use_web=False):
    contents = []
    for message in messages:
        role = "user" if message["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=message["content"])]))
    config_args = {
        "system_instruction": SYSTEM_INSTRUCTION,
        "max_output_tokens": 1400,
    }
    if use_web:
        config_args["tools"] = [types.Tool(google_search=types.GoogleSearch())]
    response = client.models.generate_content(model=MODEL, contents=contents, config=types.GenerateContentConfig(**config_args))
    return response.text


def local_answer(question):
    q = question.lower()
    if "what does unifers" in q or "what is unifers" in q:
        return "Unifers.ai is a sales intelligence and prospecting platform focused on helping revenue teams find relevant prospects, enrich data, verify information, identify buying signals and act on qualified opportunities.\n\nIts product portfolio includes Data Enrichment, LinkedIn Extension, LinkedIn Contact Finder, APIs, Email Deliverability and Email Warmup.\n\nThe goal is not simply to generate more contacts. The focus is on helping teams find the right prospects, understand why they matter, determine why now and choose the next action."
    if "products" in q and "unifers" in q:
        return "Unifers currently has these product areas in the available knowledge base:\n\n1. **Data Enrichment** for enriching incomplete prospect and company information.\n2. **LinkedIn Extension** for browser based LinkedIn prospect workflows.\n3. **LinkedIn Contact Finder** for finding contact information associated with LinkedIn prospects.\n4. **APIs** for programmatic prospect and contact data workflows.\n5. **Email Deliverability** for outbound email delivery quality.\n6. **Email Warmup** for sender reputation and outbound email readiness."
    if "data enrichment" in q:
        return "**Unifers Data Enrichment** is designed to enrich incomplete prospect and company information with additional data fields.\n\nFor a sales team, the value is better prospect context and more complete records before qualification or outreach.\n\nI do not have verified information in the current knowledge base for every available enrichment field, pricing tier or coverage limit, so I would not invent those details."
    if "linkedin contact finder" in q:
        return "**LinkedIn Contact Finder** is focused on finding contact information associated with LinkedIn prospects.\n\nIt is most relevant when a sales workflow starts with a LinkedIn prospect and needs additional contact information for outreach.\n\nI do not have verified information for specific coverage, pricing or individual contact fields beyond this description."
    if "api" in q or "apis" in q:
        return "Yes. Unifers has an **APIs** product area for programmatic prospect and contact data workflows. The available knowledge describes LinkedIn profile enrichment, verified contact information, verification, webhooks and SDK support.\n\nIf you want, I can also explain where the API fits compared with the LinkedIn tools."
    if "email warmup" in q:
        return "**Email Warmup** is focused on establishing and maintaining sender reputation before or during outbound email activity. It is relevant when a team is preparing or scaling outbound email and wants to improve sending readiness."
    if "deliverability" in q:
        return "**Email Deliverability** is focused on improving the likelihood that outbound email reaches the intended inbox. It is relevant to teams that care about the quality and reliability of outbound email delivery."
    if "linkedin extension" in q:
        return "**LinkedIn Extension** is a browser based workflow for working with LinkedIn prospect information. It is relevant when LinkedIn is part of the prospect discovery or research workflow."
    return None


def followups(question, answer):
    q = question.lower()
    if "product" in q or "what does" in q or "what is unifers" in q:
        return ["What products does Unifers offer?", "Which Unifers product is best for contact enrichment?", "How can Unifers help a sales team?"]
    if "data enrichment" in q:
        return ["What data can Unifers enrich?", "How does Data Enrichment fit into prospecting?", "Compare Data Enrichment with LinkedIn Contact Finder"]
    if "linkedin contact" in q:
        return ["How does LinkedIn Contact Finder work?", "Compare it with Data Enrichment", "What can I do after finding a contact?"]
    if "api" in q:
        return ["What does the Unifers API provide?", "Who should use the Unifers API?", "Compare APIs with the LinkedIn Extension"]
    if "email" in q or "warmup" in q or "deliverability" in q:
        return ["What is Email Warmup?", "What is Email Deliverability?", "How are Warmup and Deliverability different?"]
    return ["What products does Unifers offer?", "How does Unifers help sales teams?", "What information do you need to find prospects?"]


if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #f8fafc; }
[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1080px; padding-top: 1.5rem; padding-bottom: 8rem; }
.hero { text-align:center; padding: 4rem 1rem 2.5rem; }
.logo { width:58px; height:58px; display:flex; align-items:center; justify-content:center; margin:0 auto 18px; border-radius:18px; background:#111827; color:#fff; font-weight:800; font-size:26px; box-shadow:0 12px 30px rgba(17,24,39,.14); }
.hero h1 { margin:0; font-size:3rem; letter-spacing:-2px; color:#111827; }
.hero p { margin-top:10px; color:#64748b; font-size:1.05rem; }
.feature { background:#fff; border:1px solid #e2e8f0; border-radius:20px; padding:22px; min-height:132px; box-shadow:0 5px 20px rgba(15,23,42,.04); }
.feature b { color:#111827; font-size:1rem; }
.feature span { display:block; margin-top:8px; color:#64748b; font-size:.9rem; line-height:1.5; }
.follow-title { color:#64748b; font-size:.82rem; margin:16px 0 8px; }
[data-testid="stChatMessage"] { border-radius:20px; margin-bottom:10px; }
[data-testid="stSidebar"] { background:#fff; border-right:1px solid #e2e8f0; }
[data-testid="stSidebar"] .block-container { padding-top:1.2rem; }
div.stButton > button { border-radius:12px; border:1px solid #e2e8f0; background:#fff; text-align:left; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Unifers AI")
    st.caption("Sales Intelligence Assistant")
    st.divider()
    st.markdown("### Explore Unifers")
    st.caption("Products, APIs, enrichment, LinkedIn workflows, email infrastructure and sales intelligence.")
    st.divider()
    if st.button("What does Unifers do?", use_container_width=True, key="side_company"):
        st.session_state.pending_prompt = "What does Unifers do?"
        st.rerun()
    if st.button("Explore products", use_container_width=True, key="side_products"):
        st.session_state.pending_prompt = "What products does Unifers offer?"
        st.rerun()
    if st.button("Understand Data Enrichment", use_container_width=True, key="side_enrichment"):
        st.session_state.pending_prompt = "Explain Unifers Data Enrichment"
        st.rerun()
    if st.button("Explore APIs", use_container_width=True, key="side_api"):
        st.session_state.pending_prompt = "Does Unifers provide APIs?"
        st.rerun()
    st.divider()
    if st.button("New conversation", use_container_width=True, key="new_chat"):
        st.session_state.messages = []
        st.session_state.pending_prompt = None
        st.rerun()
    st.caption("AI answers are grounded in the available Unifers knowledge.")

if not st.session_state.messages:
    st.markdown("<div class='hero'><div class='logo'>U</div><h1>Unifers AI</h1><p>Your intelligent assistant for Unifers products and sales intelligence</p></div>", unsafe_allow_html=True)
    cols = st.columns(3)
    features = [
        ("Understand Unifers", "Get clear answers about products, capabilities and use cases."),
        ("Find better prospects", "Build ICPs, evaluate buying signals and identify relevant decision makers."),
        ("Take the next step", "Get recommendations for research, outreach and sales actions."),
    ]
    for col, item in zip(cols, features):
        with col:
            st.markdown(f"<div class='feature'><b>{item[0]}</b><span>{item[1]}</span></div>", unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("followups"):
            st.markdown("<div class='follow-title'>Continue the conversation</div>", unsafe_allow_html=True)
            follow_cols = st.columns(len(message["followups"]))
            for index, option in enumerate(message["followups"]):
                with follow_cols[index]:
                    if st.button(option, key=f"follow_{message['id']}_{index}", use_container_width=True):
                        st.session_state.pending_prompt = option
                        st.rerun()

prompt = st.chat_input("Ask anything about Unifers...")
active_prompt = prompt or st.session_state.pending_prompt
st.session_state.pending_prompt = None

if active_prompt:
    st.session_state.messages.append({"role":"user", "content":active_prompt, "id":len(st.session_state.messages)})
    with st.chat_message("user"):
        st.markdown(active_prompt)
    with st.chat_message("assistant"):
        answer = None
        local = local_answer(active_prompt)
        client = get_client()
        if client:
            try:
                with st.spinner("Thinking..."):
                    answer = ask_gemini(client, st.session_state.messages, use_web=needs_web(active_prompt))
            except Exception:
                answer = local
        else:
            answer = local
        if not answer:
            answer = "I can help with Unifers products, APIs, enrichment, LinkedIn workflows, email infrastructure, prospecting, buying signals, scoring and outreach. Tell me what you want to know, and I will answer from the available Unifers knowledge."
        st.markdown(answer)
        suggestions = followups(active_prompt, answer)
        message_id = len(st.session_state.messages)
        st.session_state.messages.append({"role":"assistant", "content":answer, "followups":suggestions, "id":message_id})
        st.markdown("<div class='follow-title'>Continue the conversation</div>", unsafe_allow_html=True)
        follow_cols = st.columns(len(suggestions))
        for index, option in enumerate(suggestions):
            with follow_cols[index]:
                if st.button(option, key=f"new_follow_{message_id}_{index}", use_container_width=True):
                    st.session_state.pending_prompt = option
                    st.rerun()
