def test_create_session(client, auth_headers):
    resp = client.post(
        "/sessions",
        json={"user_id": "user1", "title": "Test Chat"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Test Chat"
    assert data["user_id"] == "user1"
    assert data["is_favorite"] is False


def test_list_sessions(client, auth_headers):
    client.post(
        "/sessions", json={"user_id": "user1", "title": "Chat 1"}, headers=auth_headers
    )
    client.post(
        "/sessions", json={"user_id": "user1", "title": "Chat 2"}, headers=auth_headers
    )

    resp = client.get("/sessions?user_id=user1", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_get_session(client, auth_headers):
    create_resp = client.post(
        "/sessions", json={"user_id": "user1", "title": "My Chat"}, headers=auth_headers
    )
    session_id = create_resp.json()["id"]

    resp = client.get(f"/sessions/{session_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "My Chat"


def test_update_session_rename(client, auth_headers):
    create_resp = client.post(
        "/sessions", json={"user_id": "user1", "title": "Old"}, headers=auth_headers
    )
    session_id = create_resp.json()["id"]

    resp = client.patch(
        f"/sessions/{session_id}",
        json={"title": "Renamed"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Renamed"


def test_update_session_favorite(client, auth_headers):
    create_resp = client.post(
        "/sessions", json={"user_id": "user1"}, headers=auth_headers
    )
    session_id = create_resp.json()["id"]

    resp = client.patch(
        f"/sessions/{session_id}",
        json={"is_favorite": True},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["is_favorite"] is True


def test_delete_session(client, auth_headers):
    create_resp = client.post(
        "/sessions", json={"user_id": "user1"}, headers=auth_headers
    )
    session_id = create_resp.json()["id"]

    resp = client.delete(f"/sessions/{session_id}", headers=auth_headers)
    assert resp.status_code == 204


def test_delete_session_not_found(client, auth_headers):
    create_resp = client.post(
        "/sessions", json={"user_id": "user1"}, headers=auth_headers
    )
    session_id = create_resp.json()["id"]

    resp = client.delete(f"/sessions/{session_id}", headers=auth_headers)
    assert resp.status_code == 204

    resp = client.get(f"/sessions/{session_id}", headers=auth_headers)
    assert resp.status_code == 404

def test_missing_api_key_returns_401(client):
    resp = client.get("/sessions?user_id=user1")
    assert resp.status_code == 401


def test_invalid_api_key_returns_401(client):
    resp = client.get(
        "/sessions?user_id=user1", headers={"X-API-Key": "wrong-key"}
    )
    assert resp.status_code == 401


def test_pagination(client, auth_headers):
    for i in range(5):
        client.post(
            "/sessions",
            json={"user_id": "user1", "title": f"Chat {i}"},
            headers=auth_headers,
        )

    resp = client.get(
        "/sessions?user_id=user1&page=1&page_size=2", headers=auth_headers
    )
    data = resp.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["total_pages"] == 3
