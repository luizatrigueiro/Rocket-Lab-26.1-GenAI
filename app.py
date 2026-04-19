import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Absolute imports based on our project structure
from src.text2sql.db import DatabaseManager
from src.text2sql.agent import agent

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="E-Commerce Agent", page_icon="🛒", layout="centered")
st.title("🛒 Assistente de E-Commerce")
st.caption("Faça perguntas sobre as vendas, clientes e produtos.")

# --- DATABASE INITIALIZATION ---
@st.cache_resource
def get_database():
    if not os.getenv("GOOGLE_API_KEY"):
        st.error("Erro: chave não encontrada")
        st.stop()
    try:
        return DatabaseManager("banco.db")
    except Exception as e:
        st.error(f"Erro ao conectar com o banco de dados: {e}")
        st.stop()

db_manager = get_database()

if "chat_ui" not in st.session_state:
    st.session_state.chat_ui = [{"role": "assistant", "content": "Olá! O que você gostaria de saber sobre nossos dados hoje?"}]

if "agent_history" not in st.session_state:
    st.session_state.agent_history = []

for msg in st.session_state.chat_ui:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_question := st.chat_input("Ex: Qual o ticket médio dos consumidores de SP?"):
    
    # 1. Display User Message
    st.session_state.chat_ui.append({"role": "user", "content": user_question})
    with st.chat_message("user"):
        st.markdown(user_question)

    # 2. Display Assistant Response 
    with st.chat_message("assistant"):
        with st.spinner("Analisando o banco de dados... ⏳"):
            try:
                # Run the agent synchronously (Fixed Event Loop Issue)
                result = agent.run_sync(
                    user_question,
                    deps=db_manager,
                    message_history=st.session_state.agent_history
                )
                
                # Extract response and update memory
                answer = result.output.conclusion
                st.session_state.agent_history = result.all_messages()
                
                # Show answer
                st.markdown(answer)
                st.session_state.chat_ui.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                error_msg = f"❌ Ocorreu um erro: {str(e)}"
                st.error(error_msg)
                st.session_state.chat_ui.append({"role": "assistant", "content": error_msg})