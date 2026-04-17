from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
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
    6. Coloque um limite nas suas queries (ex: LIMIT 10) para análises quantitativas.

    Esquema do Banco de Dados:
    {schema}
    """

# 4. Define the Tools
@agent.tool
async def run_sql_query(ctx: RunContext[DatabaseManager], query: str) -> str:
    """
    Executes a SQL SELECT query on the database.
    The agent MUST use this tool to fetch data before answering.
    """
    return ctx.deps.run_query(query)