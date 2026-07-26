import os
import shutil
import sys
import pytest
from datetime import datetime

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,BACKEND_DIR)

from sla import deadline_range 

@pytest.fixture(scope="session", autouse=True)
def isolated_workdir(tmp_path_factory):
    """Run the whole test session against throwaway copies of the data files.

    counter.json/requests.json start empty (module loaders fall back to {} when
    the file is missing), so each test run gets a clean slate. userdata.db is
    copied so existing test accounts (gigel_pop, anaf_agent, ...) still work.
    """
    tmp_dir = tmp_path_factory.mktemp("govdesk_test")
    shutil.copy(os.path.join(BACKEND_DIR, "userdata.db"), tmp_dir / "userdata.db")

    original_cwd = os.getcwd()
    os.chdir(tmp_dir)
    try:
        yield
    finally:
        os.chdir(original_cwd)


@pytest.fixture(scope="session")
def client(isolated_workdir):
    from fastapi.testclient import TestClient
    from main import app

    return TestClient(app)

STAFF_USER = {"username": "anaf_agent", "password": "Fiscal_ANAF_2026!"}
OTHER_STAFF_USER = {"username": "anpc_agent", "password": "Consumator_ANPC_77"}
CIVILIAN_USER = {"username": "gigel_pop", "password": "Parola_Gigel_99"}


def login(client, creds):
    resp = client.post("/login/", json=creds)
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def staff_token(client):
    return login(client, STAFF_USER)


@pytest.fixture
def other_staff_token(client):
    return login(client, OTHER_STAFF_USER)


@pytest.fixture
def civilian_token(client):
    return login(client, CIVILIAN_USER)

def create_ticket(client, staff_token, priority="low",deadline=None):
    if deadline is None:
        min_dt,max_dt=deadline_range("Task",priority,datetime.now())
        deadline=min_dt+(max_dt-min_dt)/2
    resp = client.post(
        "/tickets/",
        json={
            "title": "Test ticket",
            "to": CIVILIAN_USER["username"],
            "description": "test",
            "priority": priority,
            "type": "Task",
            "deadline":deadline.isoformat()
        },
        headers=auth_headers(staff_token),
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["ticket id"]


