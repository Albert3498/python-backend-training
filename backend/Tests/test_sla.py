from datetime import datetime,timedelta
from sla import deadline_range,compute_sla_status

def test_deadline_range_document_high():
    created_at=datetime(2026,1,1,12,0,0)
    result=deadline_range("Document","high",created_at)
    assert result==(created_at + timedelta(hours=24),created_at+timedelta(hours=72))
def test_deadline_range_document_medium():
    created_at=datetime(2026,1,1,12,0,0)
    result=deadline_range("Document","medium",created_at)
    assert result==(created_at + timedelta(hours=72),created_at+timedelta(hours=168))
def test_deadline_range_document_low():
    created_at=datetime(2026,1,1,12,0,0)
    result=deadline_range("Document","low",created_at)
    assert result==(created_at + timedelta(hours=168),created_at+timedelta(hours=336))

def test_deadline_range_task_high():
    created_at=datetime(2026,1,1,12,0,0)
    result=deadline_range("Task","high",created_at)
    assert result==(created_at + timedelta(hours=48),created_at+timedelta(hours=120))
def test_deadline_range_task_medium():
    created_at=datetime(2026,1,1,12,0,0)
    result=deadline_range("Task","medium",created_at)
    assert result==(created_at + timedelta(hours=120),created_at+timedelta(hours=240))
def test_deadline_range_task_low():
    created_at=datetime(2026,1,1,12,0,0)
    result=deadline_range("Task","low",created_at)
    assert result==(created_at + timedelta(hours=240),created_at+timedelta(hours=480))

def test_deadline_contract_high():
    created_at=datetime(2026,1,1,12,0,0)
    result=deadline_range("Contract","high",created_at)
    assert result==(created_at + timedelta(hours=72),created_at+timedelta(hours=168))
def test_deadline_contract_medium():
    created_at=datetime(2026,1,1,12,0,0)
    result=deadline_range("Contract","medium",created_at)
    assert result==(created_at + timedelta(hours=168),created_at+timedelta(hours=336))
def test_deadline_contract_low():
    created_at=datetime(2026,1,1,12,0,0)
    result=deadline_range("Contract","low",created_at)
    assert result==(created_at + timedelta(hours=336),created_at+timedelta(hours=720))

def test_compute_sla_status_on_track():
    created_at=datetime(2026,1,1,12,0,0)
    deadline=created_at+timedelta(hours=100)
    ticket={
        "created_at":created_at.isoformat(),
        "deadline":deadline.isoformat(),
    }
    now=created_at+timedelta(hours=10)
    result=compute_sla_status(ticket,now)
    assert result =="on_track"
def test_compute_sla_status_at_risk_1():
    created_at=datetime(2026,1,1,12,0,0)
    deadline=created_at+timedelta(hours=100)
    ticket={
        "created_at":created_at.isoformat(),
        "deadline":deadline.isoformat(),
    }
    now=created_at+timedelta(hours=75)
    result=compute_sla_status(ticket,now)
    assert result =="at_risk"
def test_compute_sla_status_at_risk_2():
    created_at=datetime(2026,1,1,12,0,0)
    deadline=created_at+timedelta(hours=100)
    ticket={
        "created_at":created_at.isoformat(),
        "deadline":deadline.isoformat(),
    }
    now=created_at+timedelta(hours=100)
    result=compute_sla_status(ticket,now)
    assert result =="at_risk"
def test_compute_sla_status_breached():
    created_at=datetime(2026,1,1,12,0,0)
    deadline=created_at+timedelta(hours=100)
    ticket={
        "created_at":created_at.isoformat(),
        "deadline":deadline.isoformat(),
    }
    now=created_at+timedelta(hours=101)
    result=compute_sla_status(ticket,now)
    assert result =="breached"
def test_compute_sla_status_met():
    created_at=datetime(2026,1,1,12,0,0)
    deadline=created_at+timedelta(hours=100)
    ticket={
        "created_at":created_at.isoformat(),
        "deadline":deadline.isoformat(),
        "resolved_at":deadline.isoformat(),
    }
    now=created_at+timedelta(hours=200)
    result=compute_sla_status(ticket,now)
    assert result =="met"
def test_compute_sla_status_missed():
    created_at=datetime(2026,1,1,12,0,0)
    deadline=created_at+timedelta(hours=100)
    past_deadline=created_at+timedelta(hours=150)
    ticket={
        "created_at":created_at.isoformat(),
        "deadline":deadline.isoformat(),
        "resolved_at":past_deadline.isoformat(),
    }
    now=created_at+timedelta(hours=200)
    result=compute_sla_status(ticket,now)
    assert result =="missed"





