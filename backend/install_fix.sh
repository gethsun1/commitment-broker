#!/bin/bash
# Fix for psycopg2-binary installation on Python 3.13

echo "Fixing psycopg2-binary installation..."

# Upgrade pip first
pip install --upgrade pip setuptools wheel

# Try installing psycopg2-binary first (may fail, but let's try)
pip install psycopg2-binary --upgrade || echo "psycopg2-binary installation failed"

# Install other requirements (they might work even if psycopg2-binary failed)
echo "Installing other requirements..."
pip install fastapi uvicorn[standard] sqlalchemy alembic pydantic pydantic-settings python-dotenv langgraph langchain-google-genai langchain-core langchain opik httpx

# If psycopg2-binary still failed, provide instructions
if ! python -c "import psycopg2" 2>/dev/null; then
    echo ""
    echo "⚠️  psycopg2-binary installation failed."
    echo ""
    echo "Please run one of these solutions:"
    echo ""
    echo "Option 1: Install PostgreSQL dev libraries (requires sudo):"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install -y libpq-dev python3-dev"
    echo "  pip install psycopg2-binary"
    echo ""
    echo "Option 2: Use psycopg3 instead (no system dependencies):"
    echo "  pip install psycopg[binary]"
    echo "  (Then we'll need to update database.py)"
    echo ""
else
    echo "✅ psycopg2-binary installed successfully!"
fi
