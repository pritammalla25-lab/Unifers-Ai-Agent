import streamlit as st
from google import genai
from google.genai import types
from unifers_knowledge import UNIFERS_KNOWLEDGE

st.set_page_config(page_title="Unifers AI", page_icon="U", layout="wide", initial_sidebar_state="expanded")

MODEL = "gemini-3.7-flash"
LOGO_URL = "https://unifers.ai/favicon.ico"

SYSTEM_INSTRUCTION = """
You are Unifers AI, the intelligent public information and sales intelligence assistant for Unifers.ai.

Answer the user's exact question first. Use the supplied Unifers knowledge as the primary source for Unifers specific facts. When web search is enabled, prefer official Unifers.ai pages and use them to verify current information. Clearly distinguish verified public facts from inference. Never invent pricing, customers, features, integrations, people, emails, phone numbers, funding, job titles, buying signals, private information or completed actions.

If the user asks about prospecting, focus on ICP fit, company relevance, decision maker relevance, buying signal, timing, confidence and next action. Optimize for qualified conversations with the right prospects, not lead volume.

If a fact is not available or cannot be verified, say so directly. Do not make a confident guess just to fill a gap.

Keep answers practical, concise and easy to scan. Use tables when comparing multiple products or prospects.

UNIFERS KNOWLEDGE:
""" + str(UNIFERS_KNOWLEDGE)


def get_client():
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        key = ""
    return genai.Client(api_key=key) if key else None


def has_api_key():
    try:
        return bool(st.secrets.get("GEMINI_API_KEY", ""))
    except Exception:
        return False


def needs_web(question):
    q = question.lower()
    changing = [
        "latest", "current", "today", "recent", "news", "research",
        "funding", "pricing", "price", "cost", "how much", "free",
        "credits", "2026", "compare", "comparison", "available now",
        "coming soon", "new", "update"
    ]
    return any(x in q for x in changing)


def ask_gemini(client, messages, use_web=False):
    contents = []
    for message in messages:
        role = "user" if message["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=message["content"])]))

    config = {
        "system_instruction": SYSTEM_INSTRUCTION,
        "max_output_tokens": 1600,
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
        return "### What is Unifers AI?\n\nUnifers.ai is a sales discovery and outreach automation platform that helps revenue teams discover verified contacts, enrich prospect data, verify information and automate outreach workflows.\n\nIts public product areas include Data Enrichment, LinkedIn Extension, LinkedIn Contact Finder, APIs, Email Deliverability and Email Warmup."
    if "products" in q and "unifers" in q:
        return "### Unifers product areas\n\n| Product | Main purpose |\n| --- | --- |\n| Data Enrichment | Turn partial prospect records into richer profiles |\n| LinkedIn Extension | Find verified contact details while working in LinkedIn |\n| LinkedIn Contact Finder | Find verified emails and phone numbers from LinkedIn prospects |\n| APIs | Put enrichment and contact intelligence into software workflows |\n| Email Deliverability | Improve outbound email infrastructure and sender health |\n| Email Warmup | Build sender reputation for outbound email |"
    if "linkedin contact finder" in q:
        return "### LinkedIn Contact Finder\n\nUnifers describes this as a tool for finding verified business emails and direct phone numbers from LinkedIn. The public page says it supports LinkedIn and Sales Navigator, unlimited US email and phone lookups, bulk enrichment and waterfall enrichment for contacts outside the US."
    if "api" in q or "apis" in q:
        return "### Unifers APIs\n\nThe public API product is designed for programmatic contact intelligence. Unifers describes LinkedIn profile enrichment, verified contact information, real time verification, REST APIs, SDK support, webhooks, OpenAPI and Swagger specifications and a sandbox environment."
    if "email warmup" in q:
        return "### Email Warmup\n\nUnifers Email Warmup focuses on building sender reputation for outbound email. Publicly described capabilities include automated warmup interactions, slow ramping, read emulation, live placement monitoring and connections for Google Workspace or Microsoft 365."
    if "deliverability" in q:
        return "### Email Deliverability\n\nUnifers describes its deliverability product as infrastructure for protecting sender reputation and improving inbox delivery. Publicly described capabilities include bounce protection, domain health monitoring, IP throttling, load balancing and SPF, DKIM and DMARC support."
    if "data enrichment" in q:
        return "### Data Enrichment\n\nUnifers Data Enrichment turns partial prospect information into richer profiles. The public homepage describes enriching leads with emails, phone numbers and social links."
    if "find better prospects" in q or "how can i find better prospects" in q:
        return "### Finding better prospects\n\nStart with a clear ICP rather than maximizing lead volume.\n\n1. Define industry, geography, company size and business model.\n2. Identify the right decision maker.\n3. Look for a credible reason the company may care now.\n4. Verify company and contact information.\n5. Score fit, relevance, timing and confidence.\n6. Contact the highest quality opportunities first."
    if "next step" in q or "what should i do next" in q:
        return "### Recommended next step\n\nVerify the prospect, identify the strongest timing signal, decide why the person should care now, choose the right channel and personalize the message around the prospect's situation."
    return "I can help with Unifers products, prospect discovery, ICPs, buying signals, scoring, enrichment, LinkedIn workflows, APIs, email infrastructure and next best actions. Ask me a specific question and I will answer it directly."


def followups(question):
    q = question.lower()
    if "prospect" in q or "icp" in q:
        return ["Build an ICP for my business", "What buying signals should I look for?", "How should I score prospects?"]
    if "api" in q:
        return ["Who should use the Unifers API?", "What does the API provide?", "Compare APIs with LinkedIn Contact Finder"]
    if "email" in q or "warmup" in q or "deliverability" in q:
        return ["What is Email Warmup?", "What is Email Deliverability?", "How are Warmup and Deliverability different?"]
    if "linkedin" in q:
        return ["What is LinkedIn Contact Finder?", "Does Unifers work with Sales Navigator?", "What does Unifers enrich?"]
    if "outreach" in q or "action" in q:
        return ["Create a personalized outreach message", "How do I prioritize prospects?", "What should I verify before outreach?"]
    return ["What products does Unifers offer?", "How can I find better prospects?", "What should I do next after finding a prospect?"]


def source_links(question):
    q = question.lower()
    links = []
    if "api" in q:
        links.append(("Unifers APIs", "https://unifers.ai/apis"))
    if "linkedin" in q or "contact finder" in q:
        links.append(("LinkedIn Contact Finder", "https://unifers.ai/linkedin-contact-finder"))
    if "warmup" in q:
        links.append(("Email Warmup", "https://unifers.ai/email-warmup"))
    if "deliverability" in q or "email" in q:
        links.append(("Email Deliverability", "https://unifers.ai/email-deliverability"))
    if "product" in q or "what is unifers" in q or "what does unifers" in q:
        links.append(("Unifers official site", "https://unifers.ai/"))
    if not links:
        links.append(("Unifers official site", "https://unifers.ai/"))
    return links[:3]


def submit_prompt(text):
    st.session_state.pending_prompt = text
    st.rerun()


if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None
if "last_error" not in st.session_state:
    st.session_state.last_error = ""

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] { background:#f7f9fc; }
    [data-testid="stHeader"] { background:transparent; }
    .block-container { max-width:1120px; padding-top:18px; padding-bottom:110px; }
    [data-testid="stSidebar"] { background:#ffffff; border-right:1px solid #e6eaf0; }
    [data-testid="stSidebar"] .block-container { padding-top:22px; }
    .brand { display:flex; align-items:center; gap:10px; margin-bottom:18px; }
    .brand img { width:38px; height:38px; border:1px solid #e1e6ed; border-radius:11px; padding:6px; background:white; }
    .brand-name { font-weight:760; font-size:1rem; color:#111827; }
    .brand-sub { color:#7b8798; font-size:.72rem; margin-top:2px; }
    .status { display:inline-block; padding:5px 9px; border-radius:999px; background:#eef7f1; color:#24734a; font-size:.72rem; font-weight:650; margin:2px 0 16px; }
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
    .source-title { color:#8a95a5; font-size:.72rem; margin-top:18px; margin-bottom:5px; }
    .source-link { font-size:.78rem; margin-right:14px; }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown(
        f"<div class='brand'><img src='{LOGO_URL}'><div><div class='brand-name'>Unifers AI</div><div class='brand-sub'>Sales Intelligence Assistant</div></div></div>",
        unsafe_allow_html=True,
    )
    st.markdown(f"<div class='status'>{'AI connected' if has_api_key() else 'Demo mode'}</div>", unsafe_allow_html=True)
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
        st.session_state.last_error = ""
        st.rerun()
    if st.session_state.last_error:
        with st.expander("System status"):
            st.caption("The AI service returned an error, so the built in Unifers knowledge was used instead.")

if not st.session_state.messages:
    st.markdown(
        f"<div class='hero'><img src='{LOGO_URL}'><h1>Unifers AI</h1><p>Your intelligent assistant for products, prospects and sales intelligence</p><div class='hero-note'>Ask anything about Unifers or start with a workflow</div></div>",
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
        if message["role"] == "assistant" and message.get("sources"):
            st.markdown("<div class='source-title'>Official sources</div>", unsafe_allow_html=True)
            source_html = " ".join([f"<span class='source-link'><a href='{url}' target='_blank'>{name}</a></span>" for name, url in message["sources"]])
            st.markdown(source_html, unsafe_allow_html=True)
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
        st.session_state.last_error = ""
        if client:
            try:
                with st.spinner("Thinking..."):
                    answer = ask_gemini(client, st.session_state.messages, use_web=needs_web(active_prompt))
            except Exception as exc:
                st.session_state.last_error = str(exc)
                answer = local
        else:
            answer = local

        if not answer:
            answer = local

        st.markdown(answer)
        sources = source_links(active_prompt)
        st.markdown("<div class='source-title'>Official sources</div>", unsafe_allow_html=True)
        source_html = " ".join([f"<span class='source-link'><a href='{url}' target='_blank'>{name}</a></span>" for name, url in sources])
        st.markdown(source_html, unsafe_allow_html=True)

        suggestions = followups(active_prompt)
        message_id = len(st.session_state.messages)
        st.session_state.messages.append({"role":"assistant", "content":answer, "followups":suggestions, "sources":sources, "id":message_id})
        st.markdown("<div class='chat-label'>Continue with</div>", unsafe_allow_html=True)
        fcols = st.columns(len(suggestions))
        for i, option in enumerate(suggestions):
            with fcols[i]:
                if st.button(option, key=f"new_{message_id}_{i}", use_container_width=True):
                    submit_prompt(option)
