# 🦉 Owl Guide – KSU Campus Assistant

An AI chatbot for Kennesaw State students: **food on campus, campus locations (plus spots near campus), events and clubs**, for both the Kennesaw and Marietta campuses.

## How it works
- `data/*.md` holds the KSU info (dining hours, buildings, clubs). The data is small, so the whole thing goes into the prompt. No vector database needed.
- `events.py` pulls **live events** from the public KSU calendar RSS feed, so events are always current.
- The current date and time go into the prompt, so "What's open right now?" actually works, including holiday closures.
- Location answers include Google Maps links. "Near campus" questions return a Maps search around the right campus address.

## Run it (about 5 minutes)
```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # then paste your Anthropic API key
streamlit run app.py
```
Open http://localhost:8501.

To use a different Claude model, set `ANTHROPIC_MODEL` (default: `claude-sonnet-5-5`).

## Deploy for free (do this early!)
1. Push this folder to a GitHub repo. `secrets.toml` is git-ignored.
2. Go to share.streamlit.io, click **New app**, and pick the repo with `app.py`.
3. Under **Advanced settings → Secrets**, paste `ANTHROPIC_API_KEY = "sk-ant-..."`.

## Updating the data
Edit the Markdown files in `data/`. Any new `.md` file you add there is picked up automatically. Ideas:
- Paste more clubs from Owl Life into `clubs.md` (the full list needs a NetID login).
- Add Spring 2027 dining hours once KSU posts them.

## Test questions and expected answers
Run these after every data change. On Wed Nov 18, 2026, the bot should say:

| Question | Expected answer |
|---|---|
| What time does the dining hall close? | Today (Wed): The Commons (Kennesaw) and Stingers (Marietta) both close at 9 PM. Both are closed Nov 21–28 for Thanksgiving. |
| Where is the Academic Building located? | Academic Building (H), Marietta Campus, with a Maps link. It may also mention the Academic Learning Center in Kennesaw. |
| What time does the library close? | Mon–Thu 11 PM (Fri 6 PM, Sat 6 PM, Sun 9 PM). Sturgis = Kennesaw, Johnson = Marietta. |
| What tech clubs are on campus? | AI Club, OWL Cyber Club, Game Design Club, Girls Who Code, SwAT, IEEE-CS, ADSO and more, plus a pointer to Owl Life. |
| What study rooms are available on the Kennesaw Campus? | It can't see live availability, so it gives the booking link https://kennesaw.libcal.com/reserve/studyroomsK |
| Where is the Buruss building? | Burruss Building (BB) [560], Kennesaw Campus. McAlister's is inside. Includes a Maps link. |
| When is fall break? | Nov 23–29 (Thanksgiving week, no classes). |
| When are final exams? | Fall 2026: Dec 8–14. Includes the exam schedule PDF link. |
| When is the last day of classes? | Mon Dec 7 for 14-week classes (7-week II: Dec 2). |
| When is the last day to register for classes? | Spring 2027: Fri Jan 15, 2027 at 11:45 PM. |

## Demo script
1. "What's open for food right now?" shows time awareness.
2. "I'm at the library at Marietta and hungry. What's closest?" shows combined location and food reasoning.
3. "What events are happening this week?" shows the live calendar.
4. "I like robotics. What should I join?" shows club matching.
5. "Can you do my calculus homework?" gets the friendly "Sorry, I'm not able to answer that question at this time…" reply.
