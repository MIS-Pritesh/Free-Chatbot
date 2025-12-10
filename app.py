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
    df = pd.read_csv(CSV_FILE_NAME)
    return df

df = load_data()

# Build menu structures
main_menu = OrderedDict()
sub_menus = {}

for idx, subject in enumerate(df['subject'].unique(), start=1):
    main_menu[str(idx)] = subject
    sub_df = df[df['subject'] == subject]
    sub_menus[subject] = OrderedDict(
        {str(i+1): q for i, q in enumerate(sub_df['question'])}
    )

# =========================================================
# 2. SESSION STATE
# =========================================================
if "chat" not in st.session_state:
    st.session_state.chat = [{"role": "assistant", "msg": "Hello! I am PlotBot. Please select a category below."}]

if "current_menu" not in st.session_state:
    st.session_state.current_menu = "MAIN"

# =========================================================
# 3. BEAUTIFUL CHAT CSS (WhatsApp-style)
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

.assistant {
    background: #ECECEC;
    color: black;
    border-bottom-left-radius: 0;
    text-align: left;
}

.user {
    background: #4CAF50;
    color: white;
    border-bottom-right-radius: 0;
    margin-left: auto;
    text-align: right;
}
</style>
"""

st.markdown(CHAT_CSS, unsafe_allow_html=True)

# =========================================================
# 4. FUNCTIONS
# =========================================================
def add_message(role, message):
    st.session_state.chat.append({"role": role, "msg": message})

def display_chat():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for c in st.session_state.chat:
        role_class = "assistant" if c["role"] == "assistant" else "user"
        st.markdown(f'<div class="message {role_class}">{c["msg"]}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def get_answer(question):
    row = df[df["question"] == question]
    if not row.empty:
        return row.iloc[0]["answer"]
    return "I couldn't find an answer for that."

# =========================================================
# 5. STREAMLIT PAGE
# =========================================================
st.title("📱 PlotBot Assistant (Modern UI)")

# Show chat UI
display_chat()

st.write("---")

# =========================================================
# 6. MENU SYSTEM
# =========================================================
def show_menu(menu_dict, title="Choose an option:"):
    st.subheader(title)
    cols = st.columns(2)

    for idx, (key, value) in enumerate(menu_dict.items()):
        if cols[idx % 2].button(value):
            handle_selection(value)

def handle_selection(value):
    # Category selection
    if value in main_menu.values():
        st.session_state.current_menu = value
    else:
        # User clicked a question
        add_message("user", value)
        ans = get_answer(value)
        add_message("assistant", f"**Answer:** {ans}")
        add_message("assistant", "✔️ Got it!")
        st.session_state.current_menu = "MAIN"
    st.rerun()

# Main menu logic
if st.session_state.current_menu == "MAIN":
    show_menu(main_menu)
else:
    st.button("⬅️ Back", on_click=lambda: st.session_state.update(current_menu="MAIN"))
    show_menu(sub_menus[st.session_state.current_menu], title="Select a Question:")
