import streamlit as st
import pandas as pd
import os
from collections import OrderedDict

# =========================================================
# 1. LOAD DATA
# =========================================================
CSV_FILE_NAME = "Data.csv"

@st.cache_data
def load_data():
    return pd.read_csv(CSV_FILE_NAME)

df = load_data()

# Build menu structures
main_menu = OrderedDict()
sub_menus = {}

for idx, subject in enumerate(df['subject'].unique(), start=1):
    main_menu[str(idx)] = subject
    sub_df = df[df['subject'] == subject]
    sub_menus[subject] = OrderedDict({str(i+1): q for i, q in enumerate(sub_df['question'])})

# =========================================================
# 2. SESSION STATE
# =========================================================
if "chat" not in st.session_state:
    st.session_state.chat = [{"role": "assistant", "msg": "Hello! I am PlotBot. Please select a category below."}]

if "current_menu" not in st.session_state:
    st.session_state.current_menu = "MAIN"

# =========================================================
# 3. CHAT CSS (COLOR SWAPPED)
# =========================================================
CHAT_CSS = """
<style>
.chat-container {
    width: 100%;
    max-width: 450px;
    margin: auto;
}

.message {
    padding: 10px 14px;
    margin: 8px;
    max-width: 85%;
    font-size: 16px;
    border-radius: 12px;
    line-height: 1.4;
}

/* USER (white/grey bubble) */
.user {
    background: #ECECEC;
    color: black;
    border-bottom-right-radius: 0;
    margin-left: auto;
    text-align: right;
}

/* ASSISTANT (GREEN bubble) */
.assistant {
    background: #4CAF50;
    color: white;
    border-bottom-left-radius: 0;
    text-align: left;
}
</style>
"""

st.markdown(CHAT_CSS, unsafe_allow_html=True)

# =========================================================
# 4. FUNCTIONS
# =========================================================
def add_message(role, msg):
    st.session_state.chat.append({"role": role, "msg": msg})

def display_chat():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for bubble in st.session_state.chat:
        css_class = "assistant" if bubble["role"] == "assistant" else "user"
        st.markdown(f'<div class="message {css_class}">{bubble["msg"]}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def get_answer(question):
    row = df[df["question"] == question]
    if not row.empty:
        return row.iloc[0]["answer"]  # NO "Answer:" PREFIX
    return "I couldn't find an answer for that."

# =========================================================
# 5. UI
# =========================================================
st.title("ChatBot Assistant")

display_chat()
st.write("---")

def show_menu(menu_dict, title="Choose an option:"):
    st.subheader(title)
    cols = st.columns(2)
    for i, (k, v) in enumerate(menu_dict.items()):
        if cols[i % 2].button(v):
            handle_selection(v)

def handle_selection(value):
    if value in main_menu.values():  
        st.session_state.current_menu = value
    else:
        # User clicked a question -> show user message
        add_message("user", value)

        # Add assistant answer (NO "Answer:" AND NO "Got it")
        ans = get_answer(value)
        add_message("assistant", ans)

        # Return to main menu
        st.session_state.current_menu = "MAIN"

    st.rerun()

if st.session_state.current_menu == "MAIN":
    show_menu(main_menu)
else:
    st.button("⬅️ Back", on_click=lambda: st.session_state.update(current_menu="MAIN"))
    show_menu(sub_menus[st.session_state.current_menu], title="Select a Question:")
