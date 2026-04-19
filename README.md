# 🚀 Rocket Lab 2026: E-Commerce Intelligent Agent (Text-to-SQL)

This project features a state-of-the-art artificial intelligence agent capable of converting natural language into complex SQL queries. Developed for the Visagio GenAI Challenge, the system allows non-technical users to extract valuable insights from an e-commerce database in a conversational and secure manner.

## 🛠️ Tech Stack

* **Language:** Python 3.12+
* **Package Manager:** [uv](https://astral.sh/uv/) (Performance and isolation)
* **Agent Framework:** [PydanticAI](https://ai.pydantic.dev/)
* **Language Model:** Gemini 2.5 Flash
* **Web Interface:** Streamlit
* **Database:** SQLite (Relational)

## 🧠 Architecture and Technical Highlights

1.  **ReACT Mechanism (Reasoning & Acting):** The agent "thinks" before acting.
2.  **Self-Correction:** If a query fails, the agent uses `ModelRetry` to analyze the error and autonomously correct the syntax.
3.  **Business Dictionary:** The agent has specific instructions for calculating e-commerce metrics, such as Average Ticket and Delivery Rates.
4.  **Security Guardrails:**
    * **Scope:** Blocks out-of-topic questions (e.g., recipes, sports) to save tokens.
    * **Data Protection:** The execution engine only accepts `SELECT` commands, preventing modifications (INSERT/DELETE) to the database.

## ⚙️ Setup and Installation

1. Prerequisites
- Install uv if you haven't already:
  ```bash
  curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh 
  ```
2. Environment Setup
- Create a .env file in the project root with your API key:
  ```bash
  GOOGLE_API_KEY=your_google_ai_studio_key
  ```
3. Execution
- To run the Web Interface:
  ```bash
  uv run streamlit run app.py
  ```
## 🧪 Testing Guide
  
### To validate the system's intelligence, try the following use cases in the interface:
1. Business Question (Table Joins):
- Input: "What is the average ticket of consumers from São Paulo?"
- Expected: The agent should perform a JOIN between the consumers and orders tables to calculate the average.
2. Complex Question (Date Logic):
- Input: "What is the percentage of orders delivered on time?"
- Expected: The system should compare the actual delivery date with the estimated deadline.
3. Guardrail Test (Out of Scope):
- Input: "How do I make a mushroom risotto?"
- Expected: A polite response stating that the assistant is exclusively for store data analysis.
4. Self-Correction Test:
- Input: "List the top selling products using the column 'product_name_that_does_not_exist'."
- Expected: The agent will try to run it, receive a database error, consult the correct schema, and fix the query autonomously.
  
## 📌 Author

- Developed by **Luiza Trigueiro**
* [https://www.linkedin.com/in/luiza-trigueiro/]
* [https://github.com/luizatrigueiro]


