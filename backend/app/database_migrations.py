"""
Database migration utilities.
Handles automatic migration of database schema.
"""
from sqlalchemy import text, inspect
from app.database import engine
import logging

logger = logging.getLogger(__name__)


def run_evaluation_fields_migration():
    """
    Run migration to add new evaluation fields.
    Uses IF NOT EXISTS to be idempotent (safe to run multiple times).
    """
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
    
    try:
        # Check if evaluations table exists
        inspector = inspect(engine)
        if 'evaluations' not in inspector.get_table_names():
            logger.warning("⚠️  Evaluations table does not exist. Skipping migration.")
            return False
        
        # Check if migration is needed (check if any new column exists)
        columns = [col['name'] for col in inspector.get_columns('evaluations')]
        if 'evaluation_snapshot' in columns:
            logger.info("✅ Evaluation fields migration already applied.")
            return True
        
        logger.info("🔄 Running database migration to add evaluation fields...")
        
        with engine.begin() as conn:
            # Execute migration statements
            statements = [s.strip() for s in migration_sql.strip().split(';') if s.strip()]
            for statement in statements:
                if statement:
                    conn.execute(text(statement))
        
        logger.info("✅ Migration completed successfully!")
        logger.info("Added columns: evaluation_snapshot, behavioral_recovery_score, behavioral_recovery_interpretation, adherence_trend, adherence_confidence, intervention_justification, drift_classification_confidence, planning_accuracy, drift_detection_precision, intervention_timing")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        # Don't raise - allow app to start even if migration fails
        # The migration can be run manually via API endpoint
        return False


def check_migration_status():
    """Check if migration has been applied."""
    try:
        inspector = inspect(engine)
        if 'evaluations' not in inspector.get_table_names():
            return {"status": "table_not_found", "migrated": False}
        
        columns = [col['name'] for col in inspector.get_columns('evaluations')]
        has_new_fields = 'evaluation_snapshot' in columns
        
        return {
            "status": "ok",
            "migrated": has_new_fields,
            "columns": columns
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "migrated": False}
