"""
Demo data seeder for Commitment Broker.
Creates a demo user with a goal, simulates spending pattern with one failure,
triggers intervention, and shows improvement.
"""
import asyncio
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine, Base
from app.models.commitment import Commitment
from app.models.intervention import Intervention
from app.services.tracking_service import TrackingService
from app.services.commitment_service import CommitmentService


def create_demo_commitment(db: Session):
    """Create a demo commitment: $5000 savings in 6 months."""
    commitment = Commitment(
        goal_id="demo_goal_001",
        user_id="demo_user",
        weekly_target=208.33,  # $5000 / 24 weeks ≈ $208.33/week
        spending_ceiling=150.0,  # Example spending ceiling
        goal_amount=5000.0,
        goal_timeframe_weeks=24,
        income_frequency="monthly",
        risk_moments='["End of month", "Payday"]',
        version=1
    )
    
    db.add(commitment)
    db.commit()
    db.refresh(commitment)
    
    return commitment


async def simulate_spending_pattern(db: Session, commitment_id: int):
    """Simulate spending pattern: Weeks 1-2 compliant, Week 3 overspends, Week 4 improves."""
    tracking_service = TrackingService()
    commitment_service = CommitmentService()
    
    # Week 1: Compliant ($120 spent, ceiling is $150)
    await tracking_service.add_spending(
        db, commitment_id, 120.0, "Groceries", 1, "Week 1 groceries"
    )
    
    # Week 2: Compliant ($130 spent)
    await tracking_service.add_spending(
        db, commitment_id, 130.0, "Utilities", 2, "Week 2 utilities"
    )
    
    # Week 3: Failure - Overspends by $50 ($200 spent, ceiling is $150)
    await tracking_service.add_spending(
        db, commitment_id, 200.0, "Entertainment", 3, "Week 3 - overspent"
    )
    
    # Trigger drift detection and intervention for Week 3
    drift_result = await commitment_service.track_spending_and_detect_drift(
        db, commitment_id
    )
    
    if drift_result.get("should_intervene"):
        await tracking_service.trigger_intervention(
            db, commitment_id, drift_result["drift_analysis"]
        )
    
    # Week 4: Improvement - Back on track ($140 spent)
    await tracking_service.add_spending(
        db, commitment_id, 140.0, "Mixed", 4, "Week 4 - back on track"
    )
    
    # Update intervention outcome to success
    intervention = db.query(Intervention).filter(
        Intervention.commitment_id == commitment_id
    ).order_by(Intervention.triggered_at.desc()).first()
    
    if intervention:
        intervention.outcome = "success"
        db.commit()
    
    # Create evaluation
    evaluation = await tracking_service.evaluate_commitment(db, commitment_id)
    
    return evaluation


def main():
    """Main seeding function."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        print("Creating demo commitment...")
        commitment = create_demo_commitment(db)
        print(f"✓ Created commitment ID: {commitment.id}")
        
        print("Simulating spending pattern...")
        evaluation = asyncio.run(simulate_spending_pattern(db, commitment.id))
        print(f"✓ Completed simulation")
        print(f"✓ Adherence Rate: {evaluation.adherence_rate:.1f}%")
        print(f"✓ Weeks Tracked: {evaluation.weeks_tracked}")
        print(f"✓ Weeks Compliant: {evaluation.weeks_compliant}")
        
        print("\nDemo data seeded successfully!")
        print(f"\nTo view the demo:")
        print(f"1. Start the backend: cd backend && uvicorn app.main:app --reload")
        print(f"2. Start the frontend: cd frontend && npm run dev")
        print(f"3. Navigate to: http://localhost:3000/commitments/{commitment.id}")
        
    except Exception as e:
        print(f"Error seeding demo data: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
