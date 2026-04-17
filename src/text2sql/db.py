import sqlite3
import json
from pathlib import Path
from typing import List

class DatabaseManager:
    """Manages SQLite database connections and schema extraction."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        
        # Check if the database file exists before attempting connection
        if not Path(db_path).exists():
            raise FileNotFoundError(f"Base de dados não encontrada em: {db_path}")
        
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def list_tables(self) -> List[str]:
        """Fetches a list of all table names in the database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        return [row["name"] for row in cursor.fetchall()]

    def describe_table(self, table_name: str) -> str:
        """Fetches the DDL (Data Definition Language) for a specific table."""
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
        row = cursor.fetchone()
        return row["sql"] if row else ""

    def get_full_schema(self) -> str:
        """Compiles the schema of all tables to be injected into the LLM system prompt."""
        tables = self.list_tables()
        schemas = []
        for table in tables:
            schemas.append(self.describe_table(table))
        return "\n\n".join(schemas)

    def run_query(self, query: str, limit: int = 30) -> str:
        """Executes a SQL query with safety checks, returning results as a JSON string."""
        
        # Force read-only queries
        clean_query = query.strip()
        if not clean_query.upper().startswith("SELECT"):
            return "Erro: Apenas consultas de leitura (SELECT) são permitidas."

        try:
            cursor = self.conn.cursor()
            cursor.execute(clean_query)
            
            # Limit results to prevent context window overflow
            rows = cursor.fetchmany(limit)
            
            if not rows:
                return "A consulta não retornou resultados."
            
            # Convert rows to a list of dictionaries, then to a JSON formatted string
            result_data = [dict(row) for row in rows]
            return json.dumps(result_data, indent=2)
            
        except Exception as e:
            return f"Erro ao executar SQL: {str(e)}"