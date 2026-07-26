
from fastapi import FastAPI
from Authentication import auth_router
from workflow import workflow_router
from Ticket_creation import ticket_router
from sla import sla_router
app=FastAPI()
app.include_router(auth_router)
app.include_router(workflow_router)
app.include_router(ticket_router)
app.include_router(sla_router)