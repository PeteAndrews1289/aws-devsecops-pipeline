from unittest.mock import Mock, patch

import pytest

from app.remediated.app import create_app, log_to_splunk


@pytest.fixture()
def client():
    application = create_app()
    application.config.update(TESTING=True)
    return application.test_client()


def test_status_identifies_remediated_target(client):
    response = client.get("/api/status")

    assert response.status_code == 200
    assert response.get_json() == {"status": "running", "target": "remediated"}


@pytest.mark.parametrize("payload", [None, [], {}, {"target": 8}])
def test_rejects_invalid_json_shapes(client, payload):
    response = client.post("/api/ping", json=payload)

    assert response.status_code == 400


@pytest.mark.parametrize(
    "target",
    [
        "8.8.8.8; cat /etc/passwd",
        "127.0.0.1 | id",
        "example.com",
        "$(whoami)",
        "",
    ],
)
def test_rejects_command_injection_and_non_ip_targets(client, target):
    with patch("app.remediated.app.log_to_splunk") as mock_log:
        response = client.post("/api/ping", json={"target": target})

    assert response.status_code == 400
    assert response.get_json() == {"error": "target must be a literal IPv4 or IPv6 address"}
    mock_log.assert_called_once()


@pytest.mark.parametrize(
    ("target", "normalized"),
    [("8.8.8.8", "8.8.8.8"), ("2001:4860:4860::8888", "2001:4860:4860::8888")],
)
def test_accepts_literal_ip_addresses_without_executing_commands(client, target, normalized):
    response = client.post("/api/ping", json={"target": target})

    assert response.status_code == 200
    assert response.get_json() == {"target": normalized, "validated": True}


def test_hec_logging_is_optional(monkeypatch):
    monkeypatch.delenv("SPLUNK_HEC_URL", raising=False)
    monkeypatch.delenv("SPLUNK_HEC_TOKEN", raising=False)

    assert log_to_splunk("test", "LOW", "details", "127.0.0.1") is False


def test_hec_rejects_non_https_url(monkeypatch):
    monkeypatch.setenv("SPLUNK_HEC_URL", "http://collector.example.invalid")
    monkeypatch.setenv("SPLUNK_HEC_TOKEN", "unit-test-placeholder")

    with patch("app.remediated.app.requests.post") as mock_post:
        delivered = log_to_splunk("test", "LOW", "details", "127.0.0.1")

    assert delivered is False
    mock_post.assert_not_called()


def test_hec_request_uses_default_tls_verification(monkeypatch):
    monkeypatch.setenv("SPLUNK_HEC_URL", "https://collector.example.invalid")
    monkeypatch.setenv("SPLUNK_HEC_TOKEN", "unit-test-placeholder")
    response = Mock()
    response.raise_for_status.return_value = None

    with patch("app.remediated.app.requests.post", return_value=response) as mock_post:
        delivered = log_to_splunk("test", "LOW", "details", "127.0.0.1")

    assert delivered is True
    _, kwargs = mock_post.call_args
    assert "verify" not in kwargs
    assert kwargs["timeout"] == 3
    assert kwargs["json"]["event"]["source_ip"] == "127.0.0.1"
