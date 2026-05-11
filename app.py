import streamlit as st
import time
from datetime import datetime

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NeuronDepth · Deep Research AI",
    page_icon="⬡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg:      #09090b;
    --surface: #111113;
    --border:  rgba(255,255,255,0.08);
    --border2: rgba(255,255,255,0.13);
    --accent:  #6366f1;
    --green:   #22c55e;
    --text:    #f4f4f5;
    --dim:     #71717a;
    --muted:   #3f3f46;
    --font:    'Inter', sans-serif;
    --mono:    'JetBrains Mono', monospace;
}

html, body, [class*="css"] { font-family: var(--font); }
.stApp { background: var(--bg); }
#MainMenu, footer, header, [data-testid="stSidebar"] { display: none !important; }
.block-container { padding: 2.5rem 1rem 5rem !important; max-width: 660px !important; }

.stTextInput > div > div > input {
    background: var(--surface) !important;
    border: 1px solid var(--border2) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
    font-size: 0.95rem !important;
    padding: 0.75rem 1rem !important;
    caret-color: var(--accent) !important;
    transition: border-color 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
}
.stTextInput > div > div > input::placeholder { color: var(--muted) !important; }
.stTextInput > label { display: none !important; }

.stButton > button {
    background: var(--accent) !important;
    border: none !important;
    border-radius: 10px !important;
    color: #fff !important;
    font-family: var(--font) !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    padding: 0.65rem 1.4rem !important;
    width: 100% !important;
    transition: opacity 0.15s, transform 0.15s !important;
}
.stButton > button:hover { opacity: 0.85 !important; transform: translateY(-1px) !important; }

[data-testid="stDownloadButton"] button {
    background: rgba(34,197,94,0.08) !important;
    border: 1px solid rgba(34,197,94,0.25) !important;
    color: var(--green) !important;
    border-radius: 8px !important;
    font-family: var(--mono) !important;
    font-size: 0.7rem !important;
    padding: 0.45rem 1.1rem !important;
}

.stExpander {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    margin-bottom: 6px !important;
}
details summary {
    font-family: var(--mono) !important;
    font-size: 0.7rem !important;
    color: var(--dim) !important;
    padding: 0.7rem 1rem !important;
}

.stSpinner > div { border-top-color: var(--accent) !important; }

.stMarkdown p { color: var(--dim); font-size: 0.88rem; line-height: 1.75; }
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    color: var(--text) !important; font-weight: 600 !important; letter-spacing: -0.02em !important;
}
.stMarkdown code {
    font-family: var(--mono) !important; background: var(--surface) !important;
    color: var(--accent) !important; border-radius: 4px !important; padding: 1px 5px !important;
}
.stMarkdown table { border-collapse: collapse !important; width: 100% !important; font-size: 0.85rem !important; }
.stMarkdown th {
    font-family: var(--mono) !important; font-size: 0.68rem !important;
    text-transform: uppercase !important; color: var(--dim) !important;
    background: var(--surface) !important; padding: 6px 12px !important;
    border: 1px solid var(--border) !important;
}
.stMarkdown td { padding: 6px 12px !important; border: 1px solid var(--border) !important; color: var(--dim) !important; }
.stAlert { background: rgba(99,102,241,0.08) !important; border-radius: 8px !important; }

@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.35} }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
for k, v in {"results": {}, "running": False, "done": False, "timestamps": {}}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def agent_state(step):
    r = st.session_state.results
    if step in r:
        return "done"
    if st.session_state.running:
        for s in ["search", "reader", "writer", "critic"]:
            if s not in r:
                return "running" if s == step else "waiting"
    return "waiting"


def render_card(num, icon, title, desc, step):
    state = agent_state(step)
    ts = st.session_state.timestamps.get(step, "")

    bar = {"waiting": "var(--muted)", "running": "var(--accent)", "done": "var(--green)"}[state]
    bg  = {"waiting": "var(--surface)", "running": "rgba(99,102,241,0.04)",
           "done": "rgba(34,197,94,0.03)"}[state]
    bdr = {"waiting": "var(--border)", "running": "rgba(99,102,241,0.28)",
           "done": "rgba(34,197,94,0.22)"}[state]
    pill = {
        "waiting": f'<span style="font-family:var(--mono);font-size:0.6rem;color:var(--muted);">waiting</span>',
        "running": f'<span style="font-family:var(--mono);font-size:0.6rem;color:var(--accent);animation:blink 1.4s infinite;">● running</span>',
        "done":    f'<span style="font-family:var(--mono);font-size:0.6rem;color:var(--green);">✓ {ts}</span>',
    }[state]

    st.markdown(f"""
    <div style="background:{bg};border:1px solid {bdr};border-left:3px solid {bar};
         border-radius:0 10px 10px 0;padding:12px 16px;margin-bottom:7px;
         display:flex;align-items:center;gap:14px;">
      <span style="font-size:1.1rem;flex-shrink:0;width:32px;text-align:center;">{icon}</span>
      <div style="flex:1;min-width:0;">
        <div style="font-family:var(--mono);font-size:0.56rem;color:var(--muted);
             letter-spacing:0.14em;margin-bottom:2px;">AGENT {num}</div>
        <div style="font-size:0.88rem;font-weight:500;color:var(--text);">{title}</div>
        <div style="font-size:0.75rem;color:var(--dim);margin-top:1px;">{desc}</div>
      </div>
      <div style="flex-shrink:0;">{pill}</div>
    </div>
    """, unsafe_allow_html=True)


def render_progress():
    done_n = sum(1 for s in ["search","reader","writer","critic"] if s in st.session_state.results)
    pct = int((done_n / 4) * 100)
    if st.session_state.running and done_n < 4:
        pct = min(pct + 8, 94)
    st.markdown(f"""
    <div style="margin:10px 0 0;">
      <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
        <span style="font-family:var(--mono);font-size:0.58rem;color:var(--muted);letter-spacing:0.12em;">PROGRESS</span>
        <span style="font-family:var(--mono);font-size:0.58rem;color:var(--accent);">{pct}%</span>
      </div>
      <div style="height:2px;background:var(--muted);border-radius:2px;">
        <div style="height:100%;width:{pct}%;background:var(--accent);border-radius:2px;transition:width 0.6s ease;"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="text-align:center;padding:1.8rem 0 1.5rem;">
  <div style="display:inline-flex;align-items:center;gap:9px;margin-bottom:12px;">
    <div style="width:22px;height:22px;background:var(--accent);flex-shrink:0;
         clip-path:polygon(50% 0%,100% 25%,100% 75%,50% 100%,0% 75%,0% 25%);"></div>
    <span style="font-size:1.05rem;font-weight:600;letter-spacing:-0.02em;color:var(--text);">NeuronDepth</span>
  </div>
  <h1 style="font-size:2rem;font-weight:600;letter-spacing:-0.04em;color:var(--text);
      margin:0 0 0.5rem;line-height:1.1;">
    Deep Research, <span style="color:var(--accent);">Automated.</span>
  </h1>
  <p style="font-size:0.86rem;color:var(--dim);max-width:400px;margin:0 auto;line-height:1.6;font-weight:300;">
    Four AI agents collaborate to deliver a polished research report on any topic.
  </p>
</div>
<div style="height:1px;background:var(--border);margin-bottom:1.4rem;"></div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  INPUT
# ══════════════════════════════════════════════════════════════════════════════
topic = st.text_input("topic", placeholder="Research topic — e.g. Quantum error correction 2025",
                      key="topic_input", label_visibility="collapsed")

c1, c2 = st.columns([5, 1])
with c1:
    run_btn = st.button("Run Research Pipeline", use_container_width=True)
with c2:
    reset_btn = st.button("Reset", use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
#  PIPELINE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="font-family:var(--mono);font-size:0.58rem;letter-spacing:0.16em;
     color:var(--muted);margin:1.4rem 0 8px;">PIPELINE</div>
""", unsafe_allow_html=True)

render_card("01", "🔍", "Search Agent",  "Discovers recent web sources",       "search")
render_card("02", "📄", "Reader Agent",  "Scrapes & extracts deep content",     "reader")
render_card("03", "✍️", "Writer Chain",  "Drafts the full research report",     "writer")
render_card("04", "🧠", "Critic Chain",  "Reviews & scores the report",         "critic")

if st.session_state.running or st.session_state.done:
    render_progress()

# ══════════════════════════════════════════════════════════════════════════════
#  ACTIONS
# ══════════════════════════════════════════════════════════════════════════════
if reset_btn:
    for k in ["results", "running", "done", "timestamps"]:
        st.session_state[k] = {} if k in ("results","timestamps") else False
    st.rerun()

if run_btn:
    if not topic.strip():
        st.warning("Enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.timestamps = {}
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  EXECUTION
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.running and not st.session_state.done:
    from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

    results = st.session_state.results
    t = st.session_state.topic_input

    # Step 1: Search
    if "search" not in results:
        with st.spinner("Search Agent working…"):
            try:
                sr = build_search_agent().invoke({
                    "messages": [("user", f"Find recent, reliable and detailed information about: {t}")]
                })
                results["search"] = sr["messages"][-1].content
            except Exception as e:
                results["search"] = f"[Search error: {e}]"
            st.session_state.timestamps["search"] = datetime.now().strftime("%H:%M:%S")
        st.rerun()

    # Step 2: Reader
    elif "reader" not in results:
        with st.spinner("Reader Agent scraping…"):
            try:
                rr = build_reader_agent().invoke({
                    "messages": [("user",
                        f"Based on search results about '{t}', pick the most relevant URL "
                        f"and scrape it.\n\nSearch Results:\n{results['search'][:800]}"
                    )]
                })
                results["reader"] = rr["messages"][-1].content
            except Exception as e:
                results["reader"] = f"[Reader error: {e}]"
            st.session_state.timestamps["reader"] = datetime.now().strftime("%H:%M:%S")
        st.rerun()

    # Step 3: Writer
    elif "writer" not in results:
        with st.spinner("Writer Chain drafting…"):
            try:
                results["writer"] = writer_chain.invoke({
                    "topic": t,
                    "research": f"SEARCH:\n{results['search']}\n\nCONTENT:\n{results['reader']}"
                })
            except Exception as e:
                results["writer"] = f"[Writer error: {e}]"
            st.session_state.timestamps["writer"] = datetime.now().strftime("%H:%M:%S")
        st.rerun()

    # Step 4: Critic
    elif "critic" not in results:
        with st.spinner("Critic Chain reviewing…"):
            try:
                results["critic"] = critic_chain.invoke({"report": results["writer"]})
            except Exception as e:
                results["critic"] = f"[Critic error: {e}]"
            st.session_state.timestamps["critic"] = datetime.now().strftime("%H:%M:%S")
        st.rerun()

    # Step 5: Finish
    else:
        st.session_state.running = False
        st.session_state.done = True
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  RESULTS
# ══════════════════════════════════════════════════════════════════════════════
r = st.session_state.results

if r and st.session_state.done:
    st.markdown('<div style="height:1px;background:var(--border);margin:1.2rem 0;"></div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:var(--mono);font-size:0.58rem;letter-spacing:0.16em;
         color:var(--muted);margin-bottom:10px;">RESULTS</div>
    """, unsafe_allow_html=True)

    if "search" in r:
        with st.expander("🔍 Search agent output"):
            st.markdown(f'<div style="font-family:var(--mono);font-size:0.74rem;'
                        f'color:var(--dim);line-height:1.8;white-space:pre-wrap;">'
                        f'{r["search"]}</div>', unsafe_allow_html=True)

    if "reader" in r:
        with st.expander("📄 Reader agent output"):
            st.markdown(f'<div style="font-family:var(--mono);font-size:0.74rem;'
                        f'color:var(--dim);line-height:1.8;white-space:pre-wrap;">'
                        f'{r["reader"]}</div>', unsafe_allow_html=True)

    if "writer" in r:
        st.markdown("""
        <div style="background:var(--surface);border:1px solid rgba(99,102,241,0.18);
             border-left:3px solid var(--accent);border-radius:0 10px 10px 0;
             padding:1.3rem 1.5rem;margin:6px 0;">
          <div style="font-family:var(--mono);font-size:0.58rem;letter-spacing:0.14em;
               color:var(--accent);margin-bottom:0.9rem;">RESEARCH REPORT</div>
        """, unsafe_allow_html=True)
        st.markdown(r["writer"])
        st.markdown("</div>", unsafe_allow_html=True)
        st.download_button(
            label="Download report (.md)",
            data=r["writer"],
            file_name=f"neurondepth_{int(time.time())}.md",
            mime="text/markdown",
        )

    if "critic" in r:
        st.markdown("""
        <div style="background:var(--surface);border:1px solid rgba(34,197,94,0.18);
             border-left:3px solid var(--green);border-radius:0 10px 10px 0;
             padding:1.3rem 1.5rem;margin:8px 0;">
          <div style="font-family:var(--mono);font-size:0.58rem;letter-spacing:0.14em;
               color:var(--green);margin-bottom:0.9rem;">CRITIC FEEDBACK</div>
        """, unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="text-align:center;margin-top:3.5rem;">
  <span style="font-family:var(--mono);font-size:0.58rem;letter-spacing:0.1em;color:var(--muted);">
    NeuronDepth · Multi-Agent Research Pipeline
  </span>
</div>
""", unsafe_allow_html=True)