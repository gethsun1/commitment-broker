#!/bin/bash
# Quick start script for the backend (without Docker)
# This is faster for development

set -e

cd "$(dirname "$0")/backend"

echo "🚀 Starting Commitment Broker Backend..."
echo ""

# Check if PostgreSQL is running
echo "Checking PostgreSQL connection..."
if ! docker compose ps postgres | grep -q "Up"; then
    echo "⚠️  PostgreSQL container is not running. Starting it..."
    cd ..
    docker compose up -d postgres
    echo "⏳ Waiting for PostgreSQL to be ready..."
    sleep 5
    cd backend
fi

# Check if virtual environment exists
if [ ! -d "env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv env
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source env/bin/activate

# Check if packages are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📥 Installing dependencies (this may take a few minutes)..."
    export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
    pip install --upgrade pip
    pip install fastapi uvicorn[standard] sqlalchemy alembic psycopg2-binary pydantic pydantic-settings python-dotenv langgraph langchain-google-genai langchain-core langchain httpx opik
fi

# Set environment variables
export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/commitment_broker}"

# Load .env file if it exists
if [ -f "../.env" ]; then
    export $(cat ../.env | grep -v '^#' | xargs)
fi

echo ""
echo "✅ Starting backend server on http://localhost:8000"
echo "📝 API docs will be available at http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
