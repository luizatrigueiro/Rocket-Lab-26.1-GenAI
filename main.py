import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    print("Erro: chave não encontrada!")
    sys.exit(1)

from src.text2sql.db import DatabaseManager
from src.text2sql.agent import agent

async def run_chat_interface():
    """Runs the main terminal loop for user interaction."""
    
    try:
        db_manager = DatabaseManager("banco.db")
    except Exception as e:
        print(f"Erro ao conectar com o banco de dados: {e}")
        sys.exit(1)

    print("Assistente de Dados de E-commerce Iniciado!")
    print("   • Visualizando consultas em tempo real.")
    print("   • Digite 'sair' para encerrar.")

    chat_history = []

    while True:
        try:
            user_question = input("\nVocê: ")
            
            if user_question.lower() in ["sair", "exit", "quit"]:
                print("Encerrando o assistente. Até logo!")
                break
                
            if not user_question.strip():
                continue

            print("\nAnalisando dados...")

            result = await agent.run(
                user_question,
                deps=db_manager,
                message_history=chat_history
            )
                
            for message in result.new_messages():
                if hasattr(message, 'parts'):
                    for part in message.parts:
                        if hasattr(part, 'tool_name') and part.tool_name == 'run_sql_query':
                            query = part.args.get('query') if isinstance(getattr(part, 'args', None), dict) else getattr(part, 'args', '')
                            print(f"   ⚙️ Executando SQL: {query}")
            
            print(f"\nAssistente:\n{result.output.conclusion}\n")
            print("─"*60)

            # Update history
            chat_history = result.all_messages()

        except KeyboardInterrupt:
            print("\nEncerrando o assistente. Até logo!")
            break
        except Exception as e:
            print(f"\nOcorreu um erro durante o processamento: {e}")

if __name__ == "__main__":
    asyncio.run(run_chat_interface())