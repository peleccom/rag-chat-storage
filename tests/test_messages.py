def test_create_message(client, auth_headers):
    session_resp = client.post(
        "/sessions", json={"user_id": "user1"}, headers=auth_headers
    )
    session_id = session_resp.json()["id"]

    resp = client.post(
        f"/sessions/{session_id}/messages",
        json={"sender": "user", "content": "Hello"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["sender"] == "user"
    assert data["content"] == "Hello"
    assert data["context"] is None


def test_create_message_with_context(client, auth_headers):
    session_resp = client.post(
        "/sessions", json={"user_id": "user1"}, headers=auth_headers
    )
    session_id = session_resp.json()["id"]

    resp = client.post(
        f"/sessions/{session_id}/messages",
        json={
            "sender": "assistant",
            "content": "Based on docs...",
            "context": "doc1.pdf, doc2.pdf",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["context"] == "doc1.pdf, doc2.pdf"


def test_create_message_sender_system(client, auth_headers):
    session_resp = client.post(
        "/sessions", json={"user_id": "user1"}, headers=auth_headers
    )
    session_id = session_resp.json()["id"]

    resp = client.post(
        f"/sessions/{session_id}/messages",
        json={"sender": "system", "content": "System message"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["sender"] == "system"


def test_list_messages(client, auth_headers):
    session_resp = client.post(
        "/sessions", json={"user_id": "user1"}, headers=auth_headers
    )
    session_id = session_resp.json()["id"]

    for i in range(3):
        client.post(
            f"/sessions/{session_id}/messages",
            json={"sender": "user", "content": f"msg {i}"},
            headers=auth_headers,
        )

    resp = client.get(f"/sessions/{session_id}/messages", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3


def test_list_messages_empty(client, auth_headers):
    session_resp = client.post(
        "/sessions", json={"user_id": "user1"}, headers=auth_headers
    )
    session_id = session_resp.json()["id"]

    resp = client.get(f"/sessions/{session_id}/messages", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert len(data["items"]) == 0

def test_messages_pagination(client, auth_headers):
    session_resp = client.post(
        "/sessions", json={"user_id": "user1"}, headers=auth_headers
    )
    session_id = session_resp.json()["id"]

    for i in range(10):
        client.post(
            f"/sessions/{session_id}/messages",
            json={"sender": "user", "content": f"msg {i}"},
            headers=auth_headers,
        )

    resp = client.get(
        f"/sessions/{session_id}/messages?page=1&page_size=3",
        headers=auth_headers,
    )
    data = resp.json()
    assert len(data["items"]) == 3
    assert data["total"] == 10
    assert data["total_pages"] == 4


def test_message_invalid_session(client, auth_headers):
    resp = client.post(
        "/sessions/00000000-0000-0000-0000-000000000000/messages",
        json={"sender": "user", "content": "Hello"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


def test_invalid_sender(client, auth_headers):
    session_resp = client.post(
        "/sessions", json={"user_id": "user1"}, headers=auth_headers
    )
    session_id = session_resp.json()["id"]

    resp = client.post(
        f"/sessions/{session_id}/messages",
        json={"sender": "bot", "content": "Hello"},
        headers=auth_headers,
    )
    assert resp.status_code == 422
