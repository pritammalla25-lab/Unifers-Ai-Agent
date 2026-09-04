import streamlit as st
from google import genai
from google.genai import types
from unifers_knowledge import UNIFERS_KNOWLEDGE

st.set_page_config(
    page_title="Unifers AI",
    page_icon="https://unifers.ai/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL = "gemini-3.5-flash-lite"
LOGO_URL = "https://unifers.ai/favicon.ico"

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

    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=types.GenerateContentConfig(**config_args),
    )
    return response.text


def local_answer(question):
    q = question.lower()

    if "what does unifers" in q or "what is unifers" in q:
        return "Unifers.ai is a sales intelligence and prospecting platform focused on helping revenue teams find relevant prospects, enrich data, verify information, identify buying signals and act on qualified opportunities.\n\nIts product portfolio includes Data Enrichment, LinkedIn Extension, LinkedIn Contact Finder, APIs, Email Deliverability and Email Warmup.\n\nThe goal is not simply to generate more contacts. The focus is on helping teams find the right prospects, understand why they matter, determine why now and choose the next action."

    if "products" in q and "unifers" in q:
        return "**Unifers product areas**\n\n1. **Data Enrichment** for enriching incomplete prospect and company information.\n2. **LinkedIn Extension** for browser based LinkedIn prospect workflows.\n3. **LinkedIn Contact Finder** for finding contact information associated with LinkedIn prospects.\n4. **APIs** for programmatic prospect and contact data workflows.\n5. **Email Deliverability** for outbound email delivery quality.\n6. **Email Warmup** for sender reputation and outbound email readiness."

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

    if "find better prospects" in q or "prospect" in q or "icp" in q:
        return [
            "Build an ICP for my business",
            "What buying signals should I look for?",
            "How should I score prospects?",
        ]

    if "next step" in q or "outreach" in q or "action" in q:
        return [
            "Create a personalized outreach message",
            "What should I do after finding a prospect?",
            "How do I prioritize prospects?",
        ]

    if "product" in q or "what does" in q or "what is unifers" in q:
        return [
            "What products does Unifers offer?",
            "Which product is best for contact enrichment?",
            "How can Unifers help a sales team?",
        ]

    if "data enrichment" in q:
        return [
            "What data can Unifers enrich?",
            "How does Data Enrichment fit into prospecting?",
            "Compare Data Enrichment with LinkedIn Contact Finder",
        ]

    if "linkedin contact" in q:
        return [
            "How does LinkedIn Contact Finder work?",
            "Compare it with Data Enrichment",
            "What can I do after finding a contact?",
        ]

    if "api" in q:
        return [
            "What does the Unifers API provide?",
            "Who should use the Unifers API?",
            "Compare APIs with the LinkedIn Extension",
        ]

    if "email" in q or "warmup" in q or "deliverability" in q:
        return [
            "What is Email Warmup?",
            "What is Email Deliverability?",
            "How are Warmup and Deliverability different?",
        ]

    return [
        "What products does Unifers offer?",
        "How does Unifers help sales teams?",
        "What information do you need to find prospects?",
    ]


def run_prompt(prompt):
    st.session_state.pending_prompt = prompt
    st.rerun()


if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] { background: #f7f9fc; }
    [data-testid="stHeader"] { background: transparent; }
    .block-container { max-width: 1180px; padding-top: 0.7rem; padding-bottom: 7rem; }
    [data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e7ebf2; }
    [data-testid="stSidebar"] .block-container { padding-top: 1.2rem; }

    .topbar {
        display: flex;
        align-items: center;
        gap: 11px;
        padding: 8px 2px 22px;
    }
    .brand-logo {
        width: 38px;
        height: 38px;
        border-radius: 11px;
        object-fit: contain;
        background: #ffffff;
        border: 1px solid #e4e8ef;
        padding: 5px;
    }
    .brand-name { color: #111827; font-size: 1.05rem; font-weight: 750; line-height: 1.1; }
    .brand-sub { color: #7a8494; font-size: .74rem; margin-top: 3px; }

    .hero { text-align: center; padding: 3.2rem 1rem 2.5rem; }
    .hero-logo {
        width: 66px;
        height: 66px;
        border-radius: 19px;
        object-fit: contain;
        background: #ffffff;
        border: 1px solid #e1e6ee;
        padding: 9px;
        box-shadow: 0 12px 32px rgba(17, 24, 39, .08);
    }
    .hero h1 {
        margin: 18px 0 8px;
        font-size: 3rem;
        letter-spacing: -2px;
        color: #111827;
        font-weight: 760;
    }
    .hero p { margin: 0; color: #697586; font-size: 1rem; }
    .hero-small { margin-top: 9px; color: #9aa4b2; font-size: .82rem; }

    .feature-label {
        color: #111827;
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .feature-copy {
        color: #687588;
        font-size: .87rem;
        line-height: 1.5;
        min-height: 45px;
    }
    .card-button button {
        min-height: 145px;
        border-radius: 19px !important;
        border: 1px solid #dfe5ee !important;
        background: #ffffff !important;
        color: #111827 !important;
        text-align: left !important;
        padding: 22px 22px !important;
        box-shadow: 0 7px 22px rgba(15, 23, 42, .035) !important;
        transition: all .16s ease !important;
    }
    .card-button button:hover {
        border-color: #b8c5d8 !important;
        box-shadow: 0 12px 30px rgba(15, 23, 42, .08) !important;
        transform: translateY(-2px);
    }
    .card-button button p { white-space: normal !important; }

    .section-title { color: #111827; font-weight: 700; font-size: .9rem; margin: 8px 0 9px; }
    .suggestion button {
        border-radius: 12px !important;
        border: 1px solid #e0e5ed !important;
        background: #fff !important;
        color: #263246 !important;
        font-size: .82rem !important;
        text-align: left !important;
    }
    [data-testid="stChatMessage"] { border-radius: 18px; }
    div.stButton > button { border-radius: 12px; }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown(
        f"""
        <div class='topbar'>
            <img class='brand-logo' src='{LOGO_URL}'>
            <div>
                <div class='brand-name'>Unifers AI</div>
                <div class='brand-sub'>Sales Intelligence Assistant</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown("### Quick actions")
    st.caption("Start with a focused question and let the assistant guide the next step.")

    if st.button("Understand Unifers", use_container_width=True, key="side_company"):
        run_prompt("What does Unifers do?")
    if st.button("Find better prospects", use_container_width=True, key="side_prospects"):
        run_prompt("How can I find better prospects with Unifers?")
    if st.button("Take the next step", use_container_width=True, key="side_action"):
        run_prompt("What should I do next after finding a qualified prospect?")
    if st.button("Explore products", use_container_width=True, key="side_products"):
        run_prompt("What products does Unifers offer?")
    if st.button("Explore APIs", use_container_width=True, key="side_api"):
        run_prompt("Does Unifers provide APIs?")

    st.divider()
    if st.button("New conversation", use_container_width=True, key="new_chat"):
        st.session_state.messages = []
        st.session_state.pending_prompt = None
        st.rerun()
    st.caption("Answers are grounded in the available Unifers knowledge.")

if not st.session_state.messages:
    st.markdown(
        f"""
        <div class='hero'>
            <img class='hero-logo' src='{LOGO_URL}'>
            <h1>Unifers AI</h1>
            <p>Your intelligent assistant for Unifers products and sales intelligence</p>
            <div class='hero-small'>Ask a question or choose a starting point below</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(3, gap="large")
    cards = [
        (
            "Understand Unifers",
            "Get clear answers about products, capabilities and use cases.",
            "What does Unifers do?",
            "home_understand",
        ),
        (
            "Find better prospects",
            "Build ICPs, evaluate buying signals and identify relevant decision makers.",
            "How can I find better prospects with Unifers?",
            "home_prospects",
        ),
        (
            "Take the next step",
            "Get recommendations for research, outreach and sales actions.",
            "What should I do next after finding a qualified prospect?",
            "home_next",
        ),
    ]

    for col, (title, copy, prompt_value, key) in zip(cols, cards):
        with col:
            st.markdown("<div class='card-button'>", unsafe_allow_html=True)
            if st.button(
                f"{title}\n\n{copy}",
                key=key,
                use_container_width=True,
            ):
                run_prompt(prompt_value)
            st.markdown("</div>", unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("followups"):
            st.markdown("<div class='section-title'>Continue the conversation</div>", unsafe_allow_html=True)
            follow_cols = st.columns(len(message["followups"]))
            for index, option in enumerate(message["followups"]):
                with follow_cols[index]:
                    if st.button(option, key=f"follow_{message['id']}_{index}", use_container_width=True):
                        run_prompt(option)

prompt = st.chat_input("Ask anything about Unifers...")
active_prompt = prompt or st.session_state.pending_prompt
st.session_state.pending_prompt = None

if active_prompt:
    st.session_state.messages.append(
        {"role": "user", "content": active_prompt, "id": len(st.session_state.messages)}
    )

    with st.chat_message("user"):
        st.markdown(active_prompt)

    with st.chat_message("assistant"):
        answer = None
        local = local_answer(active_prompt)
        client = get_client()

        if client:
            try:
                with st.spinner("Thinking..."):
                    answer = ask_gemini(
                        client,
                        st.session_state.messages,
                        use_web=needs_web(active_prompt),
                    )
            except Exception:
                answer = local
        else:
            answer = local

        if not answer:
            answer = (
                "I can help with Unifers products, APIs, enrichment, LinkedIn workflows, "
                "email infrastructure, prospecting, buying signals, scoring and outreach. "
                "Tell me what you want to know, and I will answer from the available Unifers knowledge."
            )

        st.markdown(answer)
        suggestions = followups(active_prompt, answer)
        message_id = len(st.session_state.messages)
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "followups": suggestions,
                "id": message_id,
            }
        )

        st.markdown("<div class='section-title'>Continue the conversation</div>", unsafe_allow_html=True)
        follow_cols = st.columns(len(suggestions))
        for index, option in enumerate(suggestions):
            with follow_cols[index]:
                if st.button(option, key=f"new_follow_{message_id}_{index}", use_container_width=True):
                    run_prompt(option)
