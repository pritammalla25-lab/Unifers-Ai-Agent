import streamlit as st
from google import genai
from google.genai import types
from unifers_knowledge import UNIFERS_KNOWLEDGE

st.set_page_config(page_title="Unifers AI", page_icon="U", layout="wide", initial_sidebar_state="expanded")

MODEL = "gemini-3.7-flash"
LOGO_URL = "https://unifers.ai/favicon.ico"

SYSTEM_INSTRUCTION = """
You are Unifers AI, a B2B sales intelligence assistant for Unifers.ai.
Answer the user's exact question first. Use the supplied knowledge for Unifers specific facts. Never invent pricing, customers, features, integrations, people, emails, phone numbers, funding, job titles, buying signals or completed actions. Clearly separate verified facts from inference. For prospecting, focus on ICP fit, relevance, timing, confidence and next action. Be concise, practical and specific.

UNIFERS KNOWLEDGE:
""" + str(UNIFERS_KNOWLEDGE)


def get_client():
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        key = ""
    return genai.Client(api_key=key) if key else None


def needs_web(question):
    q = question.lower()
    return any(x in q for x in ["latest", "current", "today", "recent", "news", "research", "funding", "pricing", "price"])


def ask_gemini(client, messages, use_web=False):
    contents = []
    for message in messages:
        role = "user" if message["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=message["content"])]))
    config = {
        "system_instruction": SYSTEM_INSTRUCTION,
        "max_output_tokens": 1400,
        "temperature": 0.35,
    }
    if use_web:
        config["tools"] = [types.Tool(google_search=types.GoogleSearch())]
    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=types.GenerateContentConfig(**config),
    )
    return response.text


def local_answer(question):
    q = question.lower()
    if "what does unifers" in q or "what is unifers" in q:
        return "### What is Unifers AI?\n\nUnifers.ai is a sales intelligence and prospecting platform that helps revenue teams find relevant prospects, enrich incomplete data, verify information, identify buying signals and act on qualified opportunities.\n\nIts product areas include Data Enrichment, LinkedIn Extension, LinkedIn Contact Finder, APIs, Email Deliverability and Email Warmup."
    if "products" in q and "unifers" in q:
        return "### Unifers product areas\n\n| Product | Main purpose |\n| --- | --- |\n| Data Enrichment | Enrich incomplete prospect and company records |\n| LinkedIn Extension | Work with prospect information from LinkedIn |\n| LinkedIn Contact Finder | Find contact information associated with LinkedIn prospects |\n| APIs | Programmatic prospect and contact data workflows |\n| Email Deliverability | Improve outbound email delivery quality |\n| Email Warmup | Build and maintain sender reputation |"
    if "find better prospects" in q or "how can i find better prospects" in q:
        return "### Finding better prospects\n\nDo not start by maximizing lead volume. Start with a clear ICP.\n\n1. Define the industry, geography, company size and business model.\n2. Identify the decision maker or strongest relevant persona.\n3. Look for evidence that the company has a current reason to care.\n4. Verify the available contact and company information.\n5. Score prospects by ICP fit, relevance, timing and confidence.\n6. Contact the highest quality opportunities first."
    if "next step" in q or "what should i do next" in q:
        return "### Recommended next step\n\n1. Verify the company and person's relevance.\n2. Identify the strongest buying or timing signal available.\n3. Decide why this prospect is worth contacting now.\n4. Choose the best channel and message.\n5. Personalize the outreach around the prospect's situation.\n6. Track the response and use the result to improve future targeting."
    if "data enrichment" in q:
        return "### Unifers Data Enrichment\n\nData Enrichment is designed to turn incomplete prospect and company information into more complete records. It gives a sales team more context before qualification and outreach. Specific pricing, limits and every supported field are not verified in the current knowledge base."
    if "linkedin contact finder" in q:
        return "### LinkedIn Contact Finder\n\nLinkedIn Contact Finder focuses on finding contact information associated with LinkedIn prospects. It is useful when LinkedIn is where you discover a prospect and you need additional contact information for outreach. Specific pricing and coverage details are not verified in the current knowledge base."
    if "api" in q or "apis" in q:
        return "### Unifers APIs\n\nUnifers provides APIs for programmatic prospect and contact data workflows. The available knowledge describes LinkedIn profile enrichment, verified contact information, verification, webhooks and SDK support. The API is most relevant when you want to put prospect intelligence directly into your own application or workflow."
    if "email warmup" in q:
        return "### Email Warmup\n\nEmail Warmup focuses on establishing and maintaining sender reputation before or during outbound email activity. It is relevant when a team is preparing or scaling outbound email."
    if "deliverability" in q:
        return "### Email Deliverability\n\nEmail Deliverability focuses on improving the likelihood that outbound email reaches the intended inbox. It is relevant when a sales team wants stronger outbound email delivery and sender health."
    if "linkedin extension" in q:
        return "### LinkedIn Extension\n\nLinkedIn Extension is a browser based workflow for working with LinkedIn prospect information. It is relevant when LinkedIn is part of prospect discovery or research."
    return "I can help with Unifers products, prospect discovery, ICPs, buying signals, scoring, enrichment, LinkedIn workflows, APIs, email infrastructure and next best actions. Ask me a specific question and I will answer it directly."


def followups(question):
    q = question.lower()
    if "prospect" in q or "icp" in q:
        return ["Build an ICP for my business", "What buying signals should I look for?", "How should I score prospects?"]
    if "next step" in q or "outreach" in q or "action" in q:
        return ["Create a personalized outreach message", "How do I prioritize prospects?", "What should I verify before outreach?"]
    if "data enrichment" in q:
        return ["What data can Unifers enrich?", "Compare Data Enrichment with Contact Finder", "What should I do after enrichment?"]
    if "api" in q:
        return ["Who should use the Unifers API?", "What does the API provide?", "Compare APIs with the LinkedIn Extension"]
    if "email" in q or "warmup" in q or "deliverability" in q:
        return ["What is Email Warmup?", "What is Email Deliverability?", "How are Warmup and Deliverability different?"]
    return ["What products does Unifers offer?", "How can I find better prospects?", "What should I do next after finding a prospect?"]


def submit_prompt(text):
    st.session_state.pending_prompt = text
    st.rerun()


if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] { background:#f8fafc; }
    [data-testid="stHeader"] { background:transparent; }
    .block-container { max-width:1120px; padding-top:18px; padding-bottom:110px; }
    [data-testid="stSidebar"] { background:#ffffff; border-right:1px solid #e7ebf0; }
    [data-testid="stSidebar"] .block-container { padding-top:22px; }
    .brand { display:flex; align-items:center; gap:10px; margin-bottom:20px; }
    .brand img { width:38px; height:38px; border:1px solid #e3e8ef; border-radius:11px; padding:6px; background:white; }
    .brand-name { font-weight:750; font-size:1rem; color:#111827; }
    .brand-sub { color:#7b8798; font-size:.72rem; margin-top:2px; }
    .hero { text-align:center; padding:58px 12px 35px; }
    .hero img { width:68px; height:68px; padding:10px; border-radius:20px; background:#fff; border:1px solid #e0e6ee; box-shadow:0 12px 34px rgba(15,23,42,.08); }
    .hero h1 { color:#111827; font-size:3.15rem; letter-spacing:-2.4px; margin:17px 0 8px; font-weight:780; }
    .hero p { color:#687588; font-size:1rem; margin:0; }
    .hero-note { color:#98a2b1; font-size:.78rem; margin-top:9px; }
    .card-wrap button { min-height:154px !important; border-radius:20px !important; border:1px solid #dfe5ed !important; background:#fff !important; color:#111827 !important; box-shadow:0 7px 24px rgba(15,23,42,.035) !important; padding:22px !important; text-align:left !important; white-space:pre-wrap !important; }
    .card-wrap button:hover { border-color:#b9c5d5 !important; box-shadow:0 14px 34px rgba(15,23,42,.09) !important; }
    .chat-label { color:#8a95a5; font-size:.78rem; margin:20px 0 8px; }
    [data-testid="stChatMessage"] { border-radius:18px; }
    div.stButton > button { border-radius:12px; }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown(
        f"<div class='brand'><img src='{LOGO_URL}'><div><div class='brand-name'>Unifers AI</div><div class='brand-sub'>Sales Intelligence Assistant</div></div></div>",
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown("### Start here")
    st.caption("Choose a workflow or ask your own question.")
    for title, question, key in [
        ("Understand Unifers", "What does Unifers do?", "s1"),
        ("Find better prospects", "How can I find better prospects with Unifers?", "s2"),
        ("Take the next step", "What should I do next after finding a qualified prospect?", "s3"),
        ("Explore products", "What products does Unifers offer?", "s4"),
        ("Explore APIs", "Does Unifers provide APIs?", "s5"),
    ]:
        if st.button(title, use_container_width=True, key=key):
            submit_prompt(question)
    st.divider()
    if st.button("New conversation", use_container_width=True, key="new"):
        st.session_state.messages = []
        st.session_state.pending_prompt = None
        st.rerun()

if not st.session_state.messages:
    st.markdown(
        f"<div class='hero'><img src='{LOGO_URL}'><h1>Unifers AI</h1><p>Your intelligent assistant for products, prospects and sales intelligence</p><div class='hero-note'>Choose a workflow below or ask anything about Unifers</div></div>",
        unsafe_allow_html=True,
    )
    cards = [
        ("Understand Unifers", "Get clear answers about products, capabilities and use cases.", "What does Unifers do?", "c1"),
        ("Find better prospects", "Build ICPs, evaluate buying signals and identify relevant decision makers.", "How can I find better prospects with Unifers?", "c2"),
        ("Take the next step", "Get recommendations for research, outreach and sales actions.", "What should I do next after finding a qualified prospect?", "c3"),
    ]
    cols = st.columns(3, gap="large")
    for col, (title, copy, action, key) in zip(cols, cards):
        with col:
            st.markdown("<div class='card-wrap'>", unsafe_allow_html=True)
            if st.button(f"{title}\n\n{copy}", key=key, use_container_width=True):
                submit_prompt(action)
            st.markdown("</div>", unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("followups"):
            st.markdown("<div class='chat-label'>Continue with</div>", unsafe_allow_html=True)
            fcols = st.columns(len(message["followups"]))
            for i, option in enumerate(message["followups"]):
                with fcols[i]:
                    if st.button(option, key=f"old_{message['id']}_{i}", use_container_width=True):
                        submit_prompt(option)

prompt = st.chat_input("Ask Unifers AI anything...")
active_prompt = prompt or st.session_state.pending_prompt
st.session_state.pending_prompt = None

if active_prompt:
    user_id = len(st.session_state.messages)
    st.session_state.messages.append({"role":"user", "content":active_prompt, "id":user_id})
    with st.chat_message("user"):
        st.markdown(active_prompt)

    with st.chat_message("assistant"):
        local = local_answer(active_prompt)
        answer = None
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
            answer = local
        st.markdown(answer)
        suggestions = followups(active_prompt)
        message_id = len(st.session_state.messages)
        st.session_state.messages.append({"role":"assistant", "content":answer, "followups":suggestions, "id":message_id})
        st.markdown("<div class='chat-label'>Continue with</div>", unsafe_allow_html=True)
        fcols = st.columns(len(suggestions))
        for i, option in enumerate(suggestions):
            with fcols[i]:
                if st.button(option, key=f"new_{message_id}_{i}", use_container_width=True):
                    submit_prompt(option)
