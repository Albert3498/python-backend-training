
from datetime import timedelta,datetime
from sla import deadline_range
from conftest import auth_headers,create_ticket,CIVILIAN_USER

def test_create_ticket_deadline_in_range(client,staff_token):
    min_dt,max_dt=deadline_range("Task","low",datetime.now())
    valid_deadline=min_dt+(max_dt-min_dt)/2
    resp=client.post(
        "/tickets/",
        json={
            "title": "Test ticket",
            "to": "gigel_pop",
            "description": "test",
            "priority": "low",
            "type": "Task",
            "deadline": valid_deadline.isoformat(),
        },
        headers=auth_headers(staff_token),
    )
    assert resp.status_code == 200
def test_create_ticket_deadline_below_min(client, staff_token):
    min_dt,max_dt=deadline_range("Task","low",datetime.now())
    invalid_deadline=min_dt-timedelta(hours=1)
    resp=client.post(
        "/tickets/",
        json={
            "title": "Test ticket",
            "to": "gigel_pop",
            "description": "test",
            "priority": "low",
            "type": "Task",
            "deadline": invalid_deadline.isoformat(),
        },
        headers=auth_headers(staff_token),
    )
    assert resp.status_code == 400
def test_create_ticket_deadline_above_max(client, staff_token):
    min_dt,max_dt=deadline_range("Task","low",datetime.now())
    invalid_deadline=max_dt+timedelta(hours=1)
    resp=client.post(
        "/tickets/",
        json={
            "title": "Test ticket",
            "to": "gigel_pop",
            "description": "test",
            "priority": "low",
            "type": "Task",
            "deadline": invalid_deadline.isoformat(),
        },
        headers=auth_headers(staff_token),
    )
    assert resp.status_code == 400
def test_resolved_at_stamped_on_resolve(client,staff_token):
    ticket_id=create_ticket(client,staff_token)
    resp1=client.patch(
        f"/tickets/{ticket_id}",
        json={"status":"in_progress"},
        headers=auth_headers(staff_token),
    )
    assert resp1.status_code == 200,resp1.text
    get1=client.get(f"/tickets/{ticket_id}",headers=auth_headers(staff_token))
    assert get1.json()["tickets"].get("resolved_at") is None
    resp2=client.patch(
        f"/tickets/{ticket_id}",
        json={"status":"resolved"},
        headers=auth_headers(staff_token),
    )
    assert resp2.status_code == 200,resp1.text 
    get2=client.get(f"/tickets/{ticket_id}",headers=auth_headers(staff_token))
    resolved_at=get2.json()["tickets"].get("resolved_at")
    assert resolved_at is not None
def test_create_ticket_with_status_on_track(client, staff_token):
    min_dt,max_dt=deadline_range("Task","low",datetime.now())
    deadline=min_dt+(max_dt-min_dt)/2
    resp = client.post(
        "/tickets/",
        json={
            "title": "Test ticket",
            "to": CIVILIAN_USER["username"],
            "description": "test",
            "priority": "low",
            "type": "Task",
            "deadline":deadline.isoformat(),
        },
            headers=auth_headers(staff_token),
    )
    ticket_id=resp.json()["ticket id"]
    get_resp=client.get(f"/tickets/{ticket_id}",headers=auth_headers(staff_token))
    assert get_resp.json()["tickets"]["sla_status"]=="on_track"
def test_list_tickets_visible_to_recipient(client,staff_token,civilian_token):
    ticket_id=create_ticket(client,staff_token)
    resp=client.get("/tickets/",headers=auth_headers(civilian_token))
    assert resp.status_code==200
    assert ticket_id in resp.json()

def test_list_tickets_visible_to_creator(client,staff_token):
    ticket_id=create_ticket(client,staff_token)
    resp=client.get("/tickets/",headers=auth_headers(staff_token))
    assert resp.status_code==200
    assert ticket_id in resp.json()

def test_list_tickets_not_visible_to_other_staff(client,staff_token,other_staff_token):
    ticket_id=create_ticket(client,staff_token)
    resp=client.get("/tickets/",headers=auth_headers(other_staff_token))
    assert resp.status_code==200
    assert ticket_id not in resp.json()

def test_list_tickets_includes_sla_status(client,staff_token):
    ticket_id=create_ticket(client,staff_token)
    resp=client.get("/tickets/",headers=auth_headers(staff_token))
    assert "sla_status" in resp.json()[ticket_id]

def test_list_tickets_sort_by_priority_asc(client,staff_token):
    low_id=create_ticket(client,staff_token,priority="low")
    high_id=create_ticket(client,staff_token,priority="high")
    resp=client.get("/tickets/?sort_by=priority",headers=auth_headers(staff_token))
    assert resp.status_code==200
    keys=list(resp.json().keys())
    assert keys.index(low_id)<keys.index(high_id)

def test_list_tickets_sort_by_priority_desc(client,staff_token):
    low_id=create_ticket(client,staff_token,priority="low")
    high_id=create_ticket(client,staff_token,priority="high")
    resp=client.get("/tickets/?sort_by=priority&order=desc",headers=auth_headers(staff_token))
    assert resp.status_code==200
    keys=list(resp.json().keys())
    assert keys.index(low_id)>keys.index(high_id)

def test_create_ticket_forbidden_for_civilian(client, civilian_token):
    min_dt, max_dt = deadline_range("Task", "low", datetime.now())
    valid_deadline = min_dt + (max_dt - min_dt) / 2
    resp = client.post(
        "/tickets/",
        json={
            "title": "Test ticket",
            "to": "gigel_pop",
            "description": "test",
            "priority": "low",
            "type": "Task",
            "deadline": valid_deadline.isoformat(),
        },
        headers=auth_headers(civilian_token),
    )
    assert resp.status_code == 403

def test_create_ticket_forbidden_for_non_existent_user(client,staff_token):
    min_dt, max_dt = deadline_range("Task", "low", datetime.now())
    valid_deadline = min_dt + (max_dt - min_dt) / 2
    resp = client.post(
        "/tickets/",
        json={
            "title": "Test ticket",
            "to": "non_existent_user",
            "description": "test",
            "priority": "low",
            "type": "Task",
            "deadline": valid_deadline.isoformat(),
        },
        headers=auth_headers(staff_token),
    )
    assert resp.status_code == 400

def test_create_ticket_forbidden_for_other_staff(client,staff_token):
    min_dt, max_dt = deadline_range("Task", "low", datetime.now())
    valid_deadline = min_dt + (max_dt - min_dt) / 2
    resp = client.post(
        "/tickets/",
        json={
            "title": "Test ticket",
            "to": "anpc_agent",
            "description": "test",
            "priority": "low",
            "type": "Task",
            "deadline": valid_deadline.isoformat(),
        },
        headers=auth_headers(staff_token),
    )
    assert resp.status_code == 400
def test_get_tickets__for_non_existent_ticket(client,staff_token):
    resp=client.get(f"/tickets/TASK-99999",headers=auth_headers(staff_token))
    assert resp.status_code==404

def test_get_tickets__for_unrelated_staff(client,staff_token,other_staff_token):
    ticket_id=create_ticket(client,staff_token)
    resp=client.get(f"/tickets/{ticket_id}",headers=auth_headers(other_staff_token))
    assert resp.status_code==404

def test_delete_ticket_by_creator(client,staff_token):
    ticket_id=create_ticket(client,staff_token)
    resp=client.delete(f"/tickets/{ticket_id}",headers=auth_headers(staff_token))
    assert resp.status_code==200
    follow_up=client.get(f"/tickets/{ticket_id}",headers=auth_headers(staff_token))
    assert follow_up.status_code==404

def test_delete_ticket_by_civilian_user(client,staff_token,civilian_token):
    ticket_id=create_ticket(client,staff_token)
    resp=client.delete(f"/tickets/{ticket_id}",headers=auth_headers(civilian_token))
    assert resp.status_code==403

def test_delete_ticket_for_non_existent_ticket(client,staff_token):
    resp=client.delete(f"/tickets/TASK-99999",headers=auth_headers(staff_token))
    assert resp.status_code==404

def test_edit_ticket_forbidden_for_civilian(client, staff_token, civilian_token):
    ticket_id = create_ticket(client, staff_token)
    resp = client.patch(
        f"/tickets/{ticket_id}",
        json={"description": "trying to edit"},
        headers=auth_headers(civilian_token),
    )
    assert resp.status_code == 403

def test_edit_ticket_invalid_for_ticket_type(client, staff_token):
    ticket_id = create_ticket(client, staff_token)
    resp = client.patch(
        f"/tickets/{ticket_id}",
        json={"status": "issued"},
        headers=auth_headers(staff_token),
    )
    assert resp.status_code == 400

def test_edit_ticket_not_allowed_to_skip_status(client, staff_token):
    ticket_id = create_ticket(client, staff_token)
    resp = client.patch(
        f"/tickets/{ticket_id}",
        json={"status": "resolved"},
        headers=auth_headers(staff_token),
    )
    assert resp.status_code == 400

def test_edit_ticket_non_existent_ticket(client, staff_token):
    resp = client.patch(
        f"/tickets/TASK-99999",
        json={"description": "editing"},
        headers=auth_headers(staff_token),
    )
    assert resp.status_code == 404

def test_edit_ticket_description_persists(client, staff_token):
    ticket_id = create_ticket(client, staff_token)

    resp = client.patch(
        f"/tickets/{ticket_id}",
        json={"description": "updated description"},
        headers=auth_headers(staff_token),
    )
    assert resp.status_code == 200
    get_resp=client.get(f"/tickets/{ticket_id}",headers=auth_headers(staff_token))
    assert get_resp.json()["tickets"]["description"]=="updated description"

def test_edit_ticket_priority_persists(client, staff_token):
    ticket_id = create_ticket(client, staff_token)

    resp = client.patch(
        f"/tickets/{ticket_id}",
        json={"priority": "high"},
        headers=auth_headers(staff_token),
    )
    assert resp.status_code == 200
    get_resp=client.get(f"/tickets/{ticket_id}",headers=auth_headers(staff_token))
    assert get_resp.json()["tickets"]["priority"]=="high"


