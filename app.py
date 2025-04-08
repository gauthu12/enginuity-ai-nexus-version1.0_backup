import requests
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os

from flask import Flask, render_template, request, jsonify, send_from_directory
import random
import datetime

app = Flask(__name__)

JENKINS_URL = "http://10.133.114.131:8082"
JOB_NAME = "failing-job"
JENKINS_USER = "admin"
JENKINS_API_TOKEN = "112fdabf17246e529d1faadd329cd48aec"

# Simulated memory and dataset
incident_data = [
    {"id": 1, "title": "Database latency spike", "timestamp": "2025-04-06 10:32", "status": "open", "root_cause": "Unindexed query", "impact": "High latency in user login"},
    {"id": 2, "title": "Pod restart loop in staging", "timestamp": "2025-04-06 09:15", "status": "resolved", "root_cause": "Misconfigured health check", "impact": "Intermittent downtime in staging"},
    {"id": 3, "title": "Memory leak in image processor", "timestamp": "2025-04-05 17:45", "status": "resolved", "root_cause": "Unreleased buffer", "impact": "Increased memory usage"},
    {"id": 4, "title": "Timeouts on payment API", "timestamp": "2025-04-04 12:22", "status": "open", "root_cause": "Slow third-party service", "impact": "Payment failures"}
]

self_healing_logs = [
    {"timestamp": "2025-04-06 09:45", "action": "Restarted service", "status": "Success"},
    {"timestamp": "2025-04-05 13:10", "action": "Rolled back deployment", "status": "Success"}
]

release_notes = [
    {"version": "v3.4", "changes": ["Improved cache performance", "Fixed auth token refresh bug"]},
    {"version": "v3.3", "changes": ["Upgraded PostgreSQL", "Optimized image delivery"]},
    {"version": "v3.2", "changes": ["Introduced feature flags", "Added login audit logs"]}
]

risk_scores = {
    "PR#1221": {"score": 7.8, "reason": "Infra config drift + missing unit tests"},
    "PR#1222": {"score": 3.2, "reason": "Minor UI text changes"},
    "PR#1223": {"score": 6.5, "reason": "New DB index might affect writes"}
}

def simulate_fix():
    fix = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": random.choice(["Restarted service", "Rolled back deployment", "Scaled up replicas", "Purged cache", "Rebuilt container image"]),
        "status": "Success"
    }
    self_healing_logs.append(fix)
    return fix

def fetch_jenkins_status():
    url = f"{JENKINS_URL}/job/{JOB_NAME}/lastBuild/api/json"
    response = requests.get(url, auth=(JENKINS_USER, JENKINS_API_TOKEN))
    if response.status_code == 200:
        data = response.json()
        return {
            "job": JOB_NAME,
            "status": data.get("result", "UNKNOWN"),
            "duration": f"{data.get('duration', 0)//1000}s",
            "timestamp": data.get("timestamp", "N/A")
        }
    else:
        return {
            "job": JOB_NAME,
            "status": "ERROR",
            "message": f"Failed to fetch job: {response.status_code}"
        }

def trigger_jenkins_build():
    build_url = f"{JENKINS_URL}/job/{JOB_NAME}/build"
    response = requests.post(build_url, auth=(JENKINS_USER, JENKINS_API_TOKEN))
    return response.status_code in [200, 201]


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '').lower()

    if "incident" in user_input:
        return jsonify({"response": f"There are {len(incident_data)} incidents. Use the Incident tab for details or ask for a postmortem."})

    elif "self-heal" in user_input:
        fix = simulate_fix()
        return jsonify({"response": f"✅ Self-healing triggered: {fix['action']} at {fix['timestamp']}"})

    elif "postmortem" in user_input:
        postmortem = f"Incident: {incident_data[0]['title']}\nRoot Cause: {incident_data[0]['root_cause']}\nImpact: {incident_data[0]['impact']}"
        return jsonify({"response": postmortem})

    elif "release note" in user_input:
        latest = release_notes[0]
        return jsonify({"response": f"🚀 Release {latest['version']} includes: {', '.join(latest['changes'])}"})

    elif "risk" in user_input:
        responses = []
        for pr, score in risk_scores.items():
            responses.append(f"⚠️ {pr} Risk Score: {score['score']}/10 – {score['reason']}")
        return jsonify({"response": "\n".join(responses)})

    elif "doc" in user_input or "confluence" in user_input:
        return jsonify({"response": "📝 Generated AI documentation from Jira + Git. Summary: Feature complete, 95% test pass rate, ready for release."})

    elif "test" in user_input:
        return jsonify({"response": "🔬 Smart Test Agent: 3 flaky tests detected, 2 redundant tests skipped. Coverage at 92%."})

    else:
        return jsonify({"response": "🤖 Try asking about incidents, postmortems, self-healing, risks, tests, or docs!"})

@app.route('/incidents')
def incidents():
    return jsonify(incident_data)

@app.route('/self-healing')
def healing():
    return jsonify(self_healing_logs)

@app.route('/release-notes')
def notes():
    return jsonify(release_notes)

@app.route('/risk')
def risk():
    return jsonify(risk_scores)

@app.route('/api/jenkins')
def jenkins_monitor():
    status_data = fetch_jenkins_status()
    if status_data["status"] == "FAILURE":
        triggered = trigger_jenkins_build()
        status_data["recovery"] = "🛠️   Self-healing triggered: Jenkins job restarted." if triggered else "⚠️ Self-healing failed."
    return jsonify(status_data)

if __name__ == '__main__':
    app.run(debug = True,host='0.0.0.0',port=8058)

