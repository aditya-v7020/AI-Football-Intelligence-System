# ⚽ AI Football Intelligence & Player Recommendation System

A full-stack, multi-agent AI system for football analysis, player recommendations, scouting, and comparisons.

## 🏗️ Architecture

```
USER → React Frontend → FastAPI Backend → LangGraph Multi-Agent Pipeline
                                              │
                                 ┌─────────────┼─────────────┐
                                 │             │             │
                            API-Football   Tavily       Groq/Llama 3.3
                            (Player Data)  (Web Search) (AI Analysis)
                                 │             │             │
                                 └─────────────┼─────────────┘
                                              │
                                         PostgreSQL
                                    (Conversation Memory)
```

### Multi-Agent Pipeline

1. **Player Agent** — Retrieves structured player data from API-Football
2. **Research Agent** — Searches the web via Tavily for recent news, transfers, injuries
3. **Analysis Agent** — Analyzes all collected data with LLM-powered intelligence
4. **Final Agent** — Generates a comprehensive, formatted response

## ✨ Features

- **AI Football Chat** — ChatGPT-style interface for football questions
- **Player Search** — Search any player with API-Football data
- **Player Comparison** — Side-by-side comparison with radar charts
- **AI Scout** — Natural language scouting with AI-generated reports
- **Dashboard** — System status, quick actions, recent searches
- **Conversation Memory** — PostgreSQL-backed thread persistence
- **Source Attribution** — Clear distinction between API data and web research
- **ML-Ready Architecture** — Prepared for future dataset integration

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | React 18 + Vite |
| Backend | FastAPI (Python) |
| AI Pipeline | LangGraph + LangChain |
| LLM | Groq / Llama 3.3 70B |
| Football Data | API-Football (api-sports.io) |
| Web Research | Tavily Search API |
| Database | PostgreSQL |
| Charts | Chart.js / react-chartjs-2 |
| Routing | React Router v6 |

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL** running on localhost:5432
- API keys for: Groq, API-Football, Tavily

## 🚀 Setup & Run (Windows / VS Code)

### 1. Clone and Configure

```bash
cd d:\ITR\RoughWork\MULTI_AGENT_SYSTEM
copy .env.example .env
# Edit .env with your actual API keys and database credentials
```

### 2. Install Backend Dependencies

```bash
# Option A: Using existing venv
.\venv\Scripts\activate
pip install -r backend\requirements.txt

# Option B: Create new venv
python -m venv venv
.\venv\Scripts\activate
pip install -r backend\requirements.txt
```

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### 4. Start PostgreSQL

Make sure PostgreSQL is running on port 5432. Create the database if needed:

```sql
CREATE DATABASE langgraph_memory_demo;
```

### 5. Run Backend (Terminal 1)

```bash
# Must run from the root project directory: d:\ITR\RoughWork\MULTI_AGENT_SYSTEM
.\venv\Scripts\activate
python -m uvicorn backend.server:app --reload --host 127.0.0.1 --port 8000
```

Backend will be available at: **http://localhost:8000**
API docs at: **http://localhost:8000/docs**

### 6. Run Frontend (Terminal 2)

```bash
cd d:\ITR\RoughWork\MULTI_AGENT_SYSTEM\frontend
npm run dev
```

Frontend will be available at: **http://localhost:5173**

## 📁 Project Structure

```
MULTI_AGENT_SYSTEM/
├── .env                    # Environment variables (not committed)
├── .env.example            # Template for .env
├── .gitignore
├── README.md
├── main.py                 # Original CLI entry point (preserved)
├── tools/                  # Original tools (preserved)
│
├── backend/                # FastAPI backend
│   ├── server.py           # FastAPI app
│   ├── config.py           # Centralized config
│   ├── requirements.txt    # Python dependencies
│   ├── api/                # REST endpoints
│   │   ├── chat.py
│   │   ├── players.py
│   │   ├── scout.py
│   │   └── health.py
│   ├── core/               # LangGraph system
│   │   ├── agents.py       # All 4 agents
│   │   ├── graph.py        # Graph construction
│   │   ├── state.py        # FootballState
│   │   └── tools/          # API-Football + Tavily
│   ├── services/           # Business logic
│   │   ├── chat_service.py
│   │   ├── player_service.py
│   │   ├── comparison_service.py
│   │   └── scout_service.py
│   ├── models/             # Pydantic schemas
│   │   └── schemas.py
│   └── ml/                 # ML module (dataset-ready)
│       ├── preprocessor.py
│       ├── similarity.py
│       └── recommender.py
│
└── frontend/               # React + Vite
    ├── src/
    │   ├── api/client.js   # API client
    │   ├── components/     # Reusable components
    │   └── pages/          # Dashboard, Chat, Search, etc.
    └── package.json
```

## 🔒 Security

- All API keys are stored in `.env` (never committed)
- Frontend never accesses external APIs directly — all requests go through FastAPI
- CORS is configured for the Vite dev server only
- Input validation on all endpoints

## 📊 ML Module (Future)

The `backend/ml/` module is prepared for a football player dataset. See `backend/ml/README.md` for instructions on:
- Adding a CSV/JSON dataset
- Configuring preprocessing
- Enabling cosine similarity / KNN
- Activating ML-powered recommendations

## 📝 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | System health check |
| POST | `/api/chat` | Send football query to AI |
| GET | `/api/players/search?q=` | Search players |
| GET | `/api/players/news?name=` | Get player news |
| POST | `/api/players/compare` | Compare two players |
| POST | `/api/scout` | Run AI scouting |

# One question are we using the same API key for all the agents

Not exactly. In your current architecture, the agents share services, but different services use different API keys:

Player Agent → FOOTBALL_API_KEY → API-Football
Research Agent → TAVILY_API_KEY → Tavily
Analysis Agent → GROQ_API_KEY → Llama 3.3 70B
Final Agent → GROQ_API_KEY → Llama 3.3 70B

So Analysis Agent + Final Agent use the same Groq API key, which is completely fine.

# CODE TO RUN THE PROJECT

# Terminal 1 — Backend (Run from project root directory)
cd "d:\ITR\ITR ASSIGNMENTS COPY BRANCH\MULTI_AGENT_SYSTEM"
.\venv\Scripts\activate
python -m uvicorn backend.server:app --reload --host 127.0.0.1 --port 8000

# Terminal 2 — Frontend (Run from frontend directory)
cd "d:\ITR\ITR ASSIGNMENTS COPY BRANCH\MULTI_AGENT_SYSTEM\frontend"
npm run dev

# Website Link
https://ai-football-intelligence-system.vercel.app/