
import streamlit as st
import random

# ----------------------
# Config
# ----------------------
ADMIN_PIN = "Social-Team-2025"

if "players" not in st.session_state:
    st.session_state.players = {}
if "rounds" not in st.session_state:
    st.session_state.rounds = []
if "current_round" not in st.session_state:
    st.session_state.current_round = None

# ----------------------
# Functions
# ----------------------
def start_round(player_name):
    truth = st.session_state.players[player_name]["truth"]
    lie = st.session_state.players[player_name]["lie"]
    statements = [(truth, "truth"), (lie, "lie")]
    random.shuffle(statements)
    st.session_state.current_round = {
        "player": player_name,
        "statements": statements,
        "votes": []
    }

def end_round():
    round_data = st.session_state.current_round
    st.session_state.rounds.append(round_data)
    st.session_state.current_round = None

# ----------------------
# UI
# ----------------------
st.title("Kepler Cannon: Truth or Lie Game")

tabs = st.tabs(["Submit", "Vote", "Host"])

# ----------------------
# Submit Tab
# ----------------------
with tabs[0]:
    st.header("Submit Your Statements")
    name = st.text_input("Your Name")
    truth = st.text_input("Enter ONE True Statement")
    lie = st.text_input("Enter ONE False Statement")
    if st.button("Submit"):
        if name and truth and lie:
            st.session_state.players[name] = {"truth": truth, "lie": lie}
            st.success("Submitted!")
        else:
            st.error("Please fill all fields.")

# ----------------------
# Vote Tab
# ----------------------
with tabs[1]:
    st.header("Vote on the Current Round")
    if st.session_state.current_round:
        round_data = st.session_state.current_round
        statements = round_data["statements"]
        vote = st.radio("Which one do you think is TRUE?", 
                        options=[f"1: {statements[0][0]}", f"2: {statements[1][0]}"],
                        key=f"vote_{round_data['player']}")
        if st.button("Submit Vote"):
            st.session_state.current_round["votes"].append(vote)
            st.success("Vote submitted!")
    else:
        st.info("No active round. Wait for the host to start.")

# ----------------------
# Host Tab
# ----------------------
with tabs[2]:
    st.header("Host Controls")
    pin = st.text_input("Enter Admin PIN", type="password")
    if pin == ADMIN_PIN:
        st.success("Admin Access Granted")

        if not st.session_state.current_round:
            st.subheader("Start a New Round")
            if st.session_state.players:
                player = st.selectbox("Choose Player", list(st.session_state.players.keys()))
                if st.button("Start Round"):
                    start_round(player)
                    st.experimental_rerun()
            else:
                st.info("No players yet.")
        else:
            round_data = st.session_state.current_round
            st.subheader(f"Current Round: {round_data['player']}")
            st.write("Statements shown (random order):")
            for i, (text, kind) in enumerate(round_data["statements"], start=1):
                st.write(f"{i}. {text}")

            if st.button("Reveal & Score"):
                votes = round_data["votes"]
                total_votes = len(votes)
                lie_index = next(i for i, (_, kind) in enumerate(round_data["statements"], start=1) if kind == "lie")
                wrong_votes = sum(1 for v in votes if v.startswith(str(lie_index)))

                if total_votes > 0 and (wrong_votes / total_votes) > 0.5:
                    score = 2
                    st.success(f"{round_data['player']} fooled the majority! +2 points")
                else:
                    score = 0
                    st.info(f"{round_data['player']} did not fool the majority. +0 points")

                st.session_state.players[round_data["player"]].setdefault("score", 0)
                st.session_state.players[round_data["player"]]["score"] += score

                end_round()

            st.subheader("Leaderboard")
            leaderboard = sorted(st.session_state.players.items(), key=lambda x: x[1].get("score",0), reverse=True)
            for name, data in leaderboard:
                st.write(f"{name}: {data.get('score',0)} pts")
    else:
        st.warning("Enter admin PIN to access host controls.")
