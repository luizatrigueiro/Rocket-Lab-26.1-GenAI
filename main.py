import asyncio
import os
import sys
from dotenv import load_dotenv

# 1. Carrega as variáveis de ambiente PRIMEIRO
load_dotenv()

# Verifica a chave antes de prosseguir
if not os.getenv("GOOGLE_API_KEY"):
    print("Erro: GOOGLE_API_KEY não encontrada no arquivo .env")
    sys.exit(1)

# 2. AGORA é seguro importar os nossos módulos, pois a chave já está na memória
from src.text2sql.db import DatabaseManager
from src.text2sql.agent import agent

async def run_chat_interface():
    """Runs the main terminal loop for user interaction."""
    
    try:
        # Initialize the database connection
        db_manager = DatabaseManager("banco.db")
    except Exception as e:
        print(f"Erro ao conectar com o banco de dados: {e}")
        sys.exit(1)

    print("\n" + "="*50)
    print("Assistente de Dados de E-commerce Iniciado!")
    print("Faça perguntas sobre vendas, entregas, clientes, etc.")
    print("Digite 'sair' para encerrar.")
    print("="*50 + "\n")

    # List to keep track of the conversation context
    chat_history = []

    while True:
        try:
            user_question = input("\n👤 Você: ")
            
            if user_question.lower() in ["sair", "exit", "quit"]:
                print("Encerrando o assistente. Até logo!")
                break
                
            if not user_question.strip():
                continue

            print("Analisando dados no banco...")

            # Run the PydanticAI agent
            result = await agent.run(
                user_question,
                deps=db_manager,
                message_history=chat_history
            )

            # Print the structured output
            print(f"\nAssistente:\n{result.output.conclusion}\n")

            # Update the chat history for follow-up questions
            chat_history = result.all_messages()

        except KeyboardInterrupt:
            print("\nEncerrando o assistente. Até logo!")
            break
        except Exception as e:
            print(f"\nOcorreu um erro durante o processamento: {e}")

if __name__ == "__main__":
    asyncio.run(run_chat_interface())