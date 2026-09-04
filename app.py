import streamlit as st
import re

st.set_page_config(
    page_title="Unifers AI",
    page_icon="U",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.main {
    background-color: #f7f8fc;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1250px;
}

.hero {
    padding: 28px 32px;
    border-radius: 18px;
    background: linear-gradient(135deg, #111827, #1f2937);
    color: white;
    margin-bottom: 24px;
}

.hero h1 {
    font-size: 38px;
    margin-bottom: 8px;
}

.hero p {
    font-size: 17px;
    color: #d1d5db;
}

.metric-card {
    background: white;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #e5e7eb;
    margin-bottom: 12px;
}

.prospect-card {
    background: white;
    padding: 22px;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    margin-bottom: 16px;
}

.score {
    font-size: 30px;
    font-weight: 700;
}

.signal {
    background: #eef2ff;
    padding: 7px 12px;
    border-radius: 20px;
    display: inline-block;
    font-size: 13px;
}

.small {
    color: #6b7280;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)


if "analyzed" not in st.session_state:
    st.session_state.analyzed = False

if "target" not in st.session_state:
    st.session_state.target = ""


with st.sidebar:

    st.markdown("## Unifers AI")

    st.caption("Sales Intelligence Agent")

    st.divider()

    st.markdown("### Search configuration")

    industry = st.text_input(
        "Industry",
        placeholder="Example: SaaS"
    )

    location = st.text_input(
        "Location",
        placeholder="Example: India"
    )

    company_size = st.text_input(
        "Company size",
        placeholder="Example: 100 to 500"
    )

    role = st.text_input(
        "Target role",
        placeholder="Example: VP Sales"
    )

    st.divider()

    st.markdown("### Intelligence priorities")

    buying_signals = st.multiselect(
        "Buying signals",
        [
            "Recent funding",
            "Hiring",
            "Rapid growth",
            "New market expansion",
            "Technology change",
            "Leadership change"
        ],
        default=["Recent funding", "Hiring"]
    )

    st.divider()

    st.caption("Prototype intelligence engine")
    st.caption("Live research will be connected in the next stage.")


st.markdown("""
<div class="hero">
    <h1>Unifers AI</h1>
    <p>Find the right companies. Identify the right people. Understand why now. Decide what to do next.</p>
</div>
""", unsafe_allow_html=True)


st.markdown("## What are you looking for?")

target = st.text_area(
    "Describe your ideal customer naturally",
    value=st.session_state.target,
    height=120,
    placeholder=(
        "Example: Find SaaS companies in India with 100 to 500 "
        "employees that are hiring salespeople and recently raised funding."
    ),
    label_visibility="collapsed"
)


col1, col2 = st.columns([1, 5])

with col1:
    analyze = st.button(
        "Analyze",
        type="primary",
        use_container_width=True
    )

with col2:
    st.markdown(
        '<span class="small">The agent will interpret your ICP, evaluate opportunity signals and recommend where to focus.</span>',
        unsafe_allow_html=True
    )


if analyze:

    if not target.strip() and not industry.strip():
        st.error("Please describe your target customer or enter an industry.")
        st.stop()

    st.session_state.target = target
    st.session_state.analyzed = True


if st.session_state.analyzed:

    st.divider()

    st.markdown("## Interpreted ICP")

    text = st.session_state.target.lower()

    detected_industry = industry if industry else "Not specified"
    detected_location = location if location else "Not specified"
    detected_size = company_size if company_size else "Not specified"
    detected_role = role if role else "Not specified"

    common_industries = [
        "saas",
        "fintech",
        "edtech",
        "healthtech",
        "ecommerce",
        "logistics",
        "manufacturing",
        "real estate"
    ]

    for item in common_industries:
        if item in text:
            detected_industry = item.upper()
            break

    locations = [
        "india",
        "usa",
        "uk",
        "singapore",
        "dubai",
        "australia"
    ]

    for item in locations:
        if item in text:
            detected_location = item.title()
            break

    size_match = re.search(
        r"(\d+)\s*(?:to|-)\s*(\d+)\s*employees",
        text
    )

    if size_match:
        detected_size = (
            size_match.group(1)
            + " to "
            + size_match.group(2)
        )

    cards = st.columns(4)

    values = [
        ("Industry", detected_industry),
        ("Location", detected_location),
        ("Company size", detected_size),
        ("Target role", detected_role)
    ]

    for card, item in zip(cards, values):
        with card:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="small">{item[0]}</div>
                    <strong>{item[1]}</strong>
                </div>
                """,
                unsafe_allow_html=True
            )


    st.markdown("## Opportunity priorities")

    priorities = st.columns(4)

    metrics = [
        ("ICP Fit", "High"),
        ("Buying Intent", "Medium"),
        ("Timing", "High"),
        ("Data Confidence", "Pending")
    ]

    for card, metric in zip(priorities, metrics):
        with card:
            st.metric(metric[0], metric[1])


    st.divider()

    st.markdown("## Priority prospects")

    demo_prospects = [
        {
            "company": "Example Growth Company",
            "role": detected_role,
            "score": 91,
            "signal": "Recent funding",
            "why": "Strong ICP alignment combined with a relevant growth signal.",
            "action": "Research the relevant decision maker and prepare a personalized opening."
        },
        {
            "company": "Example Scale Company",
            "role": detected_role,
            "score": 84,
            "signal": "Hiring activity",
            "why": "Hiring can indicate increasing commercial activity and potential demand.",
            "action": "Validate the hiring signal and identify the executive responsible for growth."
        },
        {
            "company": "Example Expansion Company",
            "role": detected_role,
            "score": 76,
            "signal": "Market expansion",
            "why": "Expansion may create new acquisition and outbound requirements.",
            "action": "Investigate the expansion strategy before initiating outreach."
        }
    ]

    for prospect in demo_prospects:

        st.markdown(
            f"""
            <div class="prospect-card">

                <div style="display:flex; justify-content:space-between;">

                    <div>
                        <h3>{prospect["company"]}</h3>
                        <div class="small">{prospect["role"]}</div>
                    </div>

                    <div style="text-align:right;">
                        <div class="score">{prospect["score"]}</div>
                        <div class="small">Opportunity score</div>
                    </div>

                </div>

                <br>

                <span class="signal">{prospect["signal"]}</span>

                <br><br>

                <strong>Why this company</strong>
                <p>{prospect["why"]}</p>

                <strong>Recommended action</strong>
                <p>{prospect["action"]}</p>

            </div>
            """,
            unsafe_allow_html=True
        )


    st.info(
        "Prototype mode: the prospect examples above are placeholders. "
        "They are intentionally not presented as verified companies. "
        "Live company research, verification and enrichment will be connected next."
    )


    st.divider()

    st.markdown("## What should happen next?")

    next_cols = st.columns(3)

    with next_cols[0]:
        st.markdown("### Research")
        st.write(
            "Collect company intelligence, decision makers and buying signals."
        )

    with next_cols[1]:
        st.markdown("### Score")
        st.write(
            "Rank opportunities using ICP fit, intent, timing and confidence."
        )

    with next_cols[2]:
        st.markdown("### Act")
        st.write(
            "Recommend the best next action and prepare personalized outreach."
        )


st.divider()

st.caption(
    "Unifers AI Sales Intelligence Agent • Prototype"
)
