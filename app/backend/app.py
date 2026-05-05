from flask import Flask, request, jsonify
import subprocess
import os

app = Flask(__name__)

# VULNERABILITY 1: Hardcoded Secrets
# Trivy's secret scanner will catch standard dummy AWS keys and API tokens.
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE" 
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
SUPER_SECRET_API_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"

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