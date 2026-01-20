# Python 3.13 Compatibility Fix

Python 3.13 is very new and several packages haven't been updated yet. Here are solutions:

## Issue 1: pydantic-core (pydantic 2.5.0)
**Error**: `ForwardRef._evaluate() missing 1 required keyword-only argument: 'recursive_guard'`

**Solution**: Upgrade pydantic to 2.9.0+
```bash
pip install --upgrade "pydantic>=2.9.0" "pydantic-settings>=2.6.0"
```

## Issue 2: levenshtein (Python-Levenshtein)
**Error**: `_PyLong_AsByteArray` API changes in Python 3.13

**Solution**: 
1. Remove levenshtein dependency if not critical, or
2. Use rapidfuzz directly (opik already uses it)
3. Or install system build tools and let it compile

Try installing without opik first to see if it's required:
```bash
pip install -r requirements.txt --no-deps
pip install fastapi uvicorn sqlalchemy alembic psycopg2-binary pydantic pydantic-settings python-dotenv langgraph langchain-google-genai langchain-core langchain httpx
```

## Issue 3: tiktoken
**Error**: PyO3 doesn't support Python 3.13 (max is 3.12)

**Solution**: 
1. Set environment variable to allow forward compatibility:
```bash
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
pip install tiktoken
```

2. Or upgrade tiktoken to latest version:
```bash
pip install --upgrade tiktoken
```

## Quick Fix (All at once)

Run this in your terminal:

```bash
cd backend
source env/bin/activate  # Your venv is called 'env'

# Allow PyO3 forward compatibility for Python 3.13
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1

# Upgrade problematic packages
pip install --upgrade "pydantic>=2.9.0" "pydantic-settings>=2.6.0"

# Try installing tiktoken with forward compatibility
pip install tiktoken

# Install remaining packages, skipping problematic ones temporarily
pip install fastapi uvicorn[standard] sqlalchemy alembic psycopg2-binary python-dotenv langgraph langchain-google-genai langchain-core langchain httpx

# If levenshtein is still failing, you can skip opik for now:
# pip install opik --no-deps
# Then manually install opik's other dependencies except levenshtein
```

## Alternative: Use Python 3.11 or 3.12

If issues persist, create a new virtual environment with Python 3.11:

```bash
cd backend
rm -rf env
python3.11 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Testing Without Opik (Temporary)

If opik is causing issues, you can temporarily remove it:

1. Comment out opik imports in code
2. Install everything else
3. Come back to opik later when dependencies are updated
