import math
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

def truncate(f, n):
    """Truncates a float f to n decimal places without rounding."""
    if n < 0:
        raise ValueError("Decimal places must be a non-negative integer")
    multiplier = 10**n
    return math.trunc(f * multiplier) / multiplier

@app.route('/create_issue', methods=['POST'])
def create_issue():
    try:
        data = request.json
        try:
            checkIssueDuplicates(data)
        except Exception as e:
            print(e)
            return jsonify({"error": "Duplicate issue detected."}), 409
        try:
            checkDatabaseDuplicates(data)
        except Exception as e:
            print(e)
            return jsonify({"error": "Entry already in database."}), 409
        try:
            access_token = open("API_KEY", "r").read().strip()
        except FileNotFoundError:
            return jsonify({"error": "API configured improperly."}), 500
        url = "https://api.github.com/repos/auto-silent/database/issues"
        headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            return jsonify({
                "message": "Issue created successfully",
                "id": response.json()
            }), 201
        else:
            return jsonify({
                "error": "Failed to create issue",
                "status_code": response.status_code,
                "response": response.json()
            }), 400
    except Exception as e:
        print(e)
        return jsonify({"error": "Something went wrong."}), 500

def checkIssueDuplicates(data):
    body = data["body"]
    latitude = None
    for line in body.splitlines():
        if line.strip().startswith("**Latitude:**"):
            latitude = float(line.split("**Latitude:**", 1)[1].strip())
            break
    longitude = None
    for line in body.splitlines():
        if line.strip().startswith("**Longitude:**"):
            longitude = float(line.split("**Longitude:**", 1)[1].strip())
            break
    url = "https://api.github.com/repos/auto-silent/database/issues"
    try:
        access_token = open("API_KEY", "r").read().strip()
    except FileNotFoundError:
        return jsonify({"error": "API configured improperly."}), 500
    headers = {
        "Authorization": f"token {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    response_body = response.json()
    for issue in response_body:
        issue_body = issue["body"]
        issue_latitude = None
        for line in issue_body.splitlines():
            if line.strip().startswith("**Latitude:**"):
                issue_latitude = float(line.split("**Latitude:**", 1)[1].strip())
                break
        issue_longitude = None
        for line in issue_body.splitlines():
            if line.strip().startswith("**Longitude:**"):
                issue_longitude = float(line.split("**Longitude:**", 1)[1].strip())
                break
        if issue_latitude == latitude and issue_longitude == longitude:
            raise Exception("Duplicate issue found.")

def checkDatabaseDuplicates(data):
    body = data["body"]
    latitude = None
    for line in body.splitlines():
        if line.strip().startswith("**Latitude:**"):
            latitude = float(line.split("**Latitude:**", 1)[1].strip())
            break
    longitude = None
    for line in body.splitlines():
        if line.strip().startswith("**Longitude:**"):
            longitude = float(line.split("**Longitude:**", 1)[1].strip())
            break
    request_url = f"https://raw.githubusercontent.com/auto-silent/database/main/{int(latitude)}, {int(longitude)}.csv"
    response = requests.get(request_url)
    response_body = response.text
    if str(truncate(latitude, 3)) in response_body and str(truncate(longitude, 3)) in response_body:
        raise Exception("Duplicate database entry found.")

