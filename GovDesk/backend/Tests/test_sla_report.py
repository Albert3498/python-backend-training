from conftest import create_ticket,auth_headers
from datetime import datetime,timedelta

def test_sla_report_visible_to_civilian(client, staff_token, civilian_token):
    from Ticket_creation import tickets
    ticket_id = create_ticket(client, staff_token)
    tickets[ticket_id]["deadline"]=(datetime.now()-timedelta(hours=1)).isoformat()
    resp = client.get("/sla/report", headers=auth_headers(civilian_token))
    assert resp.status_code == 200, resp.text
    assert ticket_id in resp.json()

def test_sla_report_visible_to_staff_owner(client, staff_token):
    from Ticket_creation import tickets
    ticket_id = create_ticket(client, staff_token)
    tickets[ticket_id]["deadline"]=(datetime.now()-timedelta(hours=1)).isoformat()
    resp = client.get("/sla/report", headers=auth_headers(staff_token))
    assert resp.status_code == 200, resp.text
    assert ticket_id in resp.json()

def test_sla_report_not_visible_to_unrelated_staff(client, staff_token,other_staff_token):
    from Ticket_creation import tickets
    ticket_id = create_ticket(client, staff_token)
    tickets[ticket_id]["deadline"]=(datetime.now()-timedelta(hours=1)).isoformat()
    resp = client.get("/sla/report", headers=auth_headers(other_staff_token))
    assert resp.status_code == 200, resp.text
    assert ticket_id not in resp.json()

def test_sla_report_excludes_on_track(client, staff_token):
    ticket_id = create_ticket(client, staff_token)
    resp = client.get("/sla/report", headers=auth_headers(staff_token))
    assert resp.status_code == 200, resp.text
    assert ticket_id not in resp.json()