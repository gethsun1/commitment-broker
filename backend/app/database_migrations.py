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


def run_escrow_migration():
    """
    Create escrow_commitments table if not exists.
    Idempotent; safe to run multiple times.
    """
    migration_sql = """
    CREATE TABLE IF NOT EXISTS escrow_commitments (
        id SERIAL PRIMARY KEY,
        commitment_id INTEGER NOT NULL UNIQUE REFERENCES commitments(id),
        wallet_address VARCHAR(42) NOT NULL,
        tx_hash VARCHAR(66),
        amount BIGINT NOT NULL,
        unlock_timestamp BIGINT NOT NULL,
        chain_id INTEGER NOT NULL DEFAULT 11155111,
        contract_address VARCHAR(42) NOT NULL,
        status VARCHAR(20) NOT NULL DEFAULT 'LOCKED',
        commitment_hash VARCHAR(66) NOT NULL,
        created_at TIMESTAMPTZ DEFAULT now(),
        unlocked_at TIMESTAMPTZ
    );
    CREATE INDEX IF NOT EXISTS ix_escrow_commitments_commitment_id ON escrow_commitments(commitment_id);
    CREATE INDEX IF NOT EXISTS ix_escrow_commitments_wallet_address ON escrow_commitments(wallet_address);
    CREATE INDEX IF NOT EXISTS ix_escrow_commitments_commitment_hash ON escrow_commitments(commitment_hash);
    """
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        if "escrow_commitments" in tables:
            logger.info("✅ Escrow migration already applied (table exists).")
            return True
        if "commitments" not in tables:
            logger.warning("⚠️  Commitments table does not exist. Skipping escrow migration.")
            return False
        logger.info("🔄 Running escrow migration...")
        with engine.begin() as conn:
            for stmt in [s.strip() for s in migration_sql.strip().split(";") if s.strip()]:
                if stmt:
                    conn.execute(text(stmt))
        logger.info("✅ Escrow migration completed successfully.")
        return True
    except Exception as e:
        logger.error(f"❌ Escrow migration failed: {e}")
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
