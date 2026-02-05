from __future__ import annotations

import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from eth_hash.auto import keccak
from sqlalchemy.orm import Session

from app.config import settings
from app.models.commitment import Commitment
from app.models.escrow import EscrowCommitment


def _commitment_hash(commitment_id: int, user_id: str, target_amount: float, maturity_ts: int) -> str:
    """Deterministic keccak256. Preimage: commitment_id|user_id|target_amount|maturity_ts."""
    preimage = f"{commitment_id}|{user_id}|{target_amount}|{maturity_ts}"
    h = keccak(preimage.encode("utf-8"))
    return "0x" + h.hex()


def _maturity_timestamp(commitment: Commitment) -> int:
    """Unix timestamp for end of commitment period (created_at + goal_timeframe_weeks)."""
    base = commitment.created_at or datetime.now(timezone.utc)
    end = base + timedelta(weeks=commitment.goal_timeframe_weeks)
    return int(end.timestamp())


def generate_escrow_metadata(db: Session, commitment_id: int) -> Dict[str, Any]:
    """
    Load commitment, compute maturity and hash, return init payload for frontend.
    """
    commitment = db.query(Commitment).filter(Commitment.id == commitment_id).first()
    if not commitment:
        raise ValueError(f"Commitment {commitment_id} not found")

    maturity_ts = _maturity_timestamp(commitment)
    h = _commitment_hash(
        commitment.id,
        commitment.user_id,
        float(commitment.goal_amount),
        maturity_ts,
    )
    contract = (
        settings.escrow_contract_address
        or os.getenv("ESCROW_CONTRACT_ADDRESS")
        or "0x0000000000000000000000000000000000000000"
    )
    chain_id = settings.chain_id

    return {
        "commitment_id": h,
        "unlock_timestamp": maturity_ts,
        "contract_address": contract,
        "chain_id": chain_id,
    }


def confirm_deposit(
    db: Session,
    commitment_id: int,
    wallet_address: str,
    tx_hash: str,
    amount: int,
) -> EscrowCommitment:
    """Create or update escrow record after on-chain createCommitment tx."""
    commitment = db.query(Commitment).filter(Commitment.id == commitment_id).first()
    if not commitment:
        raise ValueError(f"Commitment {commitment_id} not found")

    maturity_ts = _maturity_timestamp(commitment)
    h = _commitment_hash(
        commitment.id,
        commitment.user_id,
        float(commitment.goal_amount),
        maturity_ts,
    )
    contract = (
        settings.escrow_contract_address
        or os.getenv("ESCROW_CONTRACT_ADDRESS")
        or "0x0000000000000000000000000000000000000000"
    )

    existing = (
        db.query(EscrowCommitment).filter(EscrowCommitment.commitment_id == commitment_id).first()
    )
    if existing:
        existing.wallet_address = wallet_address
        existing.tx_hash = tx_hash
        existing.amount = amount
        existing.status = "LOCKED"
        db.commit()
        db.refresh(existing)
        return existing

    row = EscrowCommitment(
        commitment_id=commitment_id,
        wallet_address=wallet_address,
        tx_hash=tx_hash,
        amount=amount,
        unlock_timestamp=maturity_ts,
        chain_id=settings.chain_id,
        contract_address=contract,
        status="LOCKED",
        commitment_hash=h,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_escrow_status(db: Session, commitment_id: int) -> Optional[Dict[str, Any]]:
    """Return escrow record for commitment, or None. Updates LOCKED -> UNLOCKED if past maturity."""
    row = (
        db.query(EscrowCommitment).filter(EscrowCommitment.commitment_id == commitment_id).first()
    )
    if not row:
        return None
    if row.status == "LOCKED" and int(time.time()) >= row.unlock_timestamp:
        row.status = "UNLOCKED"
        row.unlocked_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(row)
    return {
        "id": row.id,
        "commitment_id": row.commitment_id,
        "wallet_address": row.wallet_address,
        "tx_hash": row.tx_hash,
        "amount": row.amount,
        "unlock_timestamp": row.unlock_timestamp,
        "chain_id": row.chain_id,
        "contract_address": row.contract_address,
        "status": row.status,
        "commitment_hash": row.commitment_hash,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "unlocked_at": row.unlocked_at.isoformat() if row.unlocked_at else None,
    }


def mark_withdrawn(db: Session, commitment_id: int) -> EscrowCommitment:
    """Set status to WITHDRAWN and unlocked_at to now."""
    row = (
        db.query(EscrowCommitment).filter(EscrowCommitment.commitment_id == commitment_id).first()
    )
    if not row:
        raise ValueError(f"Escrow for commitment {commitment_id} not found")
    row.status = "WITHDRAWN"
    row.unlocked_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)
    return row


def update_unlocked_status(db: Session, commitment_id: int) -> None:
    """
    Set status to UNLOCKED when block.timestamp >= unlock_timestamp.
    Called by backend when serving status (optional), or by a job.
    """
    row = (
        db.query(EscrowCommitment).filter(EscrowCommitment.commitment_id == commitment_id).first()
    )
    if not row or row.status != "LOCKED":
        return
    if int(time.time()) >= row.unlock_timestamp:
        row.status = "UNLOCKED"
        row.unlocked_at = datetime.now(timezone.utc)
        db.commit()
