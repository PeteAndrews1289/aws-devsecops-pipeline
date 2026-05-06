from flask import Flask, request, jsonify
import subprocess
import os
import requests
import datetime

app = Flask(__name__)

# VULNERABILITY 1: Hardcoded Secrets
# Trivy's secret scanner will catch standard dummy AWS keys and API tokens.
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE" 
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
SUPER_SECRET_API_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"

# Fetch Splunk configuration from Kubernetes environment variables
SPLUNK_HEC_URL = os.environ.get('SPLUNK_HEC_URL')
SPLUNK_HEC_TOKEN = os.environ.get('SPLUNK_HEC_TOKEN')

def log_to_splunk(event_name, severity, details):
    """Formats the security event and sends it to Splunk via HEC"""
    if not SPLUNK_HEC_URL or not SPLUNK_HEC_TOKEN:
        print("Splunk HEC configuration missing. Skipping log.")
        return

    # Splunk HEC requires events to be wrapped in an 'event' key
    splunk_payload = {
        "time": datetime.datetime.now().timestamp(),
        "host": "devsecops-flask-pod",
        "sourcetype": "_json",
        "event": {
            "action": event_name,
            "severity": severity,
            "source_ip": request.remote_addr,
            "details": details
        }
    }

    headers = {
        "Authorization": f"Splunk {SPLUNK_HEC_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        # Append the specific HEC endpoint to the base ngrok URL
        endpoint = f"{SPLUNK_HEC_URL}/services/collector/event"
        requests.post(endpoint, headers=headers, json=splunk_payload, verify=False, timeout=3)
    except Exception as e:
        print(f"Failed to send log to Splunk: {e}")

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({"status": "running", "environment": "development"}), 200

# VULNERABILITY 2: Command Injection
# An attacker can pass '8.8.8.8; cat /etc/passwd' to execute arbitrary commands.
@app.route('/api/ping', methods=['POST'])
def ping_host():
    data = request.get_json()
    # If no target is provided, default to localhost
    target = data.get('target', '127.0.0.1')

    # SECURITY LOGGING: Detect Command Injection attempts and send to Splunk
    if ";" in target or "|" in target or "&" in target:
        log_to_splunk("command_injection_attempt", "CRITICAL", f"Malicious payload detected in ping target: {target}")

    # INSECURE: Directly passing unsanitized user input to a system shell
    command = f"ping -c 1 {target}"
    
    try:
        output = subprocess.check_output(command, shell=True, text=True)
        return jsonify({"output": output}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Ping failed", "details": str(e)}), 500

if __name__ == '__main__':
    # VULNERABILITY 3: Running in debug mode on all interfaces
    app.run(host='0.0.0.0', port=5000, debug=True)