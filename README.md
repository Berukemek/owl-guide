# 🦉 Owl Guide – AI Campus Assistant for Kennesaw State

**Live app:** [ksu-owl-guide.streamlit.app](https://ksu-owl-guide.streamlit.app) · Built by Beruke Mekonnen (Cybersecurity, KSU '28)

Owl Guide is an AI chatbot that answers Kennesaw State students' everyday campus questions in one place, across both the Kennesaw and Marietta campuses. KSU's campus information is spread across six or more websites, so Owl Guide brings it together and links every answer back to the official source.

## What it does

| Topic | Example question | What Owl Guide does |
|---|---|---|
| Food | "What's open for food right now?" | Compares the current time to every dining location's hours, including holiday closures |
| Buildings | "Where's the Buruss building?" | Handles typos, describes nearby landmarks and gives approximate walking time and a Maps link |
| Library | "What time does the library close?" | Gives hours for both campuses and links to the right study room booking page |
| Academic dates | "When are final exams?" | Picks the current semester from today's date and links to the exam schedule |
| Events | "What's happening this week?" | Pulls upcoming events live from KSU's public calendar feed |
| Clubs | "What tech clubs are on campus?" | Suggests clubs and competition teams from public KSU pages |

## How it works

```
Official KSU data (data/*.md) ─┐
Live events (public RSS feed) ─┼─▶ Claude (grounded instructions + current date/time) ─▶ Answer + source link
Student's question ────────────┘
```

- **Grounded answers.** Claude, Anthropic's large language model, receives a knowledge base built from official public KSU pages along with each question. It is instructed to answer only from that data. The data is small enough to pass directly to the model, so no vector database is needed.
- **Cited sources.** Every factual answer ends with a link to the KSU page it came from, so students can verify it.
- **No guessing.** When the answer isn't in the data, or the question is off-topic, it replies: *"Sorry, I'm not able to answer that question at this time, but I'd be more than happy to help with any other questions!"*
- **Time awareness.** The current Eastern time is included in each request, so "open now" and "when are finals" questions resolve correctly.
- **Live events.** `events.py` reads KSU's public calendar RSS feed and caches it for 30 minutes.

## Security and privacy

- **Secrets management.** The Claude API key is stored in Streamlit's encrypted secrets store (or a local `secrets.toml`). `.gitignore` excludes `secrets.toml`, and no key has ever been committed to this repository.
- **Public data only.** All data comes from public KSU web pages. Owl Guide does not scrape login-protected systems; for club data behind a NetID login, I contacted KSU Student Activities to request permission.
- **No personal data.** The app has no accounts and stores no student information. Chat history exists only in the browser session.

## Tech stack

Python · Streamlit · Claude API (Anthropic) · Streamlit Community Cloud

## Run it locally

```bash
git clone https://github.com/Berukemek/owl-guide.git
cd owl-guide
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml and add: ANTHROPIC_API_KEY = "your-key"
streamlit run app.py
```

Then open http://localhost:8501. To use a different Claude model, set the `ANTHROPIC_MODEL` environment variable.

## Project structure

```
app.py            Chat interface, system prompt and Claude API calls
events.py         Live KSU events from the public calendar RSS feed
data/             Knowledge base: dining, campus and directions, library, academic calendar, clubs
.streamlit/       Theme (KSU black and gold) and secrets template
```

## Limitations and next steps

- Study room availability isn't live; the bot links to the booking pages instead.
- Club coverage is limited to public pages (about 35 clubs, not the full 300+ on Owl Life).
- Dining hours and dates are updated by hand each semester; walking times are estimates.
- Next: live study room availability, daily dining menus, the full club list (with permission) and a feedback button.

*Owl Guide is a student project and is not an official Kennesaw State University service.*
