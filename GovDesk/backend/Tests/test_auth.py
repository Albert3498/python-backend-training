JOHN = {"username": "john_doe", "password": "Password123!"}
JOHN_WRONG_PASSWORD = {"username": "john_doe", "password": "not_the_real_password"}


def test_login_success(client):
    resp = client.post("/login/", json=JOHN)
    assert resp.status_code == 200, resp.text
    assert "access_token" in resp.json()


def test_login_rate_limited_after_five_failures(client):
    for _ in range(5):
        resp = client.post("/login/", json=JOHN_WRONG_PASSWORD)
        assert resp.status_code == 400

    resp = client.post("/login/", json=JOHN_WRONG_PASSWORD)
    assert resp.status_code == 429


def test_login_still_blocked_with_correct_password_once_rate_limited(client):
    resp = client.post("/login/", json=JOHN)
    assert resp.status_code == 429
