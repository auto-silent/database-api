import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/create_issue', methods=['POST'])
def create_issue():
    try:
        data = request.json
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
    except Exception:
        return jsonify({"error": "Something went wrong."}), 500
