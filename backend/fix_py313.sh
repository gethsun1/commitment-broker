#!/bin/bash
# Fix Python 3.13 compatibility issues

echo "🔧 Fixing Python 3.13 compatibility issues..."

# Ensure we're in the backend directory
cd "$(dirname "$0")"

# Activate virtual environment (env, not venv)
source env/bin/activate

# Upgrade pip first
echo "📦 Upgrading pip..."
pip install --upgrade pip setuptools wheel

# Set PyO3 forward compatibility flag for Python 3.13
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1

# Fix 1: Upgrade pydantic to 2.9.0+ (supports Python 3.13)
echo "🔧 Upgrading pydantic to Python 3.13 compatible version..."
pip install --upgrade "pydantic>=2.9.0" "pydantic-settings>=2.6.0"

# Fix 2: Install packages that don't depend on problematic ones
echo "📦 Installing core packages..."
pip install fastapi uvicorn[standard] sqlalchemy alembic psycopg2-binary python-dotenv httpx

# Fix 3: Install langchain packages
echo "📦 Installing LangChain packages..."
pip install langgraph langchain-core langchain-google-genai langchain

# Fix 4: Try installing tiktoken with forward compatibility
echo "🔧 Installing tiktoken with Python 3.13 forward compatibility..."
PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 pip install tiktoken || echo "⚠️  tiktoken installation failed - this is from opik dependency"

# Fix 5: Install opik without levenshtein if possible, or skip it
echo "📦 Installing opik (this may fail due to levenshtein)..."
pip install opik || echo "⚠️  opik installation failed - levenshtein doesn't support Python 3.13 yet"

# Alternative: Install opik dependencies manually except levenshtein
if ! pip show opik > /dev/null 2>&1; then
    echo "⚠️  Opik installation failed. Installing dependencies manually (without levenshtein)..."
    pip install pandas pytest tqdm uuid7 rich openai langchain-openai || true
    echo "⚠️  Note: Opik full functionality may be limited without levenshtein"
    echo "⚠️  You can comment out opik imports in the code to run without it"
fi

echo ""
echo "✅ Installation attempt complete!"
echo ""
echo "If opik still fails, you can:"
echo "1. Comment out opik imports in app/observability/opik_client.py"
echo "2. Make OpikClient methods no-ops if opik isn't installed"
echo "3. Or use Python 3.11/3.12 instead"
echo ""
echo "To verify installation:"
echo "  python -c 'import fastapi, sqlalchemy, pydantic; print(\"✅ Core packages OK\")'"
