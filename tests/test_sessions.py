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


def test_create_session_no_title(client, auth_headers):
    resp = client.post(
        "/sessions",
        json={"user_id": "user1"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["title"] == "New Chat"


def test_create_session_missing_user_id(client, auth_headers):
    resp = client.post(
        "/sessions",
        json={"title": "No User"},
        headers=auth_headers,
    )
    assert resp.status_code == 422


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


def test_list_sessions_empty(client, auth_headers):
    resp = client.get("/sessions?user_id=nobody", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["items"] == []


def test_get_session(client, auth_headers):
    create_resp = client.post(
        "/sessions", json={"user_id": "user1", "title": "My Chat"}, headers=auth_headers
    )
    session_id = create_resp.json()["id"]

    resp = client.get(f"/sessions/{session_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "My Chat"


def test_get_session_not_found(client, auth_headers):
    resp = client.get(
        "/sessions/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert resp.status_code == 404


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


def test_update_session_empty_body(client, auth_headers):
    create_resp = client.post(
        "/sessions", json={"user_id": "user1", "title": "Original"}, headers=auth_headers
    )
    session_id = create_resp.json()["id"]

    resp = client.patch(
        f"/sessions/{session_id}",
        json={},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Original"


def test_update_session_updates_updated_at(client, auth_headers):
    create_resp = client.post(
        "/sessions", json={"user_id": "user1", "title": "Before"}, headers=auth_headers
    )
    session_id = create_resp.json()["id"]
    original_updated = create_resp.json()["updated_at"]

    resp = client.patch(
        f"/sessions/{session_id}",
        json={"title": "After"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["updated_at"] != original_updated


def test_session_message_count(client, auth_headers):
    session_resp = client.post(
        "/sessions", json={"user_id": "user1"}, headers=auth_headers
    )
    session_id = session_resp.json()["id"]

    assert session_resp.json()["message_count"] == 0

    client.post(
        f"/sessions/{session_id}/messages",
        json={"sender": "user", "content": "Hi"},
        headers=auth_headers,
    )
    client.post(
        f"/sessions/{session_id}/messages",
        json={"sender": "assistant", "content": "Hello"},
        headers=auth_headers,
    )

    resp = client.get(f"/sessions/{session_id}", headers=auth_headers)
    assert resp.json()["message_count"] == 2


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
