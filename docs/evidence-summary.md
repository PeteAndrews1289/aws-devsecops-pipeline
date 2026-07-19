# Evidence Summary

## Current, reproducible evidence

| Claim | Reviewable artifact | What it proves |
|---|---|---|
| The vulnerable target still contains an unsafe command path | `app/backend/app.py` | A clearly isolated scanner/training target uses shell interpolation intentionally. |
| The remediated target rejects injection syntax | `app/remediated/tests/test_app.py` | Regression tests cover malformed JSON, shell metacharacters, hostnames, IPv4, IPv6, and HEC transport behavior. |
| The secure target—not the demo—is gated | `.github/workflows/trivy-scan.yml` | Tests, Bandit, hygiene validation, and the remediated image scan are blocking; the vulnerable scan is advisory. |
| Repository configuration is free of checked-in operational identifiers | `scripts/validate_repository.py` | CI checks text files, action pins, Kubernetes settings, and target separation. |
| Infrastructure syntax is valid | `terraform/` plus the CI workflow | Terraform formatting and validation run without AWS credentials or deployment. |
| Kubernetes defaults target the remediated app | `k8s/base/` | The example uses a private service, non-root runtime controls, and external configuration references. |

## Historical evidence

| Artifact | Observation | Limitation |
|---|---|---|
| `docs/screenshots/trivy-debian-cve.png` | The deliberately old Debian image produced HIGH package findings. | Point-in-time scanner database and image state. |
| `docs/screenshots/trivy-python-cve.png` | The deliberately obsolete Python packages produced HIGH findings. | Point-in-time result; current CI output supersedes counts. |
| `docs/screenshots/trivy-pipeline-failure.png` | An earlier workflow failed when expected vulnerable findings were treated as the release target. | The screenshot predates action pinning and target separation. |
| `docs/screenshots/splunk-command-injection-log.png` | One structured `command_injection_attempt` event reached Splunk during the controlled lab. | One event proves ingestion, not coverage, reliability, or production readiness. |

Screenshots that displayed retired public endpoints, account-specific image paths, or raw shell output are intentionally absent from the current branch. They remain available in Git history if provenance is required.

## Claims this repository does not make

- No environment is currently running.
- CI does not push an image to ECR or deploy to EKS.
- Terraform validation is not a successful plan or apply.
- A single Splunk event is not evidence of complete detection coverage.
- The intentionally vulnerable image is not safe to deploy publicly.
