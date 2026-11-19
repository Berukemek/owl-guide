"""Pulls live events from the public KSU calendar RSS feed (no login needed)."""
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from html import unescape

FEED_URL = "https://calendar.kennesaw.edu/calendar/1.xml"


def _clean(html_text: str, limit: int = 220) -> str:
    text = re.sub(r"<[^>]+>", " ", unescape(html_text or ""))
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("View on site", "").replace("Email this event", "").strip(" |")
    return text[:limit] + ("…" if len(text) > limit else "")


def parse_feed(xml_bytes: bytes, now: datetime, days_ahead: int = 7, max_events: int = 60):
    """Return upcoming events as a list of dicts, soonest first."""
    root = ET.fromstring(xml_bytes)
    events = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        desc = _clean(item.findtext("description") or "")
        pub = item.findtext("pubDate")
        try:
            start = parsedate_to_datetime(pub) if pub else None
        except (TypeError, ValueError):
            start = None
        if start is None:
            continue
        # Compare in the feed's own timezone
        now_local = now.astimezone(start.tzinfo) if now.tzinfo else now.replace(tzinfo=start.tzinfo)
        if not (now_local - timedelta(hours=3) <= start <= now_local + timedelta(days=days_ahead)):
            continue
        # Titles look like "Nov 18, 2026: Event name at Building" – drop the date prefix
        name = re.sub(r"^[A-Z][a-z]{2} \d{1,2}, \d{4}: ", "", title)
        events.append({"start": start, "title": name, "desc": desc, "link": link})
    events.sort(key=lambda e: e["start"])
    return events[:max_events]


def fetch_events(now: datetime, days_ahead: int = 7):
    req = urllib.request.Request(FEED_URL, headers={"User-Agent": "KSU-Owl-Bot (hackathon project)"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return parse_feed(resp.read(), now, days_ahead)


def events_to_text(events) -> str:
    if not events:
        return "No upcoming events found in the KSU calendar feed."
    lines = []
    for e in events:
        when = e["start"].strftime("%a %b %d, %I:%M %p").replace(" 0", " ")
        lines.append(f"- {when} | {e['title']} | {e['desc']} | {e['link']}")
    return "\n".join(lines)
