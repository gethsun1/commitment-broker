# Database Migrations

## Adding Evaluation Fields Migration

This migration adds new columns to the `evaluations` table to support AI-generated evaluation metrics.

### New Columns Added

- `evaluation_snapshot` (JSON) - Full AI-generated evaluation output
- `behavioral_recovery_score` (INTEGER) - 0-100 score for recovery effectiveness
- `behavioral_recovery_interpretation` (TEXT) - AI-generated explanation
- `adherence_trend` (VARCHAR) - "improving", "declining", or "stable"
- `adherence_confidence` (FLOAT) - Confidence score (0.0-1.0)
- `intervention_justification` (TEXT) - AI explanation for interventions
- `drift_classification_confidence` (FLOAT) - Confidence in drift classification
- `planning_accuracy` (FLOAT) - Planning agent accuracy score
- `drift_detection_precision` (FLOAT) - Drift detection precision score
- `intervention_timing` (VARCHAR) - "optimal", "early", or "late"

### Running the Migration

**Option 1: Using Python script (Recommended)**
```bash
cd backend
python run_migration.py
```

**Option 2: Using SQL directly**
```bash
psql -d commitment_broker -f migrations/add_evaluation_fields.sql
```

**Option 3: Using Docker**
```bash
docker exec -i commitment_broker_postgres psql -U postgres -d commitment_broker < backend/migrations/add_evaluation_fields.sql
```

### Verification

After running the migration, verify the columns were added:
```sql
\d evaluations
```

Or using Python:
```python
from app.database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
columns = [col['name'] for col in inspector.get_columns('evaluations')]
print(columns)
```
