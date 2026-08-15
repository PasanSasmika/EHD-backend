from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.tickets import router as ticket_router


app = FastAPI(
    title="Enterprise Helpdesk API",
)

app.include_router(auth_router)
app.include_router(ticket_router)


@app.get("/")
def home():
    return {
        "message": "Enterprise Helpdesk API is running"
    }