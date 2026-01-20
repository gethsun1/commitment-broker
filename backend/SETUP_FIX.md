# Backend Setup Fix for Python 3.13

If you encounter the `psycopg2-binary` installation error on Python 3.13, here are solutions:

## Solution 1: Install PostgreSQL Development Libraries (Recommended)

This allows `psycopg2-binary` to build from source:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y libpq-dev python3-dev

# Then retry:
pip install -r requirements.txt
```

## Solution 2: Use Latest psycopg2-binary

The requirements.txt has been updated to allow newer versions that may have Python 3.13 wheels:

```bash
# Update pip first
pip install --upgrade pip

# Install with updated requirements
pip install -r requirements.txt
```

## Solution 3: Use psycopg (psycopg3) - Modern Alternative

If psycopg2-binary continues to fail, we can switch to `psycopg` (the newer, pure Python version):

```bash
# Replace psycopg2-binary with psycopg in requirements.txt
# Change: psycopg2-binary>=2.9.9,<3.0.0
# To: psycopg[binary]>=3.1.0
```

Then update `backend/app/database.py` to use `psycopg` instead of `psycopg2`.

## Solution 4: Use Python 3.11 or 3.12

Python 3.11/3.12 have better wheel support:

```bash
# Create new venv with Python 3.11
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
