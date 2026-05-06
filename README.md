# 🛡️ AWS DevSecOps CI/CD Pipeline & Runtime SOC 

## 📖 Project Overview
This project demonstrates an end-to-end DevSecOps pipeline and cloud security architecture. The goal of this project was to simulate a complete "Shift-Left" and "Shield-Right" security lifecycle. It begins with an intentionally vulnerable Python/Flask application, implements automated security gating in CI/CD, provisions highly-available AWS infrastructure via code, and routes live runtime attacks to a centralized SIEM (Splunk) for SOC monitoring. Finally, the vulnerabilities are remediated to pass the automated security gates.

## 🛠️ Tech Stack & Tools
* **Application:** Python, Flask, Docker
* **CI/CD & AppSec:** GitHub Actions, Aquasec Trivy (Container & Vulnerability Scanning)
* **Cloud Infrastructure:** AWS (VPC, EKS, ECR, ALB), Terraform (IaC)
* **Runtime Security & SecOps:** Kubernetes, Splunk (HTTP Event Collector), Ngrok

## 🏗️ Architecture & Phases

### Phase 1: The Vulnerable Application
Developed a containerized REST API using Python and Flask. The initial codebase was intentionally flawed to simulate common OWASP vulnerabilities:
* **Hardcoded Secrets:** Embedded fake AWS keys and API tokens.
* **Command Injection (RCE):** An insecure `/api/ping` endpoint that passed unsanitized user input directly to a system shell (`subprocess`).

### Phase 2: Shift-Left Security (CI/CD)
Constructed a GitHub Actions workflow to intercept vulnerable code before deployment. 
* Integrated **Trivy** to scan the Dockerfile and Python dependencies.
* Configured the pipeline to act as a hard security gate, deliberately failing the build when `CRITICAL` or `HIGH` CVEs (like outdated Werkzeug libraries) or exposed secrets were detected.

### Phase 3: Infrastructure as Code (CloudSec)
Utilized **Terraform** to provision a secure, scalable cloud environment on AWS:
* Deployed an Amazon EKS (Elastic Kubernetes Service) cluster.
* Configured a custom VPC with private/public subnets and NAT Gateways.
* Automated the deployment of an AWS Application Load Balancer (ALB) to expose the Kubernetes pods securely to the internet.

### Phase 4: Runtime Monitoring & Watchtower (SecOps)
Engineered a real-time threat detection bridge from the AWS Cloud to a local Splunk SIEM:
* Modified the Python application to format security events (failed logins, command injection attempts) as JSON payloads.
* Passed Splunk HTTP Event Collector (HEC) tokens securely into the Kubernetes pods via Environment Variables.
* Fired simulated attacks (e.g., `8.8.8.8; cat /etc/passwd`) against the live AWS Load Balancer and built a Splunk Dashboard to monitor the alerts in real-time.

### Phase 5: Remediation & Optimization
* Patched the application code by removing hardcoded secrets and neutralizing the command injection flaw using safe `subprocess` list arguments.
* Updated `requirements.txt` to secure package versions.
* Successfully pushed the patched code through the Trivy CI/CD pipeline, resulting in a clean build and automated deployment.
* Executed `terraform destroy` for strict cloud cost optimization.

## 📸 Proof of Execution
*(See `/docs/screenshots/` for full visual documentation)*
1. **[Trivy Catching Secrets & CVEs](./docs/screenshots/trivy-pipeline-failure.png)** - CI/CD pipeline failing securely.
2. **[Live Kubernetes Cluster](./docs/screenshots/k8s-app-live-status.png)** - EKS deployment and Load Balancer provisioning.
3. **[Successful Command Injection](./docs/screenshots/command-injection.png)** - Exploiting the vulnerable `/api/ping` endpoint.
4. **[Splunk SOC Dashboard](./docs/screenshots/splunk-command-injection-log.png)** - Real-time capture of the injection payload via HEC.
5. **[Green Pipeline Run](./docs/screenshots/github-actions-success.png)** - Successful build post-remediation.
