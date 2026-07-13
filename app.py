from decimal import Decimal
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

def has_at_least_decimals(number, expected_decimals):
    """
    Checks if a number has at least the expected amount of decimals using the Decimal type.
    """
    # Convert the number to a string first to ensure accurate conversion to Decimal
    d = Decimal(str(number))
    # Get the number of digits after the decimal point
    # as_tuple().exponent gives a negative value corresponding to the number of decimals
    decimal_places = abs(d.as_tuple().exponent) if d.as_tuple().exponent < 0 else 0
    return decimal_places >= expected_decimals

@app.route('/create_issue', methods=['POST'])
def create_issue():
    try:
        data = request.json
        try:
            checkValidInput(data)
        except Exception as e:
            print(e)
            return jsonify({"error": "Invalid input format."}), 422
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

def checkValidInput(data):
    body = data["body"]

    # There should be four lines in the body
    body_lines = body.splitlines()
    if len(body_lines) != 4:
        raise Exception("Invalid input format - incorrect number of lines.")
    
    # First line should have mosque name with ###
    if not body_lines[0].strip().startswith("###"):
        raise Exception("Invalid input format - incorrect mosque name format.")
    # Second line should have mosque address with **Address:**
    if not body_lines[1].strip().startswith("**Address:**"):
        raise Exception("Invalid input format - incorrect address format.")
    
    # Third line should have latitude with **Latitude:**
    if not body_lines[2].strip().startswith("**Latitude:**"):
        raise Exception("Invalid input format - incorrect latitude format.")
    # Latitude should be a number with at least 5 decimal places
    latitude = float(body_lines[2].split("**Latitude:**", 1)[1].strip())
    if not has_at_least_decimals(latitude, 5):
        raise Exception("Invalid input format - latitude must have at least 5 decimal places.")
    
    # Fourth line should have longitude with **Longitude:**
    if not body_lines[3].strip().startswith("**Longitude:**"):
        raise Exception("Invalid input format - incorrect longitude format.")
    # Longitude should be a number with at least 5 decimal places
    longitude = float(body_lines[3].split("**Longitude:**", 1)[1].strip())
    if not has_at_least_decimals(longitude, 5):
        raise Exception("Invalid input format - longitude must have at least 5 decimal places.")