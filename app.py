import streamlit as st
import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

st.title("📊 CSV-based Chatbot (Free Open-Source Model)")

# ---------------------------------------------------------
# Load Small Model Suitable for Streamlit Cloud
# ---------------------------------------------------------
@st.cache_resource
def load_model():
    model_name = "Qwen/Qwen2.5-0.5B-Instruct"  # FAST & FREE & SMALL
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float32  # CPU-compatible
    )
    return tokenizer, model

tokenizer, model = load_model()

# ---------------------------------------------------------
# Load CSV
# ---------------------------------------------------------
@st.cache_resource
def load_csv():
    try:
        df = pd.read_csv("Data.csv")
        return df
    except Exception as e:
        st.error(f"❌ Could not load Data.csv: {e}")
        return None

df = load_csv()

if df is not None:
    st.subheader("📁 Loaded Data.csv")
    st.dataframe(df)

# Convert CSV to text knowledge
def csv_to_text(df):
    text = ""
    for idx, row in df.iterrows():
        row_text = ", ".join([f"{col}: {str(val)}" for col, val in row.items()])
        text += row_text + "\n"
    return text

csv_text = csv_to_text(df) if df is not None else ""

# ---------------------------------------------------------
# Chat Section
# ---------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.text_input("Ask based on CSV:")

if st.button("Send") and user_input.strip() != "":
    # Build prompt for the model
    prompt = (
        "You are a helpful assistant. Only answer using the following CSV data:\n\n"
        f"{csv_text}\n\n"
        "Conversation:\n"
    )

    for role, msg in st.session_state.history:
        prompt += f"{role}: {msg}\n"

    prompt += f"User: {user_input}\nAssistant:"

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)

    # CPU-friendly generation
    output = model.generate(
        **inputs,
        max_new_tokens=150,
        temperature=0.4,
        top_p=0.9,
        do_sample=True
    )

    reply = tokenizer.decode(output[0], skip_special_tokens=True)
    bot_reply = reply.split("Assistant:")[-1].strip()

    st.session_state.history.append(("User", user_input))
    st.session_state.history.append(("Assistant", bot_reply))

# Display conversation
for role, msg in st.session_state.history:
    if role == "User":
        st.markdown(f"**👤 You:** {msg}")
    else:
        st.markdown(f"**🤖 Bot:** {msg}")
