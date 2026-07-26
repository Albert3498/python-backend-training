
import sqlite3
from fastapi import APIRouter,HTTPException,Depends
from Ticket_creation import EnumPriority,tickets,save_data,ticket_counter
from pydantic import BaseModel
from enum import Enum
from Authentication import get_current_user
import json
def load_requests():
    try:
        with open("requests.json") as f:
            data=json.load(f)
            return data.get("req_counter",0),data.get("requests",{})
    except:
        return 0,{}
def save_requests(requests_dict,reqCounter):
    data={
        "req_counter":reqCounter,
        "requests":requests_dict
    }
    with open("requests.json","w") as f:
        json.dump(data,f)
req_counter,requests=load_requests()
workflow_router=APIRouter()
class RequestStatus(str,Enum):
    pending="pending"
    approved="approved"
    rejected="rejected"
class PriorityChangeRequest(BaseModel):
    ticket_id:str
    priority:EnumPriority
@workflow_router.post("/request/")
def create_request(request_data:PriorityChangeRequest,current_user=Depends(get_current_user)):
    if request_data.ticket_id not in tickets:
        raise HTTPException(status_code=404,detail="ticket not found")
    if current_user["sub"]!=tickets[request_data.ticket_id]["to"]:
        raise HTTPException(status_code=403,detail="You are not authorized to send a request")
    pending_count=sum(
        1 for r in requests.values()
        if r["ticket_id"]==request_data.ticket_id and r["status"]==RequestStatus.pending
    )
    if pending_count>=3:
        raise HTTPException(status_code=400,detail="Too many pending requests for this ticket")
    request_record=request_data.model_dump()
    request_record["user"]=current_user["sub"]
    request_record["status"]=RequestStatus.pending
    prefix="REQ"
    global req_counter
    req_counter+=1
    unique_request_id=f"{prefix}-{req_counter}"
    requests[unique_request_id]=request_record
    save_requests(requests,req_counter)
    return{
        "request id":unique_request_id,
        "status":"Request Sent",
        "data":request_data
    }
@workflow_router.post("/request/{request_id}/approve")
def accept_request(request_id:str,current_user=Depends(get_current_user)):
    if request_id not in requests:
        raise HTTPException(status_code=404,detail="Request not found")
    ticket_id=requests[request_id]["ticket_id"]
    if current_user["sub"]!=tickets[ticket_id]["user"]:
        raise HTTPException(status_code=403,detail="Not authorized")
    if requests[request_id]["status"]!=RequestStatus.pending:
        raise HTTPException(status_code=400,detail="Already decided")
    tickets[ticket_id]["priority"]=requests[request_id]["priority"]
    save_data(tickets,ticket_counter)
    requests[request_id]["status"]=RequestStatus.approved
    save_requests(requests,req_counter)
    return{
        "request_id":request_id,
        "ticket_id":ticket_id,
        "status":"Request approved"
    }
@workflow_router.post("/request/{request_id}/reject")
def reject_request(request_id:str,current_user=Depends(get_current_user)):
    if request_id not in requests:
        raise HTTPException(status_code=404,detail="Request not found")
    ticket_id=requests[request_id]["ticket_id"]
    if current_user["sub"]!=tickets[ticket_id]["user"]:
        raise HTTPException(status_code=403,detail="Not authorized")
    if requests[request_id]["status"]!=RequestStatus.pending:
        raise HTTPException(status_code=400,detail="Already decided")
    requests[request_id]["status"]=RequestStatus.rejected
    save_requests(requests,req_counter)
    return{
        "request":request_id,
        "ticket_id":ticket_id,
        "status":"Request rejected"
    }
@workflow_router.get("/request/")
def list_requests(current_user=Depends(get_current_user)):
    visible_requests={
        k:v for k,v in requests.items()
        if current_user["sub"]==v["user"]
        or current_user["sub"]==tickets[v["ticket_id"]]["user"]
    }
    return visible_requests
@workflow_router.get("/request/{request_id}")
def get_request(request_id:str,current_user=Depends(get_current_user)):
    if request_id not in requests:
        raise HTTPException(status_code=404,detail="Request not found")
    ticket_id=requests[request_id]["ticket_id"]
    if current_user["sub"]!=tickets[ticket_id]["user"] and  current_user["sub"]!=requests[request_id]["user"]:
        raise HTTPException(status_code=404,detail="Request not found")
    return({"requests":requests.get(request_id)})





