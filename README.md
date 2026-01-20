# Commitment Broker

An AI agent system that converts financial goals into enforceable behavioral commitments, tracks adherence over time, detects deviation patterns, and intervenes intelligently.

## Features

- **Goal Intake**: Collect financial goals with amount, timeframe, income frequency, and risk moments
- **Commitment Engine**: Generate weekly savings targets and behavioral constraints
- **Behavior Tracking**: Accept spending data and aggregate by week
- **Drift Detection**: Detect overspending, missed contributions, and classify drift types
- **Intervention Agent**: Trigger contextual interventions (gentle warnings, recommitment prompts, goal renegotiation)
- **Evaluation & Observability**: Track adherence rates, intervention success, and compare agent performance via Opik

## Tech Stack

### Backend
- **FastAPI** - Python web framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **LangGraph** - Agent orchestration
- **Google Gemini API** - AI models (Pro for planning, Flash for interventions)
- **Opik** - Observability and experiment tracking

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **TailwindCSS** - Styling
- **shadcn/ui** - UI components

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

## API Endpoints

- `POST /api/goals` - Create a new goal and generate commitment plan
- `GET /api/commitments/{id}` - Get commitment details
- `POST /api/spending` - Add spending entry
- `GET /api/commitments/{id}/drift` - Check for drift in spending behavior
- `GET /api/commitments/{id}/interventions` - Get intervention history
- `GET /api/commitments/{id}/evaluation` - Get evaluation metrics
- `PATCH /api/interventions/{id}/outcome` - Update intervention outcome

## Demo Scenario

The seeded demo data includes:
1. One user with goal: "Save $5000 in 6 months"
2. Generated commitment: $208/week savings target, $150/week spending ceiling
3. Spending pattern:
   - Week 1-2: Compliant
   - Week 3: Overspends by $50 (failure)
   - Week 4: Back on track (improvement)
4. One intervention triggered in Week 3 (gentle warning)
5. Evaluation shows 75% adherence rate, 100% intervention success

View the demo at: `http://localhost:3000/commitments/{commitment_id}`

## Architecture

The system uses LangGraph to orchestrate a state machine workflow:

1. **Goal Structuring Agent** - Parses user input into structured format
2. **Planning Agent** - Generates weekly commitments (uses Gemini Pro)
3. **Drift Detection Agent** - Analyzes spending patterns for deviations
4. **Intervention Agent** - Generates contextual interventions (uses Gemini Flash)
5. **Evaluation Agent** - Tracks metrics and outcomes

All agent interactions are logged to Opik for observability and prompt version comparison.

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
