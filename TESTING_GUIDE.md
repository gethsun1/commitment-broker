# Testing Guide - Commitment Broker

Quick start guide to run and test the Commitment Broker system.

## Prerequisites Check

First, verify you have all requirements:

```bash
# Check Python version (should be 3.11+)
python3 --version

# Check Node.js version (should be 18+)
node --version

# Check Docker
docker --version
docker compose version
```

## Step-by-Step Startup

### 1. Start PostgreSQL Database

**Option A: Using Docker Compose (Recommended)**
```bash
cd /home/quantum/Documents/GKM/commitment_broker

# Start PostgreSQL container
docker compose up -d postgres

# Verify it's running
docker compose ps
# Or check logs
docker compose logs postgres
```

**Option B: If PostgreSQL is already running locally**
```bash
# Skip Docker if PostgreSQL is already running on port 5432
# Just ensure your .env has the correct connection string
```

### 2. Verify Environment Variables

Ensure your `.env` file exists and has:
```bash
cd /home/quantum/Documents/GKM/commitment_broker
cat .env

# Should contain:
# GEMINI_API_KEY=your_key_here
# OPIK_API_KEY=your_key_here (optional)
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/commitment_broker
```

### 3. Setup Backend

```bash
cd /home/quantum/Documents/GKM/commitment_broker/backend

# Create virtual environment (if not exists)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create database tables (runs automatically on startup, but you can verify)
python3 -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine)"

# Seed demo data
python3 -m app.seed_demo

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 4. Setup Frontend (New Terminal)

Open a **new terminal window** (keep backend running):

```bash
cd /home/quantum/Documents/GKM/commitment_broker/frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

**Expected output:**
```
- ready started server on 0.0.0.0:3000
- event compiled client and server successfully
```

## Testing the Application

### 1. Health Check

**Backend API:**
```bash
# Test backend is running
curl http://localhost:8000/health

# Expected: {"status":"healthy"}

# Check API root
curl http://localhost:8000/

# Expected: {"message":"Commitment Broker API","status":"running"}
```

**Frontend:**
Open browser and navigate to: `http://localhost:3000`

### 2. Create a New Goal via API

```bash
curl -X POST http://localhost:8000/api/goals \
  -H "Content-Type: application/json" \
  -d '{
    "goal_description": "Save $5000 for emergency fund",
    "target_amount": 5000.0,
    "timeframe": "6 months",
    "income_frequency": "monthly",
    "risk_moments": ["End of month", "Payday"],
    "user_id": "test_user"
  }'
```

This will return a commitment object with an `id`. Save this ID for next steps.

### 3. View Commitment Details

```bash
# Replace {commitment_id} with the ID from step 2
curl http://localhost:8000/api/commitments/{commitment_id}
```

### 4. Add Spending Data

```bash
# Replace {commitment_id} with your commitment ID
curl -X POST http://localhost:8000/api/spending \
  -H "Content-Type: application/json" \
  -d '{
    "commitment_id": {commitment_id},
    "amount": 120.0,
    "category": "Groceries",
    "week_number": 1,
    "description": "Week 1 groceries"
  }'

# Add another entry (compliant)
curl -X POST http://localhost:8000/api/spending \
  -H "Content-Type: application/json" \
  -d '{
    "commitment_id": {commitment_id},
    "amount": 130.0,
    "category": "Utilities",
    "week_number": 2,
    "description": "Week 2 utilities"
  }'

# Add overspending entry (will trigger drift detection)
curl -X POST http://localhost:8000/api/spending \
  -H "Content-Type: application/json" \
  -d '{
    "commitment_id": {commitment_id},
    "amount": 200.0,
    "category": "Entertainment",
    "week_number": 3,
    "description": "Week 3 - overspent"
  }'
```

### 5. Check Drift Detection

```bash
# Check if drift was detected
curl http://localhost:8000/api/commitments/{commitment_id}/drift
```

### 6. View Interventions

```bash
# View any triggered interventions
curl http://localhost:8000/api/commitments/{commitment_id}/interventions
```

### 7. Get Evaluation Metrics

```bash
# Get performance evaluation
curl http://localhost:8000/api/commitments/{commitment_id}/evaluation
```

### 8. Test via Frontend UI

1. **Create Goal:**
   - Navigate to `http://localhost:3000/goals/new`
   - Fill out the goal form
   - Submit to create a commitment

2. **View Commitment:**
   - After creating, you'll be redirected to `/commitments/{id}`
   - View commitment details, spending tracker, and interventions

3. **Add Spending:**
   - Use the spending tracker form on the commitment page
   - Add multiple entries to see drift detection

4. **View Evaluations:**
   - Navigate to `http://localhost:3000/evaluation`
   - See overall metrics and agent performance

## Using the Demo Data

The seeded demo data provides a complete example:

1. Run the seeder (if you haven't already):
```bash
cd backend
source venv/bin/activate
python3 -m app.seed_demo
```

2. The seeder will output a commitment ID like:
```
✓ Created commitment ID: 1
```

3. Access the demo in the frontend:
   - Navigate to `http://localhost:3000/commitments/1`
   - You'll see pre-populated spending data, interventions, and evaluations

## Common Issues & Solutions

### Issue: Port 5432 already in use
**Solution:** PostgreSQL is already running. Either:
- Use existing PostgreSQL instance (update DATABASE_URL in .env)
- Stop existing PostgreSQL: `sudo systemctl stop postgresql`
- Or change port in docker-compose.yml

### Issue: Module not found errors
**Solution:** 
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Frontend can't connect to backend
**Solution:** 
- Check backend is running on port 8000
- Verify CORS is configured (should allow localhost:3000)
- Check browser console for errors

### Issue: Database connection errors
**Solution:**
```bash
# Verify PostgreSQL is running
docker compose ps postgres

# Check database exists
docker compose exec postgres psql -U postgres -c "\l"

# Create database if needed
docker compose exec postgres psql -U postgres -c "CREATE DATABASE commitment_broker;"
```

## Testing Complete Flow

1. ✅ Database running
2. ✅ Backend server running (`http://localhost:8000`)
3. ✅ Frontend server running (`http://localhost:3000`)
4. ✅ Demo data seeded
5. ✅ Create a goal via UI
6. ✅ Add spending entries
7. ✅ Verify drift detection works
8. ✅ Check interventions are triggered
9. ✅ View evaluation metrics

## Quick Test Script

Save this as `quick-test.sh`:

```bash
#!/bin/bash

echo "Testing Commitment Broker API..."

# Health check
echo "1. Health check..."
curl -s http://localhost:8000/health | jq .

# Create goal
echo "2. Creating goal..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/goals \
  -H "Content-Type: application/json" \
  -d '{
    "goal_description": "Test Goal",
    "target_amount": 1000.0,
    "timeframe": "3 months",
    "income_frequency": "monthly",
    "user_id": "test_user"
  }')

COMMITMENT_ID=$(echo $RESPONSE | jq -r '.id')
echo "Created commitment ID: $COMMITMENT_ID"

# Get commitment
echo "3. Getting commitment..."
curl -s http://localhost:8000/api/commitments/$COMMITMENT_ID | jq .

echo "✅ Basic API test complete!"
echo "Visit http://localhost:3000/commitments/$COMMITMENT_ID to see in UI"
```

Make it executable and run:
```bash
chmod +x quick-test.sh
./quick-test.sh
```

## Next Steps

- Review the demo scenario at `/commitments/{demo_id}`
- Check evaluation dashboard at `/evaluation`
- Test intervention triggers by overspending
- Experiment with different goal parameters
- Review Opik logs for agent behavior (if configured)
