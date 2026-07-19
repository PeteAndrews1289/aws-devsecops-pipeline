#!/usr/bin/env python3
"""Fail CI on portfolio hygiene regressions and unsafe default configuration."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {"", ".hcl", ".md", ".py", ".tf", ".txt", ".yaml", ".yml"}
FORBIDDEN_PATTERNS = {
    "AWS access-key shaped value": re.compile(r"AKIA[0-9A-Z]{16}"),
    "GitHub token-shaped value": re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    "disabled Requests TLS verification": re.compile(r"verify\s*=\s*False"),
    "account-specific ECR image": re.compile(r"\b\d{12}\.dkr\.ecr\.[\w-]+\.amazonaws\.com"),
    "temporary tunnel endpoint": re.compile(r"https?://[^\s\"']*\.ngrok(?:-free)?\.(?:app|dev|io)"),
}


def tracked_files() -> list[Path]:
    output = subprocess.check_output(
        ["git", "ls-files", "-z"], cwd=ROOT, text=True
    )
    return [ROOT / item for item in output.split("\0") if item]


def check_text_hygiene(files: list[Path]) -> list[str]:
    errors: list[str] = []
    for path in files:
        if path.suffix.lower() not in TEXT_SUFFIXES or "docs/screenshots" in path.as_posix():
            continue
        try:
            contents = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in FORBIDDEN_PATTERNS.items():
            if pattern.search(contents):
                errors.append(f"{path.relative_to(ROOT)} contains {label}")
    return errors


def check_action_pins() -> list[str]:
    errors: list[str] = []
    workflow_dir = ROOT / ".github" / "workflows"
    for path in workflow_dir.glob("*.y*ml"):
        for line_number, line in enumerate(path.read_text().splitlines(), start=1):
            stripped = line.strip()
            if stripped.startswith("uses:") and not re.search(r"@[0-9a-f]{40}(?:\s+#.*)?$", stripped):
                errors.append(f"{path.relative_to(ROOT)}:{line_number} action is not SHA-pinned")
    return errors


def check_target_separation() -> list[str]:
    vulnerable = (ROOT / "app/backend/app.py").read_text()
    remediated = (ROOT / "app/remediated/app.py").read_text()
    dockerfile = (ROOT / "app/remediated/Dockerfile").read_text()
    errors: list[str] = []

    if "shell=True" not in vulnerable or "debug=True" not in vulnerable:
        errors.append("vulnerable target no longer demonstrates the documented failure modes")
    if "shell=True" in remediated or "debug=True" in remediated:
        errors.append("remediated target contains a vulnerable execution or debug setting")
    if "USER appuser" not in dockerfile:
        errors.append("remediated Dockerfile must run as appuser")
    return errors


def check_kubernetes_defaults() -> list[str]:
    deployment_path = ROOT / "k8s/base/deployment.yaml"
    service_path = ROOT / "k8s/base/service.yaml"
    deployment = yaml.safe_load(deployment_path.read_text())
    service = yaml.safe_load(service_path.read_text())
    errors: list[str] = []

    if service["spec"].get("type") != "ClusterIP":
        errors.append("Kubernetes service must default to ClusterIP")

    pod_spec = deployment["spec"]["template"]["spec"]
    container = pod_spec["containers"][0]
    security = container.get("securityContext", {})
    if pod_spec.get("securityContext", {}).get("runAsNonRoot") is not True:
        errors.append("pod must require a non-root user")
    if security.get("allowPrivilegeEscalation") is not False:
        errors.append("container must disable privilege escalation")
    if security.get("capabilities", {}).get("drop") != ["ALL"]:
        errors.append("container must drop all Linux capabilities")
    if container.get("image") != "devsecops-flask-app:remediated":
        errors.append("Kubernetes base must reference the remediated image")
    return errors


def main() -> int:
    files = tracked_files()
    errors = [
        *check_text_hygiene(files),
        *check_action_pins(),
        *check_target_separation(),
        *check_kubernetes_defaults(),
    ]
    if errors:
        print("Repository validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Repository validation passed for {len(files)} tracked files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
