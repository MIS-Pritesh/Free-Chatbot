import streamlit as st
import pandas as pd
import os
from collections import OrderedDict

# ======================================================================
# 1. DATA LOADING AND PROCESSING
# ======================================================================

CSV_FILE_NAME = "Data.csv" 

@st.cache_data
def load_and_structure_data(file_name):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, file_name)
    
    if not os.path.exists(file_path):
        st.error(f"FATAL ERROR: Data file '{file_name}' not found. Please ensure the file is named **Data.csv** and is in the same directory as app.py.")
        return OrderedDict(), {}, pd.DataFrame()
    
    try:
        df = pd.read_csv(file_path)
        REQUIRED_COLS = ['subject', 'question', 'answer']
        if not all(col in df.columns for col in REQUIRED_COLS):
            st.error(f"FATAL ERROR: CSV must contain the columns: {', '.join(REQUIRED_COLS)}")
            return OrderedDict(), {}, pd.DataFrame()
        
        main_menu = OrderedDict() 
        sub_menus = {}
        grouped_data = df.groupby('subject')
        
        for subject, group in grouped_data:
            key = str(len(main_menu) + 1)
            main_menu[key] = subject
            
            sub_menu_questions = OrderedDict()
            for i, row in enumerate(group.itertuples()):
                q_key = str(i + 1)
                sub_menu_questions[q_key] = row.question
            
            sub_menus[subject] = sub_menu_questions

        return main_menu, sub_menus, df

    except Exception as e:
        st.error(f"FATAL ERROR: Failed to load or process CSV data. Error: {e}")
        return OrderedDict(), {}, pd.DataFrame()

if 'main_menu' not in st.session_state:
    main_menu_data, sub_menus_data, qa_data_df = load_and_structure_data(CSV_FILE_NAME)
    st.session_state.main_menu = main_menu_data
    st.session_state.sub_menus = sub_menus_data
    st.session_state.qa_data = qa_data_df

# ======================================================================
# 2. ANSWER RETRIEVAL LOGIC
# ======================================================================

def get_fixed_answer(question):
    if 'qa_data' not in st.session_state or st.session_state.qa_data.empty:
        return "System error: Data not loaded."
        
    try:
        answer_row = st.session_state.qa_data[st.session_state.qa_data['question'] == question]
        
        if not answer_row.empty:
            return answer_row.iloc[0]['answer']
        
        return "I'm sorry, I could not find a specific answer for that question in my database."
    except Exception as e:
        return f"An internal error occurred during lookup: {e}"

# ======================================================================
# 3. THEME INJECTION AND STREAMLIT SETUP (Sidebar Removed)
# ======================================================================

def inject_default_css():
    css = """
    :root {
        --primary-color: #4CAF50; 
        --background-color: #1c1c1c; 
        --text-color: #CCCCCC;
    }

    /* Mobile friendly styling */
    @media only screen and (max-width: 600px) {
        .stMarkdown {
            font-size: 14px !important;
            padding: 4px 8px !important;
        }
        .stButton>button {
            font-size: 14px !important;
            padding: 6px 10px !important;
            white-space: normal !important;
            text-align: left !important;
        }
        .stChatMessage>div {
            font-size: 14px !important;
            padding: 6px 10px !important;
            margin-bottom: 6px !important;
        }
    }
    """
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

inject_default_css()

# --- State Initialization ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    st.session_state.chat_history.append({
        "role": "assistant", 
        "content": "Hello! I am PlotBot, your Q&A assistant. Please select a category below to get started."
    })

if "current_menu_key" not in st.session_state:
    st.session_state.current_menu_key = "MAIN"

st.title("CSV-Driven Q&A Bot 🏡")

def display_menu(menu_dict):
    st.markdown("### Choose an Option:")
    
    cols = st.columns(1)  # mobile-friendly 1 column
    
    clicked_value = None
    
    for i, (key, value) in enumerate(menu_dict.items()):
        button_key = f"btn_{st.session_state.current_menu_key}_{key}"
        if cols[0].button(value, key=button_key):
            clicked_value = value
    
    if clicked_value is not None:
        handle_user_selection(clicked_value)
        st.experimental_rerun()  # rerun only once after the loop

def handle_user_selection(value):
    if value in st.session_state.main_menu.values():
        st.session_state.current_menu_key = value
    else:
        st.session_state.chat_history.append({"role": "assistant", "content": f"<b>Question:</b> {value}"})
        answer = get_fixed_answer(value)
        st.session_state.chat_history.append({"role": "assistant", "content": f"<b>Answer:</b> {answer}"})
        st.session_state.current_menu_key = "MAIN"
        st.session_state.chat_history.append({"role": "assistant", "content": "✅ Got it! Ready for your next question."})

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# Menu display logic
if st.session_state.main_menu:
    if st.session_state.current_menu_key == "MAIN":
        display_menu(st.session_state.main_menu)
    else:
        menu_to_display = st.session_state.sub_menus.get(st.session_state.current_menu_key, {})
        back_button_key = f"back_btn_{st.session_state.current_menu_key}"
        if st.button("⬅️ Go Back to Main Menu", key=back_button_key):
            st.session_state.current_menu_key = "MAIN"
            st.experimental_rerun()
        display_menu(menu_to_display)
