import os

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from db import get_connection
from validation import validate_opportunity

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")

# The frontend files (index.html, app.js) live in the "public" folder
app = Flask(__name__, static_folder=PUBLIC_DIR, static_url_path="")
CORS(app)

COLUMNS = ("id, title, description, research_area, faculty_name, department, "
           "required_skills, positions, deadline, status")


# ---------------------------------------------------------------- helpers
def clean_row(row):
    """MySQL gives the deadline as a date object; convert it to 'YYYY-MM-DD' text."""
    if row and row.get("deadline") is not None:
        row["deadline"] = row["deadline"].isoformat()
    return row


def find_by_id(cursor, opp_id):
    cursor.execute(f"SELECT {COLUMNS} FROM opportunities WHERE id = %s", (opp_id,))
    return clean_row(cursor.fetchone())


def read_json_body():
    """Return (body_dict, error_response). error_response is None when all is fine."""
    if not request.get_data():          # nothing sent at all
        return {}, None
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return None, (jsonify(message="Invalid JSON in request body"), 400)
    return body, None


def not_found(opp_id):
    return jsonify(message=f"Opportunity with ID {opp_id} not found"), 404


# ------------------------------------------------------------------ pages
@app.route("/")
def home():
    return send_from_directory(PUBLIC_DIR, "index.html")


# -------------------------------------------------------------------- API
# 1. CREATE  ->  POST /api/opportunities
@app.route("/api/opportunities", methods=["POST"])
def create_opportunity():
    body, error = read_json_body()
    if error:
        return error
    errors, data = validate_opportunity(body)
    if errors:
        return jsonify(message="Validation failed", errors=errors), 400

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO opportunities
                   (title, description, research_area, faculty_name, department,
                    required_skills, positions, deadline, status)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (data["title"], data["description"], data["research_area"],
                 data["faculty_name"], data["department"], data["required_skills"],
                 data["positions"], data["deadline"], data["status"]),
            )
            created = find_by_id(cur, cur.lastrowid)
        return jsonify(created), 201
    finally:
        conn.close()


# 2. READ ALL  ->  GET /api/opportunities
@app.route("/api/opportunities", methods=["GET"])
def get_all_opportunities():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT {COLUMNS} FROM opportunities ORDER BY id DESC")
            rows = [clean_row(r) for r in cur.fetchall()]
        return jsonify(rows), 200
    finally:
        conn.close()


# 3. READ ONE  ->  GET /api/opportunities/<id>
@app.route("/api/opportunities/<opp_id>", methods=["GET"])
def get_one_opportunity(opp_id):
    if not opp_id.isdigit() or int(opp_id) < 1:
        return jsonify(message="Invalid ID. It must be a positive whole number."), 400
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            row = find_by_id(cur, int(opp_id))
        if row is None:
            return not_found(opp_id)
        return jsonify(row), 200
    finally:
        conn.close()


# 4. UPDATE  ->  PUT /api/opportunities/<id>
# Partial update is allowed: fields that are not sent keep their old value.
@app.route("/api/opportunities/<opp_id>", methods=["PUT"])
def update_opportunity(opp_id):
    if not opp_id.isdigit() or int(opp_id) < 1:
        return jsonify(message="Invalid ID. It must be a positive whole number."), 400
    body, error = read_json_body()
    if error:
        return error

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            existing = find_by_id(cur, int(opp_id))
            if existing is None:
                return not_found(opp_id)

            merged = {**existing, **body}          # old values + new values
            errors, data = validate_opportunity(merged)
            if errors:
                return jsonify(message="Validation failed", errors=errors), 400

            cur.execute(
                """UPDATE opportunities SET
                     title = %s, description = %s, research_area = %s, faculty_name = %s,
                     department = %s, required_skills = %s, positions = %s,
                     deadline = %s, status = %s
                   WHERE id = %s""",
                (data["title"], data["description"], data["research_area"],
                 data["faculty_name"], data["department"], data["required_skills"],
                 data["positions"], data["deadline"], data["status"], int(opp_id)),
            )
            updated = find_by_id(cur, int(opp_id))
        return jsonify(updated), 200
    finally:
        conn.close()


# 5. DELETE  ->  DELETE /api/opportunities/<id>
@app.route("/api/opportunities/<opp_id>", methods=["DELETE"])
def delete_opportunity(opp_id):
    if not opp_id.isdigit() or int(opp_id) < 1:
        return jsonify(message="Invalid ID. It must be a positive whole number."), 400
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM opportunities WHERE id = %s", (int(opp_id),))
            deleted = cur.rowcount
        if deleted == 0:
            return not_found(opp_id)
        return jsonify(message=f"Opportunity with ID {opp_id} deleted successfully"), 200
    finally:
        conn.close()


# ----------------------------------------------------------- error pages
@app.errorhandler(404)
def handle_404(e):
    if request.path.startswith("/api"):
        return jsonify(message="API route not found"), 404
    return "Page not found", 404


@app.errorhandler(405)
def handle_405(e):
    return jsonify(message="Method not allowed"), 405


@app.errorhandler(Exception)
def handle_any_error(e):
    # e.g. the database is switched off
    from werkzeug.exceptions import HTTPException
    if isinstance(e, HTTPException):
        return e
    print("ERROR:", repr(e))
    return jsonify(message="Internal server error"), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", "3000"))
    print(f"Server running at http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
