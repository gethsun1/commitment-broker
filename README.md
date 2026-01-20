# Commitment Broker

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

Commitment Broker treats evaluation as a product feature, not an afterthought.

### Tracked Metrics
- Weekly adherence rate
- Intervention effectiveness
- Behavioral recovery after failure
- Agent decision consistency

### Experiments Compare
- Prompt versions
- Agent logic strategies
- Intervention timing policies

### Judges Can Inspect
- Agent traces
- Evaluation dashboards
- Before/after behavioral outcomes

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

View the demo at: `http://localhost:3000/commitments/{commitment_id}`

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
