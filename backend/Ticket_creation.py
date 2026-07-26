
from fastapi import APIRouter,HTTPException,Depends
from pydantic import BaseModel
from enum import Enum
import json
from Authentication import get_current_user,get_db
import sqlite3
from datetime import datetime
from sla import deadline_range,compute_sla_status
#be able to get the data from the json file
def load_counter():
    try:
        with open("counter.json") as f:
            data =json.load(f)
            return data.get("counter",{"Contract":0,"Task":0,"Document":0}),data.get("tickets",{})
    except:
        return {"Contract":0,"Task":0,"Document":0}, {}
#save any modifications in the json file
def save_data(tickets_dict,counter_val):
    data={
        "counter":counter_val,
        "tickets":tickets_dict
    }
    with open("counter.json","w") as f:
        json.dump(data,f)
ticket_counter,tickets=load_counter()
ticket_router=APIRouter()
#Only 3 types of priority available
class EnumPriority(str, Enum):
    low="low"
    medium="medium"
    high="high"
#!TODO:add more types of tickets!
class EnumType(str, Enum):
    contract="Contract"
    task="Task"
    document="Document"
class SortBy(str,Enum):
    priority="priority"
    type="type"
class UserInputs(BaseModel):
    title :str #Ex:Apartment Lease
    to:str
    description:str #Ex:Remember to pay it in a few days
    priority :EnumPriority #low,medium,high
    type:EnumType #Contract,Task,Document
    deadline:datetime
class EnumStatus(str,Enum):
    open="open"
    in_progress="in_progress"
    issued="issued"
    resolved="resolved"
    closed="closed"
ALLOWED_STATUSES={
    "Contract":{
        "open":1,
        "in_progress":2,
        "resolved":3,
        "closed":4
    }, 
    "Task":{
        "open":1,
        "in_progress":2,
        "resolved":3,
        "closed":4
    },
    "Document":{
        "issued":1,
        "resolved":2,
        "closed":3
    }
}
class UpdateTickets(BaseModel):
    description: str | None = None
    priority:EnumPriority | None = None
    status:EnumStatus | None = None
priority_order={
    "low":1,
    "medium":2,
    "high":3
}
#post a new ticket(save it onto json file)
@ticket_router.post("/tickets/")
def create_ticket(user_data:UserInputs,current_user=Depends(get_current_user),db:sqlite3.Connection=Depends(get_db)):
    if current_user["role"]!="staff":
        raise HTTPException(status_code=403,detail="You aren't allowed to create tickets")
    cur=db.cursor()
    cur.execute("SELECT role FROM userdata WHERE username=?",(user_data.to,))
    row=cur.fetchone()
    if row is None:
        raise HTTPException(status_code=400,detail="Recipient doesn't exist")
    if row[0]!="civilian":
        raise HTTPException(status_code=400,detail="Can't issue tickets to staff")
    created_at=datetime.now()
    min_dt,max_dt=deadline_range(user_data.type.value,user_data.priority.value,created_at)
    if user_data.deadline < min_dt or user_data.deadline > max_dt:
        raise HTTPException(status_code=400,detail=f"Deadline must be between {min_dt} and {max_dt}")
    default_status=min(ALLOWED_STATUSES[user_data.type.value],key=lambda x:ALLOWED_STATUSES[user_data.type.value][x])
    prefix=user_data.type.value.upper()[:4]
    ticket_counter[user_data.type.value]+=1
    unique_ticket_id=f"{prefix}-{ticket_counter[user_data.type.value]}"
    ticket_record=user_data.model_dump()
    ticket_record["user"]=current_user["sub"]
    ticket_record["status"]=default_status
    ticket_record["created_at"]=created_at.isoformat()
    ticket_record["deadline"]=user_data.deadline.isoformat()
    tickets[unique_ticket_id]=ticket_record
    save_data(tickets,ticket_counter)
    return {
        "ticket id":unique_ticket_id,
        "status":"Created Successfully",
        "data":user_data
}
#list all of the tickets(can also be in and order)
@ticket_router.get("/tickets/")
def list_tickets(sort_by: SortBy | None = None,order: str="asc",current_user=Depends(get_current_user)):
    
    visible_tickets={k:{**v,"sla_status":compute_sla_status(v,datetime.now())} for k,v in tickets.items() if current_user["sub"]==v["to"] or current_user["sub"]==v["user"]}
    if sort_by is None:
        return visible_tickets
    elif sort_by==SortBy.type:
        return dict(sorted(visible_tickets.items(),key=lambda x:x[1].get("type"),reverse=(order=="desc")))
    elif sort_by==SortBy.priority:
        return dict(sorted(visible_tickets.items(),key=lambda x:priority_order[x[1].get("priority")],reverse=(order=="desc")))
#search for a ticket
@ticket_router.get("/tickets/{ticket_id}")
def get_ticket(ticket_id:str,current_user=Depends(get_current_user)):
    if ticket_id not in tickets:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if not (current_user["sub"]==tickets[ticket_id]["user"] or tickets[ticket_id]["to"]==current_user["sub"]):
        raise HTTPException(status_code=404,detail="Ticket not found")
    ticket_copy=tickets[ticket_id].copy()
    ticket_copy["sla_status"]=compute_sla_status(tickets[ticket_id],datetime.now())
    return{"tickets":ticket_copy}
@ticket_router.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id:str,current_user=Depends(get_current_user)):
    if ticket_id not in tickets:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if current_user["sub"]==tickets[ticket_id]["user"]:
        deleted_ticket=tickets.pop(ticket_id)
        save_data(tickets,ticket_counter)
        return({"tickets":deleted_ticket})
    else:
        raise HTTPException(status_code=403,detail="Can't delete this")
@ticket_router.patch("/tickets/{ticket_id}")
def edit_ticket(ticket_id:str,edit_data:UpdateTickets,current_user=Depends(get_current_user)):
    if ticket_id not in tickets:
        raise HTTPException(status_code=404,detail="Ticket not found")
    if current_user["sub"]==tickets[ticket_id]["user"]:
        if edit_data.description is not None:
            tickets[ticket_id]["description"]=edit_data.description
        if edit_data.priority is not None:
            tickets[ticket_id]["priority"]=edit_data.priority
        if edit_data.status is not None:
            ticket_type=tickets[ticket_id]["type"]
            if edit_data.status not in ALLOWED_STATUSES[ticket_type]:
                raise HTTPException(status_code=400,detail="This is not a valid status")
            current_status=ALLOWED_STATUSES[ticket_type][tickets[ticket_id]["status"]]
            edited_status=ALLOWED_STATUSES[ticket_type][edit_data.status]
            if current_status != edited_status-1:
                raise HTTPException(status_code=400,detail="Enter only the next status available")
            tickets[ticket_id]["status"]=edit_data.status
            if edit_data.status == EnumStatus.resolved:
                tickets[ticket_id]["resolved_at"] = datetime.now().isoformat()
        save_data(tickets,ticket_counter)
        return({"tickets":tickets[ticket_id]})
    else:
        raise HTTPException(status_code=403,detail="Can't edit this")
    
