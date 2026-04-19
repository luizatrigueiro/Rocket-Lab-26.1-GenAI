from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext, ModelRetry
from .db import DatabaseManager

# Define the Structured Output
class AnalystResult(BaseModel):
    """The expected final output format from the agent."""
    conclusion: str = Field(
        ..., 
        description="A text conclusion generated from the data analysis. Must directly answer the user's question."
    )

# Initialize the PydanticAI Agent
agent = Agent(
    model='gemini-2.5-flash',
    deps_type=DatabaseManager,
    output_type=AnalystResult, 
    retries=3
)

# Dynamic System Prompt
@agent.system_prompt
async def build_system_prompt(ctx: RunContext[DatabaseManager]) -> str:
    """Injects the database schema dynamically into the LLM context."""
    schema = ctx.deps.get_full_schema()
    
    return f"""
    Você é um analista de dados especialista em bancos de dados SQL.
    Sua missão é responder à pergunta do usuário extraindo e analisando dados do banco.

    Regras Críticas:
    1. Você deve gerar uma query SQLite baseada no esquema fornecido.
    2. Você DEVE obrigatoriamente executar essa query chamando a ferramenta 'run_sql_query'.
    3. Analise matematicamente e logicamente as linhas de dados retornadas pela ferramenta.
    4. Formule sua saída final contendo a explicação descritiva em português no campo 'conclusion'.
    5. Nunca tente adivinhar dados sem executar a query.
    6. Coloque um limite nas suas queries (ex: LIMIT 10) para listas longas.
    7. Se o usuário perguntar sobre qualquer assunto que não seja relacionado a e-commerce, vendas, clientes, produtos ou dados deste banco, recuse-se a responder educadamente. Não execute nenhuma query e devolva na 'conclusion' que você é um assistente exclusivo para análise de dados da loja.

    Dicionário de Dados e Regras de Negócio (E-commerce):
    - Entrega no prazo: Refere-se a pedidos em que a data de entrega é menor ou igual à data limite estimada.
    - Entrega em atraso: Refere-se a pedidos em que a data de entrega é superior à data limite.
    - Ticket Médio: É o valor total das vendas dividido pela quantidade de pedidos únicos.
    - Avaliação Negativa: Geralmente refere-se a pontuações de avaliação baixas (ex: notas 1 ou 2).
    - Relacionamentos: Cruze sempre as tabelas de fatos (ex: fat_pedidos) com as dimensões (ex: dim_consumidores, dim_produtos) para obter os nomes reais em vez de apenas IDs.

    Esquema da Base de Dados:
    {schema}
    """

# Define the Tools
@agent.tool
async def run_sql_query(ctx: RunContext[DatabaseManager], query: str) -> str:
    """
    Executes a SQL SELECT query on the database.
    The agent MUST use this tool to fetch data before answering.
    """
    result = ctx.deps.run_query(query)
    
    if result.startswith("Erro"):
        raise ModelRetry(f"Sua consulta falhou: {result}. Verifique o esquema e tente novamente.")
        
    return result