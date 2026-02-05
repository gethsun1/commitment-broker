from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.api.schemas import (
    GoalInput,
    CommitmentResponse,
    SpendingInput,
    SpendingResponse,
    DriftResponse,
    InterventionResponse,
    EvaluationResponse,
    EscrowInitRequest,
    EscrowInitResponse,
    EscrowConfirmRequest,
    EscrowStatusResponse,
)
from app.services.commitment_service import CommitmentService
from app.services.tracking_service import TrackingService
from app.services.escrow_service import (
    generate_escrow_metadata,
    confirm_deposit,
    get_escrow_status,
    mark_withdrawn,
)

router = APIRouter()

# Initialize services lazily to avoid Opik initialization errors at import time
# Services will be created on first use via dependency injection or lazy initialization
_commitment_service = None
_tracking_service = None

def get_commitment_service():
    """Get or create CommitmentService instance (lazy initialization)."""
    global _commitment_service
    if _commitment_service is None:
        _commitment_service = CommitmentService()
    return _commitment_service

def get_tracking_service():
    """Get or create TrackingService instance (lazy initialization)."""
    global _tracking_service
    if _tracking_service is None:
        _tracking_service = TrackingService()
    return _tracking_service

# For backward compatibility, create instances but catch any initialization errors
try:
    commitment_service = CommitmentService()
    tracking_service = TrackingService()
except Exception as e:
    print(f"⚠️  Service initialization warning: {e}")
    print("   Services will be initialized on first use.")
    # Set to None - will be created lazily
    commitment_service = None
    tracking_service = None


@router.post("/goals", response_model=CommitmentResponse)
async def create_goal(goal_input: GoalInput, db: Session = Depends(get_db)):
    """Create a new goal and generate commitment plan."""
    user_input = {
        "user_id": goal_input.user_id,
        "goal_description": goal_input.goal_description,
        "target_amount": goal_input.target_amount,
        "timeframe": goal_input.timeframe,
        "income_frequency": goal_input.income_frequency,
        "risk_moments": goal_input.risk_moments or []
    }
    
    service = commitment_service if commitment_service else get_commitment_service()
    commitment = await service.create_commitment(db, user_input)
    return commitment


@router.get("/commitments", response_model=List[CommitmentResponse])
async def list_commitments(db: Session = Depends(get_db)):
    """Get all commitments."""
    from app.models.commitment import Commitment
    
    commitments = db.query(Commitment).order_by(Commitment.created_at.desc()).all()
    return commitments


@router.get("/commitments/{commitment_id}", response_model=CommitmentResponse)
async def get_commitment(commitment_id: int, db: Session = Depends(get_db)):
    """Get commitment details by ID."""
    from app.models.commitment import Commitment
    
    commitment = db.query(Commitment).filter(Commitment.id == commitment_id).first()
    if not commitment:
        raise HTTPException(status_code=404, detail="Commitment not found")
    
    return commitment


@router.post("/spending", response_model=SpendingResponse)
async def add_spending(spending_input: SpendingInput, db: Session = Depends(get_db)):
    """Add spending entry and trigger drift detection if needed."""
    tracking = tracking_service if tracking_service else get_tracking_service()
    commitment = commitment_service if commitment_service else get_commitment_service()
    
    spending = await tracking.add_spending(
        db,
        spending_input.commitment_id,
        spending_input.amount,
        spending_input.category,
        spending_input.week_number,
        spending_input.description
    )
    
    # Trigger drift detection
    drift_result = await commitment.track_spending_and_detect_drift(
        db,
        spending_input.commitment_id
    )
    
    # If drift detected, trigger intervention
    if drift_result.get("should_intervene"):
        await tracking.trigger_intervention(
            db,
            spending_input.commitment_id,
            drift_result["drift_analysis"]
        )
    
    return spending


@router.get("/commitments/{commitment_id}/drift", response_model=DriftResponse)
async def check_drift(commitment_id: int, db: Session = Depends(get_db)):
    """Check for drift in spending behavior."""
    service = commitment_service if commitment_service else get_commitment_service()
    drift_result = await service.track_spending_and_detect_drift(
        db,
        commitment_id
    )
    
    drift_analysis = drift_result.get("drift_analysis", {})
    return DriftResponse(
        has_drift=drift_analysis.get("has_drift", False),
        drift_type=drift_analysis.get("drift_type"),
        severity=drift_analysis.get("severity"),
        description=drift_analysis.get("description"),
        deviation_amount=drift_analysis.get("deviation_amount")
    )


@router.get("/commitments/{commitment_id}/interventions", response_model=List[InterventionResponse])
async def get_interventions(commitment_id: int, db: Session = Depends(get_db)):
    """Get intervention history for a commitment."""
    from app.models.intervention import Intervention
    
    interventions = db.query(Intervention).filter(
        Intervention.commitment_id == commitment_id
    ).order_by(Intervention.triggered_at.desc()).all()
    
    return interventions


@router.get("/commitments/{commitment_id}/evaluation", response_model=EvaluationResponse)
async def get_evaluation(commitment_id: int, db: Session = Depends(get_db)):
    """Get latest evaluation metrics for a commitment."""
    from app.models.evaluation import Evaluation
    from app.models.commitment import Commitment
    
    # Verify commitment exists
    commitment = db.query(Commitment).filter(Commitment.id == commitment_id).first()
    if not commitment:
        raise HTTPException(status_code=404, detail="Commitment not found")
    
    # Get the most recent evaluation
    evaluation = db.query(Evaluation).filter(
        Evaluation.commitment_id == commitment_id
    ).order_by(Evaluation.timestamp.desc()).first()
    
    if not evaluation:
        raise HTTPException(
            status_code=404, 
            detail="No evaluation found for this commitment. Use POST /api/commitments/{id}/evaluate to run evaluation."
        )
    
    return evaluation


@router.post("/commitments/{commitment_id}/evaluate", response_model=EvaluationResponse)
async def trigger_evaluation(commitment_id: int, db: Session = Depends(get_db)):
    """Manually trigger evaluation agent run to generate new AI-evaluated metrics."""
    try:
        tracking = tracking_service if tracking_service else get_tracking_service()
        evaluation = await tracking.evaluate_commitment(db, commitment_id)
        return evaluation
    except Exception as e:
        # Log the error for debugging
        import traceback
        print(f"⚠️  Error in trigger_evaluation: {e}")
        print(traceback.format_exc())
        # Re-raise as HTTPException to ensure proper error response with CORS headers
        raise HTTPException(
            status_code=500,
            detail=f"Failed to run evaluation: {str(e)}"
        )


@router.post("/admin/migrate", tags=["admin"])
async def run_migration(db: Session = Depends(get_db)):
    """
    Manually trigger database migration.
    Safe to run multiple times (idempotent).
    This endpoint can be called from Render without shell access.
    """
    from app.database_migrations import run_evaluation_fields_migration, run_escrow_migration, check_migration_status
    
    # Check current status
    status = check_migration_status()
    
    if status.get("migrated"):
        run_escrow_migration()
        return {
            "status": "already_migrated",
            "message": "Migration already applied. No action needed.",
            "details": status
        }
    
    # Run migrations
    success = run_evaluation_fields_migration()
    if success:
        run_escrow_migration()
        return {
            "status": "success",
            "message": "Migration completed successfully",
            "details": check_migration_status()
        }
    else:
        raise HTTPException(
            status_code=500,
            detail="Migration failed. Check server logs for details."
        )


@router.get("/admin/migration-status", tags=["admin"])
async def get_migration_status():
    """
    Check the status of database migrations.
    """
    from app.database_migrations import check_migration_status
    return check_migration_status()


@router.get("/commitments/{commitment_id}/spending", response_model=List[SpendingResponse])
async def get_spending(commitment_id: int, db: Session = Depends(get_db)):
    """Get spending history for a commitment."""
    from app.models.spending import Spending
    
    spending_logs = db.query(Spending).filter(
        Spending.commitment_id == commitment_id
    ).order_by(Spending.week_number, Spending.created_at).all()
    
    return spending_logs


@router.patch("/interventions/{intervention_id}/outcome")
async def update_intervention_outcome(
    intervention_id: int,
    outcome: str,
    db: Session = Depends(get_db)
):
    """Update intervention outcome (success, ignored, failed, false_positive)."""
    from app.models.intervention import Intervention
    
    intervention = db.query(Intervention).filter(Intervention.id == intervention_id).first()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")
    
    intervention.outcome = outcome
    db.commit()
    db.refresh(intervention)
    
    # Log to Opik
    from app.observability.opik_client import OpikClient
    opik = OpikClient()
    await opik.log_intervention_outcome(
        intervention_id=str(intervention.id),
        intervention_type=intervention.type.value,
        outcome=outcome,
        metrics={
            "drift_type": intervention.drift_type
        }
    )
    
    return {"status": "updated", "intervention_id": intervention_id, "outcome": outcome}


# Escrow (on-chain commitment, optional)


@router.post("/escrow/init", response_model=EscrowInitResponse)
async def escrow_init(body: EscrowInitRequest, db: Session = Depends(get_db)):
    """Generate escrow metadata for frontend (commitment hash, unlock ts, contract, chain)."""
    try:
        meta = generate_escrow_metadata(db, body.commitment_id)
        return EscrowInitResponse(
            commitment_id=meta["commitment_id"],
            unlock_timestamp=meta["unlock_timestamp"],
            contract_address=meta["contract_address"],
            chain_id=meta["chain_id"],
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/escrow/confirm")
async def escrow_confirm(body: EscrowConfirmRequest, db: Session = Depends(get_db)):
    """Save on-chain tx after wallet interaction (createCommitment)."""
    try:
        row = confirm_deposit(
            db,
            body.commitment_id,
            body.wallet_address,
            body.tx_hash,
            body.amount,
        )
        from app.observability.opik_client import OpikClient
        opik = OpikClient()
        if opik.api_key:
            try:
                await opik.log_experiment(
                    experiment_name="escrow_creation",
                    prompt_version="v1",
                    agent_type="escrow",
                    metrics={"commitment_id": body.commitment_id, "amount_wei": body.amount},
                    metadata={"wallet": body.wallet_address[:10] + "…"},
                )
            except Exception:
                pass
        return {
            "status": "confirmed",
            "escrow_id": row.id,
            "commitment_id": body.commitment_id,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/escrow/{commitment_id}", response_model=EscrowStatusResponse)
async def escrow_get(commitment_id: int, db: Session = Depends(get_db)):
    """Fetch escrow status for frontend and evaluation agent."""
    status = get_escrow_status(db, commitment_id)
    if not status:
        raise HTTPException(status_code=404, detail="Escrow not found for this commitment")
    return EscrowStatusResponse(**status)


@router.patch("/escrow/{commitment_id}/withdrawn")
async def escrow_mark_withdrawn(commitment_id: int, db: Session = Depends(get_db)):
    """Mark escrow as withdrawn after user calls contract withdraw."""
    try:
        mark_withdrawn(db, commitment_id)
        return {"status": "withdrawn", "commitment_id": commitment_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
