# app.py
"""
Streamlit app for the AI-driven Sales Training Platform.
Main entrypoint. Designed to be deployed to Streamlit Cloud or run locally.
Python 3.11.0 expected.

Usage:
  - pip install -r requirements.txt
  - export LLM_API_KEY=<your key>
  - streamlit run app.py
"""

import streamlit as st
from datetime import datetime
import os
import uuid
from ai_agent import AIAgent, Persona
from scoring import score_conversation
from data_loader import ensure_dataset
from stt_tts import transcribe_audio_file, synthesize_speech
import json
from utils import ensure_dirs

# Setup
st.set_page_config(page_title="Sales Trainer", layout="wide")

ensure_dirs(["data", "recordings", "assets"])

# Ensure dataset (non-blocking attempt)
with st.spinner("Ensuring dataset is available (kagglehub)..."):
    try:
        dataset_path = ensure_dataset()  # downloads into data/ by default
    except Exception as e:
        dataset_path = None
        st.warning("Dataset download failed or skipped. You can still run the app without it.")
        st.info(str(e))

# Sidebar - Admin / config
st.sidebar.title("Sales Trainer — Configuration")
scenario = st.sidebar.selectbox("Scenario", [
    "Cold call", "Follow-up call", "Demo call", "Pricing/negotiation call", "Renewal call"
])
persona_name = st.sidebar.selectbox("Persona", [
    "Friendly", "Skeptical", "Rushed", "Annoyed", "Technical buyer", "Economic buyer"
])
voice_enabled = st.sidebar.checkbox("Enable TTS (play AI voice responses)", value=False)
save_recordings = st.sidebar.checkbox("Save recordings & transcripts", value=True)
show_admin = st.sidebar.checkbox("Show Admin Dashboard", value=False)

# Instantiate agent with persona
agent = AIAgent()  # will pick LLM provider via env vars inside ai_agent.py
persona = Persona(name=persona_name)

# UI layout
st.title("AI Sales Trainer — Practice realistic sales conversations")
col1, col2 = st.columns([2, 1])

with col1:
    st.header("Session")
    st.write(f"**Scenario:** {scenario} — **Persona:** {persona_name}")
    st.write("Start a practice session. Type your lines or upload a short audio file (wav/mp3).")

    # Conversation display
    if "conversation" not in st.session_state:
        st.session_state.conversation = []  # list of {"speaker": "rep"|"ai", "text": "...", "timestamp": ...}

    # Show conversation
    for turn in st.session_state.conversation:
        speaker = "You" if turn["speaker"] == "rep" else f"Prospect ({persona.name})"
        st.markdown(f"**{speaker}**: {turn['text']}  \n*{turn['timestamp']}*")

    # Input controls
    mode = st.radio("Input mode", ["Text", "Upload audio (mp3/wav)"])
    user_text = ""
    uploaded_file = None
    if mode == "Text":
        user_text = st.text_area("Say something to the prospect:", height=100)
        send = st.button("Send")
    else:
        uploaded_file = st.file_uploader("Upload an audio file (wav/mp3)", type=["wav", "mp3", "m4a"])
        send = st.button("Transcribe & Send")

    if send:
        # process user input
        if mode == "Upload audio (mp3/wav)":
            if not uploaded_file:
                st.error("Please upload an audio file.")
            else:
                with st.spinner("Transcribing audio..."):
                    wav_path = os.path.join("recordings", f"upload_{uuid.uuid4().hex}.wav")
                    # write to disk
                    with open(wav_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    try:
                        user_text = transcribe_audio_file(wav_path)  # from stt_tts.py
                    except Exception as e:
                        st.error("Error during transcription: " + str(e))
                        user_text = ""
                st.success("Transcription: " + user_text[:200])

        if user_text and user_text.strip() != "":
            # Save rep turn
            turn_entry = {"speaker": "rep", "text": user_text.strip(), "timestamp": datetime.utcnow().isoformat()}
            st.session_state.conversation.append(turn_entry)

            # Ask AI agent for immediate reply (aim <1s where possible)
            with st.spinner("Generating prospect response..."):
                ai_reply = agent.reply(user_text=user_text, scenario=scenario, persona=persona)
            ai_turn = {"speaker": "ai", "text": ai_reply, "timestamp": datetime.utcnow().isoformat()}
            st.session_state.conversation.append(ai_turn)

            # Optionally synthesize speech and play
            if voice_enabled:
                with st.spinner("Synthesizing audio..."):
                    try:
                        audio_bytes = synthesize_speech(ai_reply, persona=persona)
                        st.audio(audio_bytes, format="audio/wav")
                    except Exception as e:
                        st.warning("TTS failed: " + str(e))

            # Optional saving
            if save_recordings:
                fname = os.path.join("recordings", f"session_{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}_{uuid.uuid4().hex}.json")
                with open(fname, "w", encoding="utf-8") as f:
                    json.dump(st.session_state.conversation, f, ensure_ascii=False, indent=2)

with col2:
    st.header("Coaching & Scoring")
    st.write("After a few turns, click **Analyze** to get scoring and coaching tips.")
    if st.button("Analyze"):
        transcript = " ".join([t["text"] for t in st.session_state.conversation if t["speaker"] == "rep" or t["speaker"] == "ai"])
        scores, tips = score_conversation(st.session_state.conversation, scenario=scenario)
        st.metric("Outcome Rating", scores.get("outcome_rating", 0))
        st.metric("Confidence Score", scores.get("confidence_score", 0))
        st.metric("Objection Handling", scores.get("objection_score", 0))
        st.markdown("**Coaching Tips**")
        for tip in tips:
            st.write("- " + tip)

    st.header("Session controls")
    if st.button("Reset conversation"):
        st.session_state.conversation = []
        st.success("Conversation reset.")

# Admin dashboard (simple)
if show_admin:
    st.sidebar.header("Admin Dashboard")
    st.sidebar.write("Saved recordings & transcripts:")
    files = sorted(os.listdir("recordings"), reverse=True)
    for f in files[:50]:
        st.sidebar.write(f"- {f}")

st.write("---")
st.caption("This is a prototype. Replace the placeholder LLM/STT/TTS adapters with your production provider and API keys.")
