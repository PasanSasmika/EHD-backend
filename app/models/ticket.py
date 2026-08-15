from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func

from app.database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)

    ticket_number = Column(
        String(50),
        unique=True,
        nullable=False,
    )

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    department = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)

    priority = Column(
        String(50),
        default="MEDIUM",
    )

    status = Column(
        String(50),
        default="OPEN",
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
    )