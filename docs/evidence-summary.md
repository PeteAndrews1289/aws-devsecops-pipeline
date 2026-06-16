# Evidence Summary

This file summarizes the non-screenshot evidence a reviewer can inspect in this repository.

## Application Security Evidence

- `app/backend/app.py` contains an intentionally vulnerable Flask API used for training and scanner validation.
- The `/api/ping` route demonstrates command injection risk in a controlled lab context.
- The app emits structured JSON security events for suspicious payloads before sending them to Splunk HEC.

## CI/CD Evidence

- `.github/workflows/devsecops.yml` builds the Docker image and runs Trivy.
- The Trivy configuration fails the workflow on high and critical findings.
- The workflow demonstrates a basic shift-left security gate.

## Cloud / Infrastructure Evidence

- `terraform/vpc.tf` provisions a VPC with public and private subnets.
- `terraform/ecr.tf` provisions an ECR repository for the application image.
- `terraform/eks.tf` provisions EKS resources for the Kubernetes deployment.

## Kubernetes Evidence

- `k8s/base/deployment.yaml` defines the vulnerable Flask deployment.
- `k8s/base/service.yaml` exposes the application service.
- Environment variables connect the app to Splunk HEC for runtime security events.

## Runtime Detection Evidence

- `docs/screenshots/splunk-command-injection-log.png` shows a command injection event reaching Splunk.
- The runtime path demonstrates the "shield-right" side of the lab: attack attempts should produce searchable security telemetry.

## Reviewer Takeaway

This project is strongest when reviewed as an end-to-end DevSecOps lab: vulnerable app, CI scan gate, cloud deployment, runtime attack simulation, and SIEM telemetry.
