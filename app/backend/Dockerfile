# VULNERABILITY 4: Outdated Base Image
# Using an older "buster" image guarantees we will inherit OS-level CVEs (like in apt, curl, or bash) for Trivy to catch.
FROM python:3.8-slim-buster

WORKDIR /app

# VULNERABILITY 5: Misconfiguration - Hardcoded Environment Variables
# Storing sensitive data in plaintext ENV vars inside the Dockerfile is a bad practice.
ENV DB_PASSWORD="super_secret_admin_password"

# Copying dependencies first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copying the rest of the application
COPY . .

# VULNERABILITY 6: Misconfiguration - Running as Root
# We are not explicitly creating a non-root user, meaning this app runs as root inside the container.
# Trivy's misconfiguration scanner will flag this.

EXPOSE 5000

CMD ["python", "app.py"]