from pydantic import BaseModel
class TicketCreate(BaseModel):
    title: str
    description: str
    department: str
    category: str
    priority: str = "MEDIUM"


class TicketUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: str | None = None
    status: str | None = None


class TicketAssign(BaseModel):
    technician_id: int
