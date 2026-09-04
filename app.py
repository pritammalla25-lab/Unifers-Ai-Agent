import streamlit as st
from google import genai
from google.genai import types
from unifers_knowledge import UNIFERS_KNOWLEDGE

st.set_page_config(
    page_title="Unifers AI",
    page_icon="U",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL = "gemini-3.8-flash"

SYSTEM_INSTRUCTION = """
You are Unifers AI, an intelligent B2B Sales Intelligence and Prospecting Agent for Unifers.ai.

Your goal is to help users identify the right companies, right people, right timing and right action. Think like a senior SDR, sales researcher, GTM strategist, account research analyst, data enrichment specialist, sales intelligence analyst and AI outreach strategist.

Core philosophy: Find -> Understand -> Verify -> Score -> Recommend -> Act -> Learn.
Optimize for qualified conversations, not lead volume.

Conversation behavior:
Understand the user's goal. Ask only for missing information that is necessary. Reuse information already provided. For broad prospecting requests, clarify ICP when needed.

Prospect intelligence priorities:
ICP fit, company relevance, decision maker relevance, buying intent, timing and data confidence.
When information is available, consider company, website, industry, employees, location, revenue, funding, growth, hiring, technology, executives, decision makers, contact information, developments and buying signals.

Research behavior:
Separate verified facts from inference and unknown information. Buying signals may indicate relevance but do not prove purchase intent. Use language such as may indicate, suggests and potentially relevant when evidence is not conclusive.

Scoring behavior:
When enough evidence exists, use a transparent decision support score based on ICP fit, role relevance, company growth, buying intent, data confidence and timing. Do not present the score as scientifically exact.

For high priority prospects explain:
Why this company?
Why this person?
Why now?
Recommended action.

Outreach:
Keep cold outreach concise and human. Personalize using verified company events, role responsibilities, hiring, funding, products, technology, business challenges or recent developments. Never invent familiarity or facts.

Data honesty:
Never invent emails, phone numbers, company facts, funding, job titles, buying signals, technology usage, customer relationships or personal information. If unavailable, say: I don't have verified information for this field.

Action safety:
Distinguish between recommended, prepared, ready to send, sent and completed. Never claim an action was completed unless a connected system confirms it.

Response style:
Be concise for simple questions and structured for complex tasks. Use headings, bullets and tables when useful. Be analytical rather than blindly agreeable. If the user's targeting is weak or too broad, explain why and suggest a better approach.

Unifers knowledge:
""" + str(UNIFERS_KNOWLEDGE)


def get_client():
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


def ask_gemini(client, messages):
    contents = []
    for message in messages:
        role = "user" if message["role"] == "user" else "model"
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part(text=message["content"])],
            )
        )

    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=[types.Tool(google_search=types.GoogleSearch())],
            max_output_tokens=2500,
        ),
    )
    return response.text


if "messages" not in st.session_state:
    st.session_state.messages = []

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #ffffff; }
[data-testid="stHeader"] { background: rgba(255,255,255,0.85); }
.block-container { max-width: 1050px; padding-top: 2rem; padding-bottom: 7rem; }
.hero { text-align: center; padding: 3.5rem 1rem 2rem; }
.logo { display:inline-flex; width:52px; height:52px; align-items:center; justify-content:center; border-radius:15px; background:#111827; color:white; font-size:25px; font-weight:800; margin-bottom:18px; }
.hero h1 { font-size: 2.7rem; letter-spacing:-1.5px; margin:0; color:#111827; }
.hero p { color:#6b7280; font-size:1.05rem; margin-top:10px; }
.card { border:1px solid #e5e7eb; border-radius:18px; padding:20px; background:white; height:100%; box-shadow:0 4px 18px rgba(17,24,39,.04); }
.card-title { font-weight:700; color:#111827; margin-bottom:7px; }
.card-text { color:#6b7280; font-size:.93rem; line-height:1.5; }
[data-testid="stChatMessage"] { border-radius:18px; padding:12px 16px; }
[data-testid="stSidebar"] { border-right:1px solid #e5e7eb; }
[data-testid="stSidebar"] .block-container { padding-top:1.5rem; }
.small-note { color:#9ca3af; font-size:.8rem; text-align:center; margin-top:18px; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Unifers AI")
    st.caption("Sales Intelligence Assistant")
    st.divider()
    st.markdown("### Explore")
    st.caption("Ask about Unifers products, capabilities, APIs, prospecting, enrichment, LinkedIn workflows and sales intelligence.")
    st.divider()
    st.markdown("### Suggested questions")
    starters = [
        "What does Unifers do?",
        "What products does Unifers offer?",
        "Explain Unifers Data Enrichment",
        "What is the LinkedIn Contact Finder?",
        "Does Unifers provide APIs?",
        "How can Unifers help a sales team?",
    ]
    for question in starters:
        if st.button(question, key="starter_" + question, use_container_width=True):
            st.session_state.pending_prompt = question
            st.rerun()
    st.divider()
    if st.button("New conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pop("pending_prompt", None)
        st.rerun()
    st.divider()
    st.caption("Powered by Gemini")
    st.caption("Web grounded when useful")

if not st.session_state.messages:
    st.markdown("<div class='hero'><div class='logo'>U</div><h1>Unifers AI</h1><p>Ask anything about Unifers</p></div>", unsafe_allow_html=True)
    cols = st.columns(3)
    cards = [
        ("Products", "Understand Unifers products, capabilities and use cases."),
        ("Sales intelligence", "Explore prospecting, enrichment, buying signals and outreach."),
        ("Research", "Ask for current information and the assistant can use web grounded research."),
    ]
    for col, (title, text) in zip(cols, cards):
        with col:
            st.markdown(f"<div class='card'><div class='card-title'>{title}</div><div class='card-text'>{text}</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='small-note'>Start with a question below. Unifers AI will keep the conversation in context.</div>", unsafe_allow_html=True)
else:
    st.markdown("<div style='padding-bottom:12px'><h1 style='margin-bottom:0'>Unifers AI</h1><div style='color:#6b7280'>Your Unifers product and sales intelligence assistant</div></div>", unsafe_allow_html=True)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask anything about Unifers...")
pending = st.session_state.pop("pending_prompt", None)
active_prompt = prompt or pending

if active_prompt:
    st.session_state.messages.append({"role": "user", "content": active_prompt})
    with st.chat_message("user"):
        st.markdown(active_prompt)
    with st.chat_message("assistant"):
        client = get_client()
        if client is None:
            st.error("Gemini is not connected yet. Add GEMINI_API_KEY in Streamlit Secrets and reload the app.")
        else:
            try:
                with st.spinner("Thinking..."):
                    answer = ask_gemini(client, st.session_state.messages)
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as error:
                st.error("I could not complete that request right now.")
                st.caption("Please check the Gemini API key and model access in Streamlit Secrets.")
                st.caption("Technical detail: " + str(error))
