import pytest
from conftest import CIVILIAN_USER,auth_headers,create_ticket

def create_priority_request(client, civilian_token, ticket_id, priority="high"):
    resp = client.post(
        "/request/",
        json={"ticket_id": ticket_id, "priority": priority},
        headers=auth_headers(civilian_token),
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["request id"]


def test_create_request_success(client, staff_token, civilian_token):
    ticket_id = create_ticket(client, staff_token)
    request_id = create_priority_request(client, civilian_token, ticket_id, "high")
    assert request_id.startswith("REQ-")


def test_create_request_ticket_not_found(client, civilian_token):
    resp = client.post(
        "/request/",
        json={"ticket_id": "NOPE-1", "priority": "high"},
        headers=auth_headers(civilian_token),
    )
    assert resp.status_code == 404


def test_create_request_rejects_fourth_pending(client, staff_token, civilian_token):
    ticket_id = create_ticket(client, staff_token)
    create_priority_request(client, civilian_token, ticket_id, "high")
    create_priority_request(client, civilian_token, ticket_id, "medium")
    create_priority_request(client, civilian_token, ticket_id, "low")

    resp = client.post(
        "/request/",
        json={"ticket_id": ticket_id, "priority": "high"},
        headers=auth_headers(civilian_token),
    )
    assert resp.status_code == 400


def test_create_request_wrong_recipient(client, staff_token):
    ticket_id = create_ticket(client, staff_token)
    resp = client.post(
        "/request/",
        json={"ticket_id": ticket_id, "priority": "high"},
        headers=auth_headers(staff_token),
    )
    assert resp.status_code == 403


def test_accept_request_success(client, staff_token, civilian_token):
    ticket_id = create_ticket(client, staff_token, priority="low")
    request_id = create_priority_request(client, civilian_token, ticket_id, "high")

    resp = client.post(f"/request/{request_id}/approve", headers=auth_headers(staff_token))
    assert resp.status_code == 200, resp.text

    ticket_resp = client.get(f"/tickets/{ticket_id}", headers=auth_headers(staff_token))
    assert ticket_resp.json()["tickets"]["priority"] == "high"


def test_accept_request_wrong_user(client, staff_token, civilian_token, other_staff_token):
    ticket_id = create_ticket(client, staff_token)
    request_id = create_priority_request(client, civilian_token, ticket_id, "high")

    resp = client.post(f"/request/{request_id}/approve", headers=auth_headers(other_staff_token))
    assert resp.status_code == 403


def test_accept_request_already_decided(client, staff_token, civilian_token):
    ticket_id = create_ticket(client, staff_token)
    request_id = create_priority_request(client, civilian_token, ticket_id, "high")

    first = client.post(f"/request/{request_id}/approve", headers=auth_headers(staff_token))
    assert first.status_code == 200

    second = client.post(f"/request/{request_id}/approve", headers=auth_headers(staff_token))
    assert second.status_code == 400


def test_reject_request_success(client, staff_token, civilian_token):
    ticket_id = create_ticket(client, staff_token, priority="low")
    request_id = create_priority_request(client, civilian_token, ticket_id, "high")

    resp = client.post(f"/request/{request_id}/reject", headers=auth_headers(staff_token))
    assert resp.status_code == 200, resp.text

    ticket_resp = client.get(f"/tickets/{ticket_id}", headers=auth_headers(staff_token))
    assert ticket_resp.json()["tickets"]["priority"] == "low"


def test_reject_request_not_found(client, staff_token):
    resp = client.post("/request/does-not-exist/reject", headers=auth_headers(staff_token))
    assert resp.status_code == 404


def test_list_requests_visible_to_civilian(client, staff_token, civilian_token):
    ticket_id = create_ticket(client, staff_token)
    request_id = create_priority_request(client, civilian_token, ticket_id, "high")

    resp = client.get("/request/", headers=auth_headers(civilian_token))
    assert resp.status_code == 200, resp.text
    assert request_id in resp.json()


def test_list_requests_visible_to_staff_owner(client, staff_token, civilian_token):
    ticket_id = create_ticket(client, staff_token)
    request_id = create_priority_request(client, civilian_token, ticket_id, "high")

    resp = client.get("/request/", headers=auth_headers(staff_token))
    assert resp.status_code == 200, resp.text
    assert request_id in resp.json()


def test_list_requests_not_visible_to_unrelated_staff(client, staff_token, civilian_token, other_staff_token):
    ticket_id = create_ticket(client, staff_token)
    request_id = create_priority_request(client, civilian_token, ticket_id, "high")

    resp = client.get("/request/", headers=auth_headers(other_staff_token))
    assert resp.status_code == 200, resp.text
    assert request_id not in resp.json()


def test_get_request_success_as_civilian(client, staff_token, civilian_token):
    ticket_id = create_ticket(client, staff_token)
    request_id = create_priority_request(client, civilian_token, ticket_id, "high")

    resp = client.get(f"/request/{request_id}", headers=auth_headers(civilian_token))
    assert resp.status_code == 200, resp.text
    assert resp.json()["requests"]["ticket_id"] == ticket_id


def test_get_request_success_as_staff_owner(client, staff_token, civilian_token):
    ticket_id = create_ticket(client, staff_token)
    request_id = create_priority_request(client, civilian_token, ticket_id, "high")

    resp = client.get(f"/request/{request_id}", headers=auth_headers(staff_token))
    assert resp.status_code == 200, resp.text


def test_get_request_not_visible_to_unrelated_staff(client, staff_token, civilian_token, other_staff_token):
    ticket_id = create_ticket(client, staff_token)
    request_id = create_priority_request(client, civilian_token, ticket_id, "high")

    resp = client.get(f"/request/{request_id}", headers=auth_headers(other_staff_token))
    assert resp.status_code == 404


def test_get_request_not_found(client, staff_token):
    resp = client.get("/request/does-not-exist", headers=auth_headers(staff_token))
    assert resp.status_code == 404
