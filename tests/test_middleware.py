"""Tests for API auth middleware and channel contracts."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from backend.main import app, session_histories

    session_histories.clear()

    async def _fake_stream(user_input, session_id, chat_history):
        yield "ok"

    with patch("backend.main.astream_response", new=_fake_stream):
        with TestClient(app) as c:
            yield c

    session_histories.clear()


def test_health_with_client_header(client):
    resp = client.get("/health", headers={"X-ASK-Client": "cli"})
    assert resp.status_code == 200
    assert resp.json()["client"] == "cli"


def test_api_key_rejects_without_token(client, monkeypatch):
    monkeypatch.setenv("ASK_API_KEY", "test-secret")
    from backend.config import Settings

    with patch("backend.middleware.settings", Settings(ask_api_key="test-secret")):
        from backend.main import app

        with TestClient(app) as c:
            resp = c.post("/chat", json={"message": "hi"})
            assert resp.status_code == 401


def test_api_key_allows_with_token(client, monkeypatch):
    monkeypatch.setenv("ASK_API_KEY", "test-secret")

    async def _fake(user_input, session_id, chat_history):
        yield "authenticated"

    with patch("backend.main.astream_response", new=_fake):
        with patch("backend.middleware.settings") as mock_settings:
            mock_settings.ask_api_key = "test-secret"
            from backend.main import app

            with TestClient(app) as c:
                resp = c.post(
                    "/chat",
                    json={"message": "hi"},
                    headers={"Authorization": "Bearer test-secret"},
                )
                assert resp.status_code == 200


def test_chat_rejects_voice_output_channel(client):
    resp = client.post(
        "/chat/stream",
        json={
            "message": "hi",
            "output_channel": "voice",
        },
    )
    assert resp.status_code == 400


def test_ops_backup_disabled_without_api_key(client):
    with patch("backend.middleware.settings") as mock_settings:
        mock_settings.ask_api_key = ""
        resp = client.post("/ops/backup")
        assert resp.status_code == 503


def test_ops_backup_rejects_without_token(client):
    with patch("backend.middleware.settings") as mock_settings:
        mock_settings.ask_api_key = "test-secret"
        resp = client.post("/ops/backup")
        assert resp.status_code == 401


def test_ops_restore_rejects_disallowed_target(client):
    with patch("backend.middleware.settings") as mock_settings:
        mock_settings.ask_api_key = "test-secret"
        resp = client.post(
            "/ops/restore",
            json={"backup_path": "./backups/memory_graph.db.bak", "target_path": "/etc/passwd"},
            headers={"Authorization": "Bearer test-secret"},
        )
        assert resp.status_code == 400


class _FakeWebSocket:
    def __init__(self, headers=None, query_params=None):
        self.headers = headers or {}
        self.query_params = query_params or {}


def test_authorize_websocket_open_when_no_key_configured():
    from backend.middleware import authorize_websocket

    with patch("backend.middleware.settings") as mock_settings:
        mock_settings.ask_api_key = ""
        assert authorize_websocket(_FakeWebSocket()) is True


def test_authorize_websocket_accepts_bearer_header():
    from backend.middleware import authorize_websocket

    with patch("backend.middleware.settings") as mock_settings:
        mock_settings.ask_api_key = "test-secret"
        ws = _FakeWebSocket(headers={"authorization": "Bearer test-secret"})
        assert authorize_websocket(ws) is True


def test_authorize_websocket_accepts_token_query_param():
    from backend.middleware import authorize_websocket

    with patch("backend.middleware.settings") as mock_settings:
        mock_settings.ask_api_key = "test-secret"
        ws = _FakeWebSocket(query_params={"token": "test-secret"})
        assert authorize_websocket(ws) is True


def test_authorize_websocket_rejects_missing_or_invalid_credentials():
    from backend.middleware import authorize_websocket

    with patch("backend.middleware.settings") as mock_settings:
        mock_settings.ask_api_key = "test-secret"
        assert authorize_websocket(_FakeWebSocket()) is False
        assert authorize_websocket(_FakeWebSocket(query_params={"token": "wrong"})) is False
        assert authorize_websocket(_FakeWebSocket(headers={"authorization": "Bearer wrong"})) is False


def test_voice_stt_stream_rejects_connection_without_key(client):
    with patch("backend.middleware.settings") as mock_settings:
        mock_settings.ask_api_key = "test-secret"
        with pytest.raises(Exception):  # noqa: B017 - Starlette raises WebSocketDisconnect on rejected handshake
            with client.websocket_connect("/voice/stt/stream"):
                pass


def test_voice_stt_stream_accepts_connection_with_token_query_param(client):
    with patch("backend.middleware.settings") as mock_settings:
        mock_settings.ask_api_key = "test-secret"
        with client.websocket_connect("/voice/stt/stream?token=test-secret") as ws:
            ws.send_json({"browser_transcript": "hello", "final": True})
            data = ws.receive_json()
            assert data["text"] == "hello"
