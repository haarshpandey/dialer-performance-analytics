"""
seed.py — generates a synthetic outbound-dialer dataset (dialer.db).

Domain: outbound sales dialing, inspired by CRM-embedded power dialers
(multi-line dialing, voicemail drops, spam-flag monitoring, speed-to-lead).

All data is SYNTHETIC and generated deterministically (seed=42). This is an
independent portfolio project — not affiliated with any dialer company.

Tables:
  reps   — sales reps
  leads  — leads entering the system (source, phone spam-flag status)
  calls  — every dial attempt (outcome, duration, lines used, voicemail drop)

Outcome probabilities are engineered to reflect real-world patterns:
  - contact rate decays as minutes-to-first-call grows (speed-to-lead)
  - spam-flagged numbers connect far less often
  - business hours (9am-5pm local) connect better than early/late
"""

import random
import sqlite3
from datetime import datetime, timedelta

random.seed(42)

DB = "dialer.db"
START = datetime(2026, 9, 1)  # 30-day window
DAYS = 30

REPS = [
    ("Maya Chen", "SMB"), ("Dev Patel", "SMB"), ("Sofia Reyes", "SMB"),
    ("Jake Thompson", "Mid-Market"), ("Aisha Khan", "Mid-Market"), ("Liam O'Connor", "Mid-Market"),
    ("Nora Haddad", "Enterprise"), ("Ethan Wright", "Enterprise"),
    ("Priya Nair", "SMB"), ("Carlos Mendez", "Mid-Market"),
    ("Grace Liu", "SMB"), ("Omar Farouk", "Enterprise"),
]

SOURCES = ["inbound_web", "purchased_list", "referral", "event"]
SOURCE_W = [0.35, 0.30, 0.20, 0.15]

OUTCOMES = ["connected", "voicemail", "no_answer", "busy", "failed"]


def pick_source():
    r = random.random()
    cum = 0.0
    for s, w in zip(SOURCES, SOURCE_W):
        cum += w
        if r <= cum:
            return s
    return SOURCES[-1]


def base_contact_prob(minutes_to_first, flagged, hour):
    """Probability a dial attempt results in a live connection."""
    # speed-to-lead decay
    if minutes_to_first <= 5:
        p = 0.34
    elif minutes_to_first <= 30:
        p = 0.27
    elif minutes_to_first <= 60:
        p = 0.21
    elif minutes_to_first <= 240:
        p = 0.15
    else:
        p = 0.10
    # spam-flagged numbers are answered far less
    if flagged:
        p *= 0.45
    # business hours connect better
    if 9 <= hour <= 17:
        p *= 1.25
    elif hour < 7 or hour >= 20:
        p *= 0.55
    return min(p, 0.9)


def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.executescript("""
        DROP TABLE IF EXISTS calls;
        DROP TABLE IF EXISTS leads;
        DROP TABLE IF EXISTS reps;
        CREATE TABLE reps (
            rep_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            team TEXT NOT NULL
        );
        CREATE TABLE leads (
            lead_id INTEGER PRIMARY KEY,
            source TEXT NOT NULL,
            created_at TEXT NOT NULL,
            phone_flagged INTEGER NOT NULL  -- 1 = spam-likely flag on the number
        );
        CREATE TABLE calls (
            call_id INTEGER PRIMARY KEY,
            rep_id INTEGER NOT NULL REFERENCES reps(rep_id),
            lead_id INTEGER NOT NULL REFERENCES leads(lead_id),
            call_at TEXT NOT NULL,
            lines_used INTEGER NOT NULL,      -- 1-3, multi-line dialing
            outcome TEXT NOT NULL,            -- connected | voicemail | no_answer | busy | failed
            duration_sec INTEGER NOT NULL,
            voicemail_dropped INTEGER NOT NULL, -- 1 = pre-recorded voicemail left
            minutes_to_first_call INTEGER,      -- NULL except on the lead's first attempt
            meeting_booked INTEGER NOT NULL DEFAULT 0
        );
    """)

    for i, (name, team) in enumerate(REPS, start=1):
        cur.execute("INSERT INTO reps VALUES (?, ?, ?)", (i, name, team))

    call_id = 0
    n_leads = 3000
    for lead_id in range(1, n_leads + 1):
        source = pick_source()
        flagged = 1 if random.random() < 0.15 else 0
        # leads arrive during working hours, weighted to mornings
        day = random.randrange(DAYS)
        hour = random.choice([8, 9, 9, 10, 10, 11, 11, 12, 13, 14, 14, 15, 15, 16, 17])
        created = START + timedelta(days=day, hours=hour, minutes=random.randrange(60))
        cur.execute("INSERT INTO leads VALUES (?, ?, ?, ?)",
                    (lead_id, source, created.isoformat(), flagged))

        # 1-4 attempts per lead; first attempt timing drives speed-to-lead
        n_attempts = random.choice([1, 1, 2, 2, 3, 4])
        first_delay_min = int(random.expovariate(1 / 45))  # mean ~45 min
        first_delay_min = min(first_delay_min, 24 * 60)
        attempt_time = created + timedelta(minutes=first_delay_min)

        for attempt in range(n_attempts):
            rep_id = random.randint(1, len(REPS))
            lines = random.choice([1, 1, 2, 2, 2, 3])
            p = base_contact_prob(
                first_delay_min if attempt == 0 else 9999, flagged, attempt_time.hour)
            r = random.random()
            if r < p:
                outcome = "connected"
            elif r < p + 0.28:
                outcome = "voicemail"
            elif r < p + 0.55:
                outcome = "no_answer"
            elif r < p + 0.68:
                outcome = "busy"
            else:
                outcome = "failed"

            duration = 0
            vm_drop = 0
            meeting = 0
            if outcome == "connected":
                duration = random.randint(45, 600)
                meeting = 1 if random.random() < 0.22 else 0
            elif outcome == "voicemail":
                duration = random.randint(20, 60)
                vm_drop = 1 if random.random() < 0.60 else 0

            call_id += 1
            cur.execute(
                """INSERT INTO calls
                   (call_id, rep_id, lead_id, call_at, lines_used, outcome,
                    duration_sec, voicemail_dropped, minutes_to_first_call, meeting_booked)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (call_id, rep_id, lead_id, attempt_time.isoformat(), lines, outcome,
                 duration, vm_drop,
                 first_delay_min if attempt == 0 else None, meeting))

            if outcome == "connected":
                break  # stop dialing once connected
            # next attempt: 1-3 days later
            attempt_time += timedelta(days=random.randint(1, 3),
                                      hours=random.randint(0, 8))

    conn.commit()
    n_calls = cur.execute("SELECT COUNT(*) FROM calls").fetchone()[0]
    conn.close()
    print(f"dialer.db written: {len(REPS)} reps, {n_leads} leads, {n_calls} calls")


if __name__ == "__main__":
    main()
