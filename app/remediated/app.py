"""Remediated comparison target for the intentionally vulnerable Flask lab."""

from __future__ import annotations

import ipaddress
import logging
import os
from urllib.parse import urlparse

import requests
from flask import Flask, jsonify, request

LOGGER = logging.getLogger(__name__)
REQUEST_TIMEOUT_SECONDS = 3


def _hec_endpoint() -> str | None:
    """Return a normalized HTTPS HEC event endpoint when configured safely."""
    base_url = os.environ.get("SPLUNK_HEC_URL", "").strip().rstrip("/")
    token = os.environ.get("SPLUNK_HEC_TOKEN", "").strip()
    if not base_url or not token:
        return None

    parsed = urlparse(base_url)
    if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password:
        LOGGER.warning("Splunk HEC URL must be an HTTPS origin without embedded credentials")
        return None

    return f"{base_url}/services/collector/event"


def log_to_splunk(event_name: str, severity: str, details: str, source_ip: str | None) -> bool:
    """Send a bounded structured event with normal certificate verification."""
    endpoint = _hec_endpoint()
    token = os.environ.get("SPLUNK_HEC_TOKEN", "").strip()
    if endpoint is None:
        return False

    payload = {
        "host": "devsecops-remediated-app",
        "sourcetype": "_json",
        "event": {
            "action": event_name[:64],
            "severity": severity[:16],
            "source_ip": source_ip or "unknown",
            "details": details[:256],
        },
    }
    headers = {
        "Authorization": f"Splunk {token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        return True
    except requests.RequestException:
        LOGGER.exception("Splunk HEC delivery failed")
        return False


def create_app() -> Flask:
    application = Flask(__name__)
    application.config["MAX_CONTENT_LENGTH"] = 4 * 1024

    @application.get("/api/status")
    def status():
        return jsonify({"status": "running", "target": "remediated"}), 200

    @application.post("/api/ping")
    def validate_ping_target():
        data = request.get_json(silent=True)
        if not isinstance(data, dict) or not isinstance(data.get("target"), str):
            return jsonify({"error": "target must be a JSON string"}), 400

        supplied_target = data["target"].strip()
        try:
            address = ipaddress.ip_address(supplied_target)
        except ValueError:
            log_to_splunk(
                "invalid_target_rejected",
                "MEDIUM",
                "Rejected a target that was not a literal IP address",
                request.remote_addr,
            )
            return jsonify({"error": "target must be a literal IPv4 or IPv6 address"}), 400

        # The portfolio-safe remediation validates the target without invoking
        # a shell or operating-system command. A production reachability check
        # should use a narrowly scoped network service with explicit policy.
        return jsonify({"target": str(address), "validated": True}), 200

    return application


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
