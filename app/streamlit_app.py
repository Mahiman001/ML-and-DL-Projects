
import json
import sqlite3
import uuid
from pathlib import Path
import os
import requests
import streamlit as st


# ---------- Configuration ----------

st.set_page_config(
    page_title="Big Five Personality Test",
    page_icon="🧠",
    layout="centered",
)

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000/predict"
)


DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "DATA"
    / "processed"
    / "progress.db"
)

TRAIT_NAMES = {
    "E": "Extraversion",
    "A": "Agreeableness",
    "C": "Conscientiousness",
    "O": "Openness to Experience",
    "N": "Neuroticism",
}

TRAIT_DESCRIPTIONS = {
    "E": "How outgoing, talkative, and socially energetic you tend to be.",
    "A": "How considerate, compassionate, and cooperative you tend to be.",
    "C": "How organized, responsible, and self-disciplined you tend to be.",
    "O": "How curious, imaginative, and open to new experiences you tend to be.",
    "N": "How sensitive you may be to stress and negative emotions.",
}

QUESTIONS = {
    "EXT1": "I am the life of the party.",
    "EXT2": "I don't talk a lot.",
    "EXT3": "I feel comfortable around people.",
    "EXT4": "I keep in the background.",
    "EXT5": "I start conversations.",
    "EXT6": "I have little to say.",
    "EXT7": "I talk to a lot of different people at parties.",
    "EXT8": "I don't like to draw attention to myself.",
    "EXT9": "I don't mind being the center of attention.",
    "EXT10": "I am quiet around strangers.",

    "EST1": "I get stressed out easily.",
    "EST2": "I am relaxed most of the time.",
    "EST3": "I worry about things.",
    "EST4": "I seldom feel blue.",
    "EST5": "I am easily disturbed.",
    "EST6": "I get upset easily.",
    "EST7": "I change my mood a lot.",
    "EST8": "I have frequent mood swings.",
    "EST9": "I get irritated easily.",
    "EST10": "I often feel blue.",

    "AGR1": "I feel little concern for others.",
    "AGR2": "I am interested in people.",
    "AGR3": "I insult people.",
    "AGR4": "I sympathize with others' feelings.",
    "AGR5": "I am not interested in other people's problems.",
    "AGR6": "I have a soft heart.",
    "AGR7": "I am not really interested in others.",
    "AGR8": "I take time out for others.",
    "AGR9": "I feel others' emotions.",
    "AGR10": "I make people feel at ease.",

    "CSN1": "I am always prepared.",
    "CSN2": "I leave my belongings around.",
    "CSN3": "I pay attention to details.",
    "CSN4": "I make a mess of things.",
    "CSN5": "I get chores done right away.",
    "CSN6": "I often forget to put things back in their proper place.",
    "CSN7": "I like order.",
    "CSN8": "I shirk my duties.",
    "CSN9": "I follow a schedule.",
    "CSN10": "I am exacting in my work.",

    "OPN1": "I have a rich vocabulary.",
    "OPN2": "I have difficulty understanding abstract ideas.",
    "OPN3": "I have a vivid imagination.",
    "OPN4": "I am not interested in abstract ideas.",
    "OPN5": "I have excellent ideas.",
    "OPN6": "I do not have a good imagination.",
    "OPN7": "I am quick to understand things.",
    "OPN8": "I use difficult words.",
    "OPN9": "I spend time reflecting on things.",
    "OPN10": "I am full of ideas.",
}


# ---------- SQLite persistence ----------

DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def connect_db():
    return sqlite3.connect(DB_PATH)


def initialize_db():
    with connect_db() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                session_id TEXT PRIMARY KEY,
                page INTEGER NOT NULL,
                answers TEXT NOT NULL,
                results TEXT
            )
        """)


def load_progress(session_id):
    with connect_db() as connection:
        row = connection.execute(
            """
            SELECT page, answers, results
            FROM progress
            WHERE session_id = ?
            """,
            (session_id,),
        ).fetchone()

    if row is None:
        return 0, {}, None

    return (
        row[0],
        json.loads(row[1]),
        json.loads(row[2]) if row[2] else None,
    )


def save_progress():
    with connect_db() as connection:
        connection.execute(
            """
            INSERT INTO progress (session_id, page, answers, results)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                page = excluded.page,
                answers = excluded.answers,
                results = excluded.results
            """,
            (
                st.session_state.session_id,
                st.session_state.page,
                json.dumps(st.session_state.answers),
                (
                    json.dumps(st.session_state.results)
                    if st.session_state.results is not None
                    else None
                ),
            ),
        )


initialize_db()


# ---------- Restore the session ----------

if "session_id" not in st.session_state:
    session_id = st.query_params.get("session_id")

    if not session_id:
        session_id = str(uuid.uuid4())
        st.query_params["session_id"] = session_id

    saved_page, saved_answers, saved_results = load_progress(session_id)

    st.session_state.session_id = session_id
    st.session_state.page = saved_page
    st.session_state.answers = saved_answers
    st.session_state.results = saved_results


# ---------- Results page ----------

if st.session_state.results is not None:
    st.title("🧠 Your Personality Results")
    st.write("Your estimated Big Five personality profile")

    scores = st.session_state.results["personality_scores"]
    interpretations = st.session_state.results["interpretations"]

    for trait in ["E", "A", "C", "O", "N"]:
        score = float(scores[trait])
        level = interpretations[trait]["level"]

        st.subheader(TRAIT_NAMES[trait])
        st.metric("Estimated score (1–5)", f"{score:.2f}")
        st.caption(f"Provisional range: {level}")
        st.write(TRAIT_DESCRIPTIONS[trait])
        st.progress(min(max(score / 5, 0.0), 1.0))
        st.divider()

    st.caption(
        "Educational estimates only. These labels use provisional thresholds "
        "and are not validated psychological classifications or diagnoses."
    )

    if st.button("Retake test", type="primary"):
        with connect_db() as connection:
            connection.execute(
                "DELETE FROM progress WHERE session_id = ?",
                (st.session_state.session_id,),
            )

        for question_id in QUESTIONS:
            st.session_state.pop(f"input_{question_id}", None)

        st.session_state.answers = {}
        st.session_state.page = 0
        st.session_state.results = None
        save_progress()
        st.rerun()

    st.stop()


# ---------- Questionnaire ----------

st.title("🧠 Big Five Personality Test")
st.write("Answer 50 questions across five short pages.")
st.info("Educational estimate only — not a clinical assessment.")

page = st.session_state.page
question_ids = list(QUESTIONS.keys())[page * 10:(page + 1) * 10]

st.progress((page + 1) / 5)
st.subheader(f"Page {page + 1} of 5")
st.caption(f"Questions {page * 10 + 1}–{page * 10 + 10} of 50")

with st.form(key=f"page_{page}"):
    for question_id in question_ids:
        previous_answer = st.session_state.answers.get(question_id)

        st.radio(
            f"{question_id}: {QUESTIONS[question_id]}",
            options=[1, 2, 3, 4, 5],
            index=(
                [1, 2, 3, 4, 5].index(previous_answer)
                if previous_answer is not None
                else None
            ),
            format_func=lambda value: {
                1: "1 — Strongly disagree",
                2: "2 — Disagree",
                3: "3 — Neutral",
                4: "4 — Agree",
                5: "5 — Strongly agree",
            }[value],
            key=f"input_{question_id}",
            horizontal=True,
        )

    col1, col2 = st.columns(2)

    with col1:
        previous = st.form_submit_button(
            "← Previous",
            disabled=(page == 0),
            use_container_width=True,
        )

    with col2:
        next_page = st.form_submit_button(
            "Submit answers" if page == 4 else "Next →",
            type="primary",
            use_container_width=True,
        )


# ---------- Save answers and navigate ----------

if previous or next_page:
    for question_id in question_ids:
        answer = st.session_state.get(f"input_{question_id}")

        if answer is not None:
            st.session_state.answers[question_id] = answer

    unanswered = [
        question_id
        for question_id in question_ids
        if st.session_state.answers.get(question_id) is None
    ]

    if unanswered:
        st.error("Please answer all 10 questions on this page.")

    elif previous:
        st.session_state.page -= 1
        save_progress()
        st.rerun()

    elif page < 4:
        st.session_state.page += 1
        save_progress()
        st.rerun()

    else:
        try:
            response = requests.post(
                API_URL,
                json={"answers": st.session_state.answers},
                timeout=30,
            )
            response.raise_for_status()

            st.session_state.results = response.json()
            st.session_state.page = 5
            save_progress()
            st.rerun()

        except requests.RequestException as error:
            st.error(f"Could not contact the prediction API: {error}")
