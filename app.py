"""Personalized Study Plan Generator - single-file Streamlit app.
Run:  pip install streamlit requests   then   streamlit run app.py
"""
import json
import os
from html import escape

import requests
import streamlit as st

st.set_page_config(page_title="Study Plan Generator", page_icon="📚", layout="wide")

CURRICULUM = json.loads(r'''{
  "subject": "Python Programming",
  "topics": [
    {"id":"t1","name":"Variables & Data Types","difficulty":1,"hours":2,"prereqs":[],"objective":"Store and manipulate basic values"},
    {"id":"t2","name":"Operators & Input/Output","difficulty":1,"hours":2,"prereqs":["t1"],"objective":"Read input and compute results"},
    {"id":"t3","name":"Conditionals","difficulty":1,"hours":2,"prereqs":["t2"],"objective":"Make decisions with if/elif/else"},
    {"id":"t4","name":"Loops","difficulty":2,"hours":3,"prereqs":["t3"],"objective":"Repeat work with for and while"},
    {"id":"t5","name":"Functions","difficulty":2,"hours":3,"prereqs":["t4"],"objective":"Write reusable functions"},
    {"id":"t6","name":"Lists & Tuples","difficulty":2,"hours":3,"prereqs":["t4"],"objective":"Work with ordered collections"},
    {"id":"t7","name":"Dictionaries & Sets","difficulty":2,"hours":3,"prereqs":["t6"],"objective":"Use key-value and unique collections"},
    {"id":"t8","name":"File Handling","difficulty":2,"hours":2,"prereqs":["t5"],"objective":"Read and write files"},
    {"id":"t9","name":"OOP Basics","difficulty":3,"hours":4,"prereqs":["t5","t7"],"objective":"Model problems with classes"},
    {"id":"t10","name":"Error Handling & Modules","difficulty":3,"hours":3,"prereqs":["t5"],"objective":"Handle exceptions and organise code"}
  ]
}''')
PRESETS = json.loads(r'''[
  {"label":"Limited daily time","dailyHours":1,"daysPerWeek":4,"weeks":4,"goals":["t9"],"completed":[],"weak":[]},
  {"label":"Specific goal: file handling","dailyHours":2,"daysPerWeek":5,"weeks":2,"goals":["t8"],"completed":[],"weak":[]},
  {"label":"Full curriculum","dailyHours":2,"daysPerWeek":5,"weeks":4,"goals":["t9","t8","t10"],"completed":[],"weak":[]},
  {"label":"Re-plan after progress","dailyHours":2,"daysPerWeek":4,"weeks":3,"goals":["t9","t8","t10"],"completed":["t1","t2","t3"],"weak":["t4"]}
]''')
CSS = r'''@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
html,body,[class*="css"],.stApp{font-family:'Inter',system-ui,sans-serif}
[data-testid="stAppViewContainer"]{background:linear-gradient(135deg,#0b1026,#1a1446 50%,#0d2a3f)}
[data-testid="stHeader"]{background:transparent}
#MainMenu,footer{visibility:hidden}
.block-container{position:relative;z-index:1;max-width:1150px;padding-top:2.2rem}
.blob{position:fixed;border-radius:50%;filter:blur(80px);opacity:.45;z-index:0;pointer-events:none;animation:float 18s ease-in-out infinite}
.b1{width:380px;height:380px;background:#6c5ce7;top:-90px;left:-70px}
.b2{width:340px;height:340px;background:#00cec9;bottom:-80px;right:-40px;animation-delay:-6s}
.b3{width:260px;height:260px;background:#fd79a8;top:45%;left:55%;animation-delay:-11s;opacity:.28}
@keyframes float{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(60px,40px) scale(1.15)}}
.hero h1{font-size:2.6rem;font-weight:800;margin:0;background:linear-gradient(90deg,#fff,#a29bfe,#55efc4,#fff);background-size:250% 100%;-webkit-background-clip:text;background-clip:text;color:transparent;animation:shine 8s linear infinite}
@keyframes shine{to{background-position:250% 0}}
.hero p{color:#b8c0e0;margin:.2rem 0 1.4rem}
[data-testid="stVerticalBlockBorderWrapper"]{background:rgba(255,255,255,.07);backdrop-filter:blur(18px) saturate(150%);-webkit-backdrop-filter:blur(18px) saturate(150%);border:1px solid rgba(255,255,255,.18)!important;border-radius:20px;box-shadow:0 8px 32px rgba(0,0,0,.35)}
[data-baseweb="select"]>div,[data-baseweb="input"],[data-baseweb="base-input"]{background:rgba(255,255,255,.08)!important;border-color:rgba(255,255,255,.2)!important;border-radius:12px!important}
.stButton>button,.stDownloadButton>button{border-radius:12px;border:1px solid rgba(255,255,255,.25);background:rgba(255,255,255,.1);color:#fff;transition:transform .2s,box-shadow .2s}
.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-2px);box-shadow:0 8px 22px rgba(124,108,240,.45);border-color:#fff}
button[kind="primary"],button[data-testid="stBaseButton-primary"]{background:linear-gradient(135deg,#6c5ce7,#00b8d4)!important;border:0!important;font-weight:700;background-size:200%}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:12px}
.tile,.card,.note,.empty{background:rgba(255,255,255,.08);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border:1px solid rgba(255,255,255,.16);border-radius:16px}
.tile{padding:12px 14px;animation:up .6s both}
.tile .num{font-size:1.7rem;font-weight:800}.tile .lbl{color:#b8c0e0;font-size:.8rem}
.bar{height:8px;border-radius:99px;background:rgba(255,255,255,.12);overflow:hidden;margin:4px 0 6px}
.bar>i{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,#6c5ce7,#00cec9);animation:grow 1.3s ease-out both}
@keyframes grow{from{width:0}}
.note{padding:10px 14px;margin-bottom:12px;animation:up .6s both}
.note.warn{border-color:#fdcb6e;background:rgba(253,203,110,.12)}
.week{border-left:2px solid rgba(255,255,255,.18);margin:18px 0 0 14px;padding-left:24px;position:relative}
.wk-head{font-weight:700;font-size:1.1rem;margin-bottom:10px}.wk-head small{color:#b8c0e0;font-weight:400;margin-left:8px}
.dot{position:absolute;left:-15px;top:-2px;width:28px;height:28px;border-radius:50%;display:grid;place-items:center;font-weight:700;font-size:.85rem;background:linear-gradient(135deg,#6c5ce7,#00cec9);animation:pulse 2.4s infinite}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(108,92,231,.7)}70%,100%{box-shadow:0 0 0 12px rgba(108,92,231,0)}}
.card{padding:14px 16px;margin-bottom:12px;animation:up .6s both cubic-bezier(.2,.8,.2,1);transition:transform .25s,box-shadow .25s,border-color .25s}
.card:hover{transform:translateY(-4px);box-shadow:0 12px 32px rgba(108,92,231,.4);border-color:rgba(255,255,255,.4)}
@keyframes up{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
.top{display:flex;justify-content:space-between;gap:10px;font-weight:700}.hrs{color:#55efc4;white-space:nowrap}
.chip{display:inline-block;font-size:.72rem;padding:2px 9px;border-radius:99px;margin:6px 6px 4px 0;border:1px solid}
.d1{color:#55efc4;border-color:#55efc4}.d2{color:#ffeaa7;border-color:#ffeaa7}.d3{color:#ff7675;border-color:#ff7675}.rev{color:#a29bfe;border-color:#a29bfe}
.card ul{margin:4px 0 0;padding-left:18px;color:#dfe4ff}.card li{margin:2px 0}
.tip{color:#b8c0e0;font-size:.88rem;margin-top:8px}
.empty{padding:48px 20px;text-align:center;border-style:dashed;color:#b8c0e0}
.empty .ico{font-size:3rem;display:block;animation:float2 3s ease-in-out infinite}
@keyframes float2{50%{transform:translateY(-10px)}}
.stApp,.stApp p,.stApp li,.stApp span,.stApp label,[data-testid="stWidgetLabel"] *,[data-testid="stMarkdownContainer"] *{color:#eef1ff}
h1,h2,h3,h4,h5,h6,[data-testid="stHeading"] *,[data-testid="stMarkdownContainer"] h4{color:#ffffff!important}
[data-testid="stCaptionContainer"] *,.stCaption *{color:#b8c0e0!important}
.hero h1{color:transparent!important}.hero p{color:#b8c0e0!important}
.hrs{color:#55efc4!important}.tile .lbl,.wk-head small,.tip,.empty,.empty *{color:#b8c0e0!important}
.d1{color:#55efc4!important}.d2{color:#ffeaa7!important}.d3{color:#ff7675!important}.rev{color:#a29bfe!important}
[data-baseweb="select"] *,[data-baseweb="input"] input,[data-baseweb="base-input"] input{color:#ffffff!important}
[data-baseweb="select"] svg{fill:#ffffff}
.stButton>button *,.stDownloadButton>button *{color:#ffffff!important}
@media(max-width:800px){.stats{grid-template-columns:1fr}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
'''

# ---------------- planner (deterministic part) ----------------


def _half(h):
    return max(0.5, round(h * 2) / 2)


def build_skeleton(curriculum, s):
    by_id = {t["id"]: t for t in curriculum["topics"]}
    done, weak = set(s["completed"]), set(s["weak"])

    # 1. Scope = goals + all their prerequisites; finished topics are skipped unless marked weak
    scope = set()

    def add(tid):
        if tid in by_id and tid not in scope:
            scope.add(tid)
            for p in by_id[tid]["prereqs"]:
                add(p)

    for g in s["goals"]:
        add(g)
    ids = [t for t in scope if t not in done or t in weak]

    # 2. Prerequisite-safe order (topological), easiest available topic first
    order, placed = [], {t for t in scope if t not in ids}
    while len(order) < len(ids):
        ready = [t for t in ids if t not in order
                 and all(p in placed or p not in scope for p in by_id[t]["prereqs"])]
        if not ready:
            break
        ready.sort(key=lambda t: (by_id[t]["difficulty"], t))
        order.append(ready[0])
        placed.add(ready[0])

    # 3. Time budget: weak topics get +25%, everything scaled down if it does not fit
    weekly = s["dailyHours"] * s["daysPerWeek"]
    total = weekly * s["weeks"]
    raw = [by_id[t]["hours"] * (1.25 if t in weak else 1) for t in order]
    need = sum(raw)
    scale = total / need if need > total else 1
    warnings = []
    if scale < 1:
        warnings.append(f"Needs about {need:.1f}h but only {total:.1f}h is available. "
                        f"Time per topic was reduced by {round((1 - scale) * 100)}%. Consider more weeks or hours.")
    if scale < 0.5:
        warnings.append("Time is very tight, so this plan covers topics at overview level only.")

    items, cum = [], 0.0
    for t, r in zip(order, raw):
        hours = _half(r * scale)
        items.append({"topicId": t, "name": by_id[t]["name"], "difficulty": by_id[t]["difficulty"],
                      "objective": by_id[t]["objective"], "hours": hours,
                      "week": min(s["weeks"], int(cum // weekly) + 1), "revision": t in weak})
        cum += hours
    return {"items": items, "totalHours": total, "plannedHours": cum, "warnings": warnings}


def merge_activities(skeleton, ai):
    """Validate the AI output against the fixed schedule. Returns a plan dict or None."""
    if not isinstance(ai, dict) or not isinstance(ai.get("items"), list):
        return None
    ai_map = {x.get("topicId"): x for x in ai["items"] if isinstance(x, dict)}
    merged = []
    for it in skeleton["items"]:
        a = ai_map.get(it["topicId"])
        if not a or not isinstance(a.get("activities"), list) or not a["activities"]:
            return None
        merged.append({**it, "activities": [str(x) for x in a["activities"][:4]], "tip": str(a.get("tip", ""))})
    return {"summary": str(ai.get("summary", "")), "items": merged}


def fallback_plan(skeleton):
    return {"summary": "Plan built from your curriculum and available time.",
            "items": [{**it,
                       "activities": [f"Read notes on {it['name']}", "Solve 5 practice exercises",
                                      "Self-quiz and review mistakes"],
                       "tip": "Marked weak: focus on mistakes you made before." if it["revision"] else ""}
                      for it in skeleton["items"]]}


# ---------------- LLM call ----------------


def _secret(name, default=None):
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return os.environ.get(name, default)


def ask_gemini(skeleton, s):
    key = _secret("GEMINI_API_KEY")
    if not key:
        raise RuntimeError("GEMINI_API_KEY missing")
    model = _secret("GEMINI_MODEL", "gemini-2.0-flash")
    prompt = (
        "You are a study-plan assistant. The schedule below is FIXED. Do not add, remove or reorder topics "
        "or change hours.\nFor each topic write 3 short, concrete learning activities that fit its hours and "
        'difficulty (1 easy - 3 hard). If "revision" is true, focus on revising weak areas.\n'
        'Return ONLY JSON: {"summary": "2 motivating sentences", "items": [{"topicId": "...", '
        '"activities": ["...","...","..."], "tip": "one short tip"}]}\n'
        f"Student: {json.dumps({k: s[k] for k in ('dailyHours', 'daysPerWeek', 'weeks')})}\n"
        f"Schedule: {json.dumps(skeleton['items'])}"
    )
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    r = requests.post(url, params={"key": key}, timeout=25, json={
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.4}})
    r.raise_for_status()
    return json.loads(r.json()["candidates"][0]["content"]["parts"][0]["text"])


# ---------------- UI ----------------

st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
st.markdown('<div class="blob b1"></div><div class="blob b2"></div><div class="blob b3"></div>', unsafe_allow_html=True)

NAMES = {t["id"]: t["name"] for t in CURRICULUM["topics"]}
LABELS = [p["label"] for p in PRESETS]
LEVEL = {1: "Easy", 2: "Medium", 3: "Hard"}


def load_preset():
    p = PRESETS[LABELS.index(st.session_state.preset)]
    st.session_state.update(daily=float(p["dailyHours"]), days=p["daysPerWeek"], weeks=p["weeks"],
                            goals=p["goals"], done=p["completed"], weak=p["weak"])
    st.session_state.pop("plan", None)


def vote(kind):
    st.session_state.votes[kind] += 1
    st.session_state.voted = True


def card(i, n):
    rev = '<span class="chip rev">Revision</span>' if i["revision"] else ""
    acts = "".join(f"<li>{escape(a)}</li>" for a in i["activities"])
    tip = f'<div class="tip">💡 {escape(i["tip"])}</div>' if i["tip"] else ""
    return (f'<div class="card" style="animation-delay:{n * 0.09:.2f}s"><div class="top"><span>{escape(i["name"])}</span>'
            f'<span class="hrs">{i["hours"]}h</span></div><span class="chip d{i["difficulty"]}">{LEVEL[i["difficulty"]]}</span>{rev}'
            f'<ul>{acts}</ul>{tip}</div>')


def plan_markdown(plan):
    out = [f"# Study plan: {CURRICULUM['subject']}", "", plan["summary"], ""]
    for i in plan["items"]:
        out += [f"## Week {i['week']}: {i['name']} ({i['hours']}h)"] + [f"- {a}" for a in i["activities"]] + [""]
    return "\n".join(out)


if "daily" not in st.session_state:
    st.session_state.preset = LABELS[0]
    load_preset()
    st.session_state.votes = {"up": 0, "down": 0}
    st.session_state.voted = False

st.markdown(f'<div class="hero"><h1>Study Plan Generator</h1><p>{CURRICULUM["subject"]} · tell us your goal and time, get an adaptive plan in seconds.</p></div>',
            unsafe_allow_html=True)

left, right = st.columns([1, 1.7], gap="large")

with left:
    with st.container(border=True):
        st.markdown("#### ✨ Your details")
        st.selectbox("Sample student", LABELS, key="preset", on_change=load_preset)
        c1, c2, c3 = st.columns(3)
        c1.number_input("Hours/day", min_value=0.5, step=0.5, key="daily")
        c2.number_input("Days/week", min_value=1, max_value=7, key="days")
        c3.number_input("Weeks", min_value=1, max_value=26, key="weeks")
        fmt = lambda i: NAMES[i]
        st.multiselect("🎯 Goal topics", list(NAMES), format_func=fmt, key="goals")
        st.multiselect("✅ Already completed", list(NAMES), format_func=fmt, key="done")
        st.multiselect("🔁 Need more practice", list(NAMES), format_func=fmt, key="weak")
        go = st.button("Generate / update plan", type="primary", use_container_width=True)

if go:
    s = {"dailyHours": st.session_state.daily, "daysPerWeek": st.session_state.days,
         "weeks": st.session_state.weeks, "goals": st.session_state.goals,
         "completed": st.session_state.done, "weak": st.session_state.weak}
    st.session_state.voted = False
    if not s["goals"]:
        st.session_state.plan = {"error": "Choose at least one goal topic."}
    else:
        sk = build_skeleton(CURRICULUM, s)
        if not sk["items"]:
            st.session_state.plan = {"error": "Nothing left to study for these goals. All topics are marked complete."}
        else:
            plan, source = None, "ai"
            with st.spinner("Crafting your plan…"):
                for _ in range(2):  # one retry, then fall back
                    try:
                        plan = merge_activities(sk, ask_gemini(sk, s))
                    except Exception:
                        plan = None
                    if plan:
                        break
            if not plan:
                plan, source = fallback_plan(sk), "fallback"
            st.session_state.plan = {**plan, "source": source, "warnings": sk["warnings"],
                                     "total": sk["totalHours"], "planned": sk["plannedHours"]}

with right:
    plan = st.session_state.get("plan")
    if not plan:
        st.markdown('<div class="empty"><span class="ico">🎓</span>Your plan will appear here.<br>Pick a sample student and press Generate.</div>',
                    unsafe_allow_html=True)
    elif "error" in plan:
        st.error(plan["error"])
    else:
        pct = min(100, round(plan["planned"] / plan["total"] * 100))
        weeks = sorted({i["week"] for i in plan["items"]})
        st.markdown(
            f'<div class="stats"><div class="tile"><div class="num">{len(plan["items"])}</div><div class="lbl">Topics</div></div>'
            f'<div class="tile" style="animation-delay:.1s"><div class="num">{plan["planned"]:g}h</div><div class="lbl">Planned of {plan["total"]:g}h</div></div>'
            f'<div class="tile" style="animation-delay:.2s"><div class="num">{len(weeks)}</div><div class="lbl">Weeks</div></div></div>'
            f'<div class="bar"><i style="width:{pct}%"></i></div>'
            f'<div class="note">{escape(plan["summary"])}</div>', unsafe_allow_html=True)
        if plan["source"] == "fallback":
            st.markdown('<div class="note warn">⚠️ AI was unavailable, so this plan was built from rules only.</div>', unsafe_allow_html=True)
        for w in plan["warnings"]:
            st.markdown(f'<div class="note warn">⚠️ {escape(w)}</div>', unsafe_allow_html=True)
        n = 0
        for week in weeks:
            items = [x for x in plan["items"] if x["week"] == week]
            html = f'<div class="week"><span class="dot">{week}</span><div class="wk-head">Week {week}<small>{sum(x["hours"] for x in items):g}h</small></div>'
            for i in items:
                html += card(i, n)
                n += 1
            st.markdown(html + "</div>", unsafe_allow_html=True)
        with st.container(border=True):
            v = st.session_state.votes
            total = v["up"] + v["down"]
            f1, f2, f3, f4 = st.columns([2.2, 1, 1, 2])
            if st.session_state.voted:
                f1.write("Thanks for your feedback 💜")
            else:
                f1.write("Is this plan relevant?")
                f2.button("👍 Yes", on_click=vote, args=("up",))
                f3.button("👎 No", on_click=vote, args=("down",))
            if total:
                f4.caption(f"Relevance: {round(v['up'] / total * 100)}% ({total} ratings)")
            st.download_button("⬇️ Download plan", plan_markdown(plan), file_name="study_plan.md")
