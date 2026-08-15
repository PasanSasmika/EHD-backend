import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.ticket import TicketCreate, TicketUpdate
from app.models.ticket_message import TicketMessage
from app.schemas.message import MessageCreate

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"],
)

@router.post("/")
def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = Ticket(
        ticket_number=f"TKT-{uuid.uuid4().hex[:8].upper()}",
        title=ticket_data.title,
        description=ticket_data.description,
        department=ticket_data.department,
        category=ticket_data.category,
        priority=ticket_data.priority,
        created_by=current_user.id,
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket

@router.get("/")
def get_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "ADMIN":
        return db.query(Ticket).all()

    if current_user.role == "TECHNICIAN":
        return db.query(Ticket).filter(
            Ticket.assigned_to == current_user.id
        ).all()

    return db.query(Ticket).filter(
        Ticket.created_by == current_user.id
    ).all()

@router.get("/{ticket_id}")
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return ticket

@router.put("/{ticket_id}")
def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    if current_user.role not in ["ADMIN", "TECHNICIAN"]:
        raise HTTPException(
            status_code=403,
            detail="Permission denied",
        )

    data = ticket_data.model_dump(exclude_unset=True)

    for key, value in data.items():
        setattr(ticket, key, value)

    db.commit()
    db.refresh(ticket)

    return ticket
@router.put("/{ticket_id}/assign")
def assign_ticket(
    ticket_id: int,
    data: TicketAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Only admin can assign tickets",
        )

    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    technician = db.query(User).filter(
        User.id == data.technician_id,
        User.role == "TECHNICIAN",
    ).first()

    if not technician:
        raise HTTPException(
            status_code=404,
            detail="Technician not found",
        )

    ticket.assigned_to = technician.id
    ticket.status = "IN_PROGRESS"

    db.commit()
    db.refresh(ticket)

    return ticket


@router.post("/{ticket_id}/messages")
def send_message(
    ticket_id: int,
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    message = TicketMessage(
        ticket_id=ticket.id,
        sender_id=current_user.id,
        message=data.message,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


@router.get("/{ticket_id}/messages")
def get_messages(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(TicketMessage).filter(
        TicketMessage.ticket_id == ticket_id
    ).order_by(TicketMessage.created_at).all()
