"""Owl Guide – a KSU campus chatbot (food, locations, events, clubs)."""
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus
from zoneinfo import ZoneInfo

import anthropic
import streamlit as st

from events import events_to_text, fetch_events

DATA_DIR = Path(__file__).parent / "data"
TZ = ZoneInfo("America/New_York")
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")

CAMPUSES = {
    "Kennesaw": "1000 Chastain Rd NW, Kennesaw, GA 30144",
    "Marietta": "1100 South Marietta Pkwy SE, Marietta, GA 30060",
}

STARTERS = [
    "What time does the dining hall close?",
    "What time does the library close?",
    "Which study rooms are available on the Kennesaw Campus?",
    "When are final exams?",
    "What tech clubs are on campus?",
    "What events are happening this week?",
]


def maps_link(query: str) -> str:
    return f"https://www.google.com/maps/search/?api=1&query={quote_plus(query)}"


@st.cache_data
def load_knowledge() -> str:
    parts = []
    for f in sorted(DATA_DIR.glob("*.md")):
        parts.append(f"<file name='{f.name}'>\n{f.read_text()}\n</file>")
    return "\n\n".join(parts)


@st.cache_data(ttl=1800, show_spinner=False)
def load_events(day_key: str) -> str:
    # day_key only exists so the cache refreshes each day
    try:
        return events_to_text(fetch_events(datetime.now(TZ), days_ahead=7))
    except Exception as exc:  # feed down / no internet – the bot still works
        return f"(Live events feed unavailable right now: {exc}. Point users to https://calendar.kennesaw.edu and Owl Life.)"


def build_system_prompt(campus: str) -> str:
    now = datetime.now(TZ)
    campus_line = (
        f"The user mostly uses the {campus} Campus; favor it but mention the other campus when useful."
        if campus != "Both"
        else "The user uses both campuses; say which campus each answer applies to."
    )
    return f"""You are Owl Guide, a friendly assistant for Kennesaw State University (KSU) students.
You help with: food on campus, campus locations (and spots near campus), libraries and study rooms,
academic calendar dates (breaks, finals, registration), events, and clubs, for BOTH the Kennesaw and Marietta campuses.

Current date and time: {now.strftime('%A, %B %d, %Y, %I:%M %p')} (Eastern Time).
{campus_line}

RULES
- Answer ONLY from the KSU information below.
- If you can't answer a question (the info isn't below, or it's off-topic), reply with this message:
  "Sorry, I'm not able to answer that question at this time, but I'd be more than happy to help with any other questions! 🦉"
  If a KSU page or office below clearly covers the topic, you can add one line pointing to it. Never guess.
- For "open now" or "tonight" questions, compare the current day/time to the hours, and check the closures list first (closures override regular hours).
TONE
- Be warm, upbeat and encouraging, like a helpful upperclassman. Use the student's words and a casual, friendly voice.
- Lead with the answer, use short bullets, and keep most replies under 120 words.
- One emoji is fine when it fits (🦉 🍕 📚 🎉); don't overdo it.
- You can end with a short friendly line or a helpful follow-up offer, e.g. "Want spots that are open later?"

CONTENT
- For "where is…" questions, say which campus it's on and describe where it is in plain words: which buildings
  are next to it or nearby (e.g. "on the north edge of the Campus Green, right next to The Commons"), and roughly
  how long a walk it is from a well-known spot like the Student Center. Mention the closest parking when it helps.
  Walking times are estimates, so always say "about". Don't mention building numbers or map grid codes unless asked.
- For "how do I get from X to Y" questions, use the layout and walking times to give simple directions.
- When you mention a building or place, add a Google Maps link in this format:
  https://www.google.com/maps/search/?api=1&query=<place name + Kennesaw State University, URL-encoded with +>
- For places NEAR campus (coffee, groceries, pharmacies, restaurants off campus), you don't have a verified list.
  Give a Google Maps search link instead, e.g. {maps_link('coffee near ' + CAMPUSES['Kennesaw'])}
  Use the right campus address: Kennesaw = {CAMPUSES['Kennesaw']}; Marietta = {CAMPUSES['Marietta']}.
- If a question applies to both campuses ("the dining hall", "the library") and the user hasn't picked one, answer for BOTH, labeled by campus.
- Study room availability changes constantly and you CANNOT see it. Never claim a room is free. Give the live booking link for the right campus.
- For dates (finals, breaks, registration), use today's date to pick the current or upcoming semester.
- For events, use the live calendar below and include the event link. For clubs, say the full list of 300+ clubs is on Owl Life.
- ALWAYS end every factual answer with a line in this exact format:
  🔗 **More details:** [Name of KSU page](URL)
  Use the most specific KSU page URL that appears in the KSU information below (each file lists its sources, and
  many items have their own link). Don't make up URLs. If the answer covers two topics, you can list two links.
- Only answer KSU campus-life questions. For anything else, use the "Sorry, I'm not able to answer…" message above.

KSU INFORMATION
{load_knowledge()}

<file name='live_events_next_7_days'>
{load_events(now.strftime('%Y-%m-%d'))}
</file>
"""


def get_client() -> anthropic.Anthropic:
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        try:
            key = st.secrets["ANTHROPIC_API_KEY"]
        except Exception:
            key = None
    if not key:
        st.error("Add ANTHROPIC_API_KEY to .streamlit/secrets.toml or your environment, then restart.")
        st.stop()
    return anthropic.Anthropic(api_key=key)


def stream_answer(client, system: str, history: list[dict]):
    with client.messages.stream(model=MODEL, max_tokens=800, system=system, messages=history) as stream:
        for text in stream.text_stream:
            yield text


# ---------------- UI ----------------
st.set_page_config(page_title="Owl Guide – KSU Campus Assistant", page_icon="🦉", layout="centered")

with st.sidebar:
    st.markdown("## 🦉 Owl Guide")
    st.caption("Your AI guide to food, places, events and clubs at Kennesaw State.")
    campus = st.radio("My campus", ["Both", "Kennesaw", "Marietta"], horizontal=True)

    st.markdown("#### 📚 Book a study room")
    st.markdown(
        "- [Kennesaw (Sturgis Library)](https://kennesaw.libcal.com/reserve/studyroomsK)\n"
        "- [Marietta (Johnson Library)](https://kennesaw.libcal.com/reserve/studyroomsM)"
    )

    st.markdown("#### Near campus")
    addr = CAMPUSES.get(campus, CAMPUSES["Kennesaw"])
    for label, q in [("☕ Coffee", "coffee"), ("🍔 Food", "restaurants"), ("🛒 Groceries", "grocery store"),
                     ("💊 Pharmacy", "pharmacy"), ("📚 Study spots", "cafe with wifi")]:
        st.markdown(f"[{label}]({maps_link(f'{q} near {addr}')})")

    st.markdown("#### Official links")
    st.markdown(
        "- [Dining hours](https://campus.kennesaw.edu/offices-services/dining/hours-locations.php)\n"
        "- [Campus map](https://maps.kennesaw.edu/)\n"
        "- [Academic calendar](https://campus.kennesaw.edu/current-students/registrar/academic-calendars)\n"
        "- [Library hours](https://campus.kennesaw.edu/offices-services/library/about/hours.php)\n"
        "- [Events calendar](https://calendar.kennesaw.edu)\n"
        "- [Owl Life (clubs)](https://owllife.kennesaw.edu)"
    )
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

st.title("🦉 Owl Guide")
st.caption("Kennesaw + Marietta campuses: food, buildings, library and study rooms, key dates, events and clubs.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Starter questions (shown until the first message)
clicked = None
if not st.session_state.messages:
    cols = st.columns(2)
    for i, q in enumerate(STARTERS):
        if cols[i % 2].button(q, use_container_width=True):
            clicked = q

for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar="🦉" if m["role"] == "assistant" else None):
        st.markdown(m["content"])

prompt = st.chat_input("Ask Owl Guide…") or clicked
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    client = get_client()
    system = build_system_prompt(campus)
    history = st.session_state.messages[-11:]  # last few turns; odd count so it starts with a user message
    with st.chat_message("assistant", avatar="🦉"):
        try:
            reply = st.write_stream(stream_answer(client, system, history))
        except anthropic.APIError as exc:
            reply = ("Sorry, I'm not able to answer that question at this time, but I'd be more than happy "
                     "to help with any other questions! 🦉")
            st.markdown(reply)
            print(f"[Owl Guide] API error: {exc!r}")  # shows in the terminal for debugging
    st.session_state.messages.append({"role": "assistant", "content": reply})
    if clicked:
        st.rerun()
