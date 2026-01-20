from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Spending(Base):
    __tablename__ = "spending"

    id = Column(Integer, primary_key=True, index=True)
    commitment_id = Column(Integer, ForeignKey("commitments.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=True)  # Optional spending category
    week_number = Column(Integer, nullable=False)  # Week number since commitment start
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    commitment = relationship("Commitment", back_populates="spending_logs")
