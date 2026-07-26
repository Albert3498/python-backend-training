from fastapi import APIRouter,Depends
from datetime import timedelta,datetime
from Authentication import get_current_user

sla_router=APIRouter()

SLA_WINDOWS={
    ("Document","high"):(24,72),
    ("Document","medium"):(72,168),
    ("Document","low"):(168,336),
    ("Task","high"):(48,120),
    ("Task","medium"):(120,240),
    ("Task","low"):(240,480),
    ("Contract","high"):(72,168),
    ("Contract","medium"):(168,336),
    ("Contract","low"):(336,720)
}
AT_RISK_THRESHOLD=0.75
def compute_sla_status(ticket,now):
    created_at=datetime.fromisoformat(ticket["created_at"])
    deadline=datetime.fromisoformat(ticket["deadline"])
    resolved_at_str=ticket.get("resolved_at")
    if resolved_at_str is not None :
        resolved_at=datetime.fromisoformat(resolved_at_str)
        if resolved_at <= deadline:
            return "met"
        else:
            return "missed"
    if now > deadline:
        return "breached"
    elapsed_fraction=(now-created_at)/(deadline-created_at)
    if elapsed_fraction >= AT_RISK_THRESHOLD:
        return "at_risk"
    return "on_track"
def deadline_range(ticket_type,priority,created_at):
    min_hours,max_hours=SLA_WINDOWS[(ticket_type,priority)]
    min_deadline=created_at+timedelta(hours=min_hours)
    max_deadline=created_at+timedelta(hours=max_hours)
    return min_deadline,max_deadline

@sla_router.get("/sla/report")
def sla_report(current_user=Depends(get_current_user)):
    from Ticket_creation import tickets
    visible_tickets={k:{**v,"sla_status":compute_sla_status(v,datetime.now())} for k,v in tickets.items() if current_user["sub"]==v["to"] or current_user["sub"]==v["user"]}
    report={k:v for k,v in visible_tickets.items() if v["sla_status"] in {"at_risk","breached","missed"}}
    return report
