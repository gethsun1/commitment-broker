from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class EscrowCommitment(Base):
    __tablename__ = "escrow_commitments"

    id = Column(Integer, primary_key=True, index=True)
    commitment_id = Column(Integer, ForeignKey("commitments.id"), nullable=False, index=True, unique=True)
    wallet_address = Column(String(42), nullable=False, index=True)
    tx_hash = Column(String(66), nullable=True)
    amount = Column(BigInteger, nullable=False)  # wei
    unlock_timestamp = Column(BigInteger, nullable=False)
    chain_id = Column(Integer, nullable=False, default=11155111)
    contract_address = Column(String(42), nullable=False)
    status = Column(String(20), nullable=False, default="LOCKED")  # LOCKED | UNLOCKED | WITHDRAWN
    commitment_hash = Column(String(66), nullable=False, index=True)  # bytes32 as 0x-prefixed hex
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    unlocked_at = Column(DateTime(timezone=True), nullable=True)

    commitment = relationship("Commitment", backref="escrow")
