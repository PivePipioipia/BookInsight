# BookInsight Agent

A personalized AI Book Assistant built with a Multi-tool Agent architecture, RAG-Fusion, and Text-to-SQL.

This is an end-to-end AI Engineer portfolio project demonstrating the full lifecycle of building a modern AI system—from raw data processing to a fully interactive web application.


## Demo
You can watch the demo video for my BookInsight project here:
[Watch the Demo Video on YouTube](https://www.youtube.com/watch?v=jZ-ebkbY-XI)

Demo workflow example:

1. (Test RAG) What is the book 'The Hobbit' about?

2. (Test Memory) Who is the author of that book?

3. (RAG + Memory) Show me other books by that author

4. (Test SQL) Okay. Now, show me the cheapest book in the 'Horror' category


5. (Test Personalization) I liked our talk about 'The Hobbit' (Fantasy), but I also asked for 'Horror'. Can you recommend a "Dark Fantasy" book?

## Features

This project is a multi-tool Agent built with LangChain, capable of:

- Advanced RAG (RAG-Fusion):

    + Moves beyond basic RAG by implementing RAG-Fusion (Query Expansion + Reciprocal Rank Fusion) to improve the relevance and accuracy of search results across a 100,000-book dataset.

    + Uses the BAAI/bge-small-en-v1.5 embedding model and a FAISS vector store for semantic search.

- Structured Querying (Text-to-SQL):

    + The Agent can autonomously write and execute SQL queries (via SQLDatabaseTool) to answer complex, structured questions (e.g., "What is the most expensive book?", "How many books does author X have?").

- Personalization & Statefulness:

    + The Agent can "learn" and "remember" user preferences (e.g., "I like 'Science Fiction'") by using a SavePreferenceTool to write to the database.

    + It can proactively make recommendations based on saved preferences (GetPersonalizedRecommendationTool), demonstrating advanced "tool-calling-tool" logic.

- Conversational Memory:

    + The Agent maintains the context of the conversation, allowing for natural follow-up questions (e.g., "How much does that book cost?").

- End-to-End API Architecture:

    + The entire Agent is wrapped in a FastAPI Backend API, fully decoupling the AI logic from the user interface.

    + The UI is built with Streamlit, which communicates with the API via HTTP requests.

## System Architecture
1. Frontend (Streamlit): The chat interface (app.py) the user interacts with. It sends requests to the Backend API.

2. Backend (FastAPI): The server (src/app/main.py) that receives requests, wraps the AgentExecutor, and loads all models/databases on startup.

3. Agent (LangChain): The "brain" (src/agent/agent.py) that orchestrates the 4 tools (RAG, SQL, Save, Rec) and manages memory to make decisions.

4. Data Storage (Hybrid):

    - SQL Database (SQLite): Stores all structured metadata for 100k books (e.g., title, price, author_name, rating). Used by the SQLTool.

    - Vector Store (FAISS): Stores 100k vectors (from description, features, author_about) for semantic search. Used by the RAGTool.

## Tech Stack

- Python 3.11

- AI & Agent: LangChain, OpenAI (GPT-4o), SentenceTransformers (BGE)

- Vector Search: FAISS

- Database: SQLite, Pandas

- Backend: FastAPI, Uvicorn

- Frontend: Streamlit

## How to Run
This project requires running two servers in parallel (Backend & Frontend).

1. Environment Setup
# Clone the repo
git clone [YOUR_REPO_URL]
cd BookInsight

# Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\activate  # (On Windows)
# source venv/bin/activate  (On macOS/Linux)

# Install dependencies
pip install -r requirements.txt

2. (CRITICAL) Build the Data Foundation

This project does not commit the database or vector store to Git. You must build them from the clean data file.

    1. Download the clean data file (amazon_books_clean_100ksamples.parquet) and place it in the data/ directory (or as specified in src/utils/config.py).

    2. Open and run the entire notebooks/2_build_database.ipynb notebook. (This step will generate data/database/books.db and the files in data/vectorstores/. You only need to do this once.)

3. Set API Key
Set your OpenAI API Key as an environment variable in your terminal:

# Using PowerShell (or set in Run Configurations)
$env:OPENAI_API_KEY="sk-..."

4. Run the Application (2 Terminals)
You need two separate terminals (with the venv activated and API key set).

- Terminal 1: Run the Backend (FastAPI)

uvicorn src.app.main:app --reload

Wait for this terminal to show "Application startup complete."

- Terminal 2: Run the Frontend (Streamlit)
streamlit run app.py

Streamlit will automatically open http://localhost:8501 in your browser.
