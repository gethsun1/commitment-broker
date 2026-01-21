# Commitment Broker

![Commitment Broker Cover](frontend/public/assets/commitmentbroker_cover.png)

**Turning Financial Resolutions into Measurable Commitments**

Commitment Broker is an AI agent system designed to solve a familiar failure: people do not fail at setting financial goals — they fail at sticking to them.

This project transforms abstract financial intentions into structured behavioral commitments, continuously monitors real-world adherence, detects behavioral drift, and intervenes intelligently. Most importantly, the system evaluates itself, learning which interventions actually help users follow through.

**Built for real users. Designed for measurable change. Engineered with observability at its core.**

## Why Commitment Broker Exists

New Year's resolutions fail not due to lack of motivation, but lack of structure, feedback, and accountability.

Commitment Broker addresses this gap by:

- **Converting goals into enforceable weekly commitments**
- **Detecting early signs of behavioral drift**
- **Intervening before failure becomes abandonment**
- **Measuring whether the AI itself is helping — or merely talking**

> This is not a budgeting app.  
> It is a behavioral commitment engine.

## Core Capabilities

### Goal Structuring
- Collects financial goals (amount, timeframe, income cadence)
- Normalizes them into measurable weekly commitments
- Identifies risk moments where failure is statistically likely

### Commitment Engine
- Generates weekly savings targets
- Creates spending ceilings
- Defines behavioral constraints
- Stores commitments as versioned, auditable objects

### Behavioral Tracking
- Accepts real spending data (manual entry, demo-seeded)
- Aggregates behavior by week
- Produces deviation and consistency metrics

### Drift Detection
Detects:
- Overspending
- Missed contributions
- Pattern instability

Classifies drift by type:
- **Timing** — Spending happens at wrong times
- **Volume** — Spending exceeds ceiling
- **Consistency** — Irregular patterns

### Intelligent Interventions
Triggers context-aware interventions:
- **Gentle warnings** — For low severity, first-time issues
- **Recommitment prompts** — For medium severity, recurring issues
- **Goal renegotiation** — For high severity, significant deviations

Logs intervention timing, content, and outcome

### Evaluation & Observability (First-Class Feature)
Tracks:
- Goal adherence rate
- Intervention success rate
- False-positive interventions

Compares:
- Prompt versions
- Agent logic variants

All agent behavior is logged and evaluated using Opik

## System Architecture Overview

Commitment Broker is implemented as a closed-loop agent system orchestrated with LangGraph, ensuring explicit state transitions and auditable decision paths.

### Agent Workflow

1. **Goal Structuring Agent** — Parses user input into structured format
2. **Commitment Planning Agent** (Gemini Pro) — Generates weekly commitments
3. **Behavioral Tracking** — Aggregates spending data by week
4. **Drift Detection Agent** — Analyzes patterns for deviations
5. **Intervention Agent** (Gemini Flash) — Generates contextual interventions
6. **Evaluation Agent** — Tracks metrics and outcomes
7. **Feedback loop** into future planning

> Every loop improves the system's understanding of what actually works.

## Technology Stack

### Backend
- **FastAPI** — API and orchestration layer
- **PostgreSQL** — Durable behavioral data store
- **SQLAlchemy** — ORM
- **LangGraph** — Agent state machine
- **Google Gemini API**
  - `gemini-1.5-pro` for planning and reasoning
  - `gemini-1.5-flash` for fast interventions
- **Opik** — Observability, experiment tracking, evaluation

### Frontend
- **Next.js 14** (App Router)
- **TypeScript**
- **TailwindCSS**
- **shadcn/ui**

### Infrastructure
- **Docker & Docker Compose**
- Local-first, Vercel-ready deployment

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- Google Gemini API key
- Opik API key (optional, but recommended)

### Environment Setup

1. Copy `.env.example` to `.env` and fill in your API keys:
```bash
cp .env.example .env
```

2. Update `.env` with your credentials:
```
GEMINI_API_KEY=your_gemini_api_key_here
OPIK_API_KEY=your_opik_api_key_here
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/commitment_broker
```

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start PostgreSQL with Docker Compose:
```bash
cd ..
docker-compose up -d postgres
```

5. Run database migrations (if using Alembic):
```bash
cd backend
alembic upgrade head
```

6. Seed demo data:
```bash
python -m app.seed_demo
```

7. Start the backend server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Project Structure

```
commitment_broker/
├── backend/
│   ├── app/
│   │   ├── agents/          # LangGraph agent nodes
│   │   ├── api/             # FastAPI routes and schemas
│   │   ├── models/          # SQLAlchemy database models
│   │   ├── observability/   # Opik integration
│   │   ├── services/        # Business logic
│   │   ├── config.py        # Configuration
│   │   ├── database.py      # Database setup
│   │   └── main.py          # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/                 # Next.js App Router
│   ├── components/          # React components
│   ├── lib/                 # Utilities and API client
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Observability & Evaluation (Opik Integration)

Commitment Broker treats evaluation as a product feature, not an afterthought. The system uses [Opik](https://www.comet.com/opik) for comprehensive LLM observability, tracing all agent interactions, and tracking experiment performance.

### Opik Integration Overview

Opik is integrated at multiple levels to provide complete visibility into the AI system:

1. **LLM Call Tracing** - All Gemini API calls are automatically traced with OpikTracer
2. **LangGraph Workflow Tracing** - Complete workflow executions are tracked
3. **Experiment Tracking** - Custom metrics and intervention outcomes are logged

### What's Being Traced

#### LLM Agent Calls
All four LLM-powered agents are automatically traced:

- **Goal Structuring Agent** (`structure_goal`)
  - Tags: `langchain`, `gemini`, `goal_agent`
  - Captures: User input parsing, structured goal generation

- **Commitment Planning Agent** (`plan_commitment`)
  - Tags: `langchain`, `gemini`, `planning_agent`
  - Captures: Weekly target calculation, spending ceiling generation

- **Drift Detection Agent** (`detect_drift`)
  - Tags: `langchain`, `gemini`, `drift_agent`
  - Captures: Spending pattern analysis, drift classification

- **Intervention Agent** (`generate_intervention`)
  - Tags: `langchain`, `gemini`, `intervention_agent`
  - Captures: Contextual intervention message generation

#### LangGraph Workflows
Complete workflow executions are traced:
- **Commitment Creation Workflow** - Full goal-to-commitment pipeline
- **Tracking & Detection Workflow** - Drift detection and intervention flow

#### Automatic Metrics Captured
- **Input/Output** - Complete prompts and responses
- **Cost Tracking** - Token usage and API costs for Gemini calls
- **Latency** - Response times for each LLM call
- **Errors** - Any failures or exceptions during execution
- **Metadata** - Agent type, method names, workflow context

### Configuration

Opik is configured in `backend/app/main.py` and automatically initializes on application startup:

```python
import opik
from app.config import settings

# Configure Opik before app creation
if settings.opik_api_key:
    opik.configure(api_key=settings.opik_api_key)
```

### Environment Setup

Add your Opik API key to `.env`:

```bash
OPIK_API_KEY=your_opik_api_key_here
```

Get your API key from: https://comet.com/opik/your-workspace-name/get-started

### Viewing Traces

1. **Opik Dashboard** - Access your workspace dashboard to view all traces
2. **Filter by Tags** - Use tags like `goal_agent`, `planning_agent` to filter traces
3. **Workflow Visualization** - See complete LangGraph execution paths
4. **Cost Analysis** - Track spending across all LLM calls
5. **Performance Metrics** - Analyze latency and token usage patterns

### Tracked Metrics
- Weekly adherence rate
- Intervention effectiveness
- Behavioral recovery after failure
- Agent decision consistency
- LLM call costs and token usage
- Workflow execution times

### Experiments Compare
- Prompt versions
- Agent logic strategies
- Intervention timing policies
- Model performance (Pro vs Flash)

### Inspect
- Agent traces with full input/output
- Evaluation dashboards
- Before/after behavioral outcomes
- Cost and performance analytics
- Workflow execution graphs

### Implementation Details

#### GeminiService Integration
Located in `backend/app/services/gemini_service.py`:

```python
from opik.integrations.langchain import OpikTracer

# Each LLM method includes OpikTracer
tracer = OpikTracer(
    project_name="commitment-broker",
    tags=["langchain", "gemini", "goal_agent"],
    metadata={"agent_type": "goal_agent", "method": "structure_goal"}
)

response = await self.pro_model.ainvoke(
    messages,
    config={"callbacks": [tracer]}
)
```

#### LangGraph Integration
Located in `backend/app/agents/graph.py`:

```python
from opik.integrations.langchain import OpikTracer, track_langgraph

# Wrap compiled graphs for automatic tracing
opik_tracer = OpikTracer(
    project_name="commitment-broker",
    tags=["langchain", "langgraph", "workflow"]
)
self.graph = track_langgraph(compiled_graph, opik_tracer)
```

### Benefits

- **Complete Visibility** - See every LLM interaction in your system
- **Cost Tracking** - Monitor and optimize API spending
- **Performance Optimization** - Identify slow or inefficient calls
- **Debugging** - Trace issues through complete execution paths
- **Experiment Tracking** - Compare different prompt versions and strategies

## API Overview

- `POST /api/goals` — Create a new goal and generate commitment plan
- `GET /api/commitments/{id}` — Get commitment details
- `POST /api/spending` — Add spending entry
- `GET /api/commitments/{id}/drift` — Check for drift in spending behavior
- `GET /api/commitments/{id}/interventions` — Get intervention history
- `GET /api/commitments/{id}/evaluation` — Get evaluation metrics
- `PATCH /api/interventions/{id}/outcome` — Update intervention outcome

## Demo Scenario

The seeded demo illustrates a complete behavioral loop:

**User goal:** Save $5,000 in 6 months

**Commitment generated:**
- $208 weekly savings target
- $150 weekly discretionary spending ceiling

**Observed behavior:**
- Weeks 1–2: compliant
- Week 3: overspend by $50 (detected drift)
- Intervention triggered
- Week 4: behavior corrected

**Evaluation results:**
- 75% adherence rate
- 100% intervention success
- Clear recovery after failure

> This demo intentionally includes failure — because recovery is the real signal of success.

View the demo at: `https://commitmentbroker.vercel.app/`

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Database Migrations

```bash
cd backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## License

MIT
