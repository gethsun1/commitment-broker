#!/usr/bin/env python3
"""
Run database migration to add new evaluation fields.
This script adds the new columns for AI-generated evaluation metrics.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.database import engine
from app.config import settings

def run_migration():
    """Run SQL migration to add new evaluation fields."""
    migration_sql = """
    -- Add evaluation_snapshot column (JSON)
    ALTER TABLE evaluations 
    ADD COLUMN IF NOT EXISTS evaluation_snapshot JSON;

    -- Add behavioral_recovery_score column (Integer, 0-100)
    ALTER TABLE evaluations 
    ADD COLUMN IF NOT EXISTS behavioral_recovery_score INTEGER;

    -- Add behavioral_recovery_interpretation column (Text)
    ALTER TABLE evaluations 
    ADD COLUMN IF NOT EXISTS behavioral_recovery_interpretation TEXT;

    -- Add adherence_trend column (String)
    ALTER TABLE evaluations 
    ADD COLUMN IF NOT EXISTS adherence_trend VARCHAR(50);

    -- Add adherence_confidence column (Float)
    ALTER TABLE evaluations 
    ADD COLUMN IF NOT EXISTS adherence_confidence FLOAT;

    -- Add intervention_justification column (Text)
    ALTER TABLE evaluations 
    ADD COLUMN IF NOT EXISTS intervention_justification TEXT;

    -- Add drift_classification_confidence column (Float)
    ALTER TABLE evaluations 
    ADD COLUMN IF NOT EXISTS drift_classification_confidence FLOAT;

    -- Add planning_accuracy column (Float)
    ALTER TABLE evaluations 
    ADD COLUMN IF NOT EXISTS planning_accuracy FLOAT;

    -- Add drift_detection_precision column (Float)
    ALTER TABLE evaluations 
    ADD COLUMN IF NOT EXISTS drift_detection_precision FLOAT;

    -- Add intervention_timing column (String)
    ALTER TABLE evaluations 
    ADD COLUMN IF NOT EXISTS intervention_timing VARCHAR(50);
    """
    
    print("🔄 Running database migration to add evaluation fields...")
    print(f"📊 Database: {settings.database_url.split('@')[-1] if '@' in settings.database_url else settings.database_url}")
    
    try:
        with engine.begin() as conn:
            # Execute migration statements
            statements = [s.strip() for s in migration_sql.strip().split(';') if s.strip()]
            for statement in statements:
                if statement:
                    conn.execute(text(statement))
        
        print("✅ Migration completed successfully!")
        print("\nAdded columns:")
        print("  - evaluation_snapshot (JSON)")
        print("  - behavioral_recovery_score (INTEGER)")
        print("  - behavioral_recovery_interpretation (TEXT)")
        print("  - adherence_trend (VARCHAR)")
        print("  - adherence_confidence (FLOAT)")
        print("  - intervention_justification (TEXT)")
        print("  - drift_classification_confidence (FLOAT)")
        print("  - planning_accuracy (FLOAT)")
        print("  - drift_detection_precision (FLOAT)")
        print("  - intervention_timing (VARCHAR)")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("\nYou can also run the SQL migration manually:")
        print("  psql -d commitment_broker -f migrations/add_evaluation_fields.sql")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()
