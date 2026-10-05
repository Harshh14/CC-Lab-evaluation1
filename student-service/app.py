from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)

CORS(app)

DB_PATH = "/data/students.db"


def get_db():
    os.makedirs("/data", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            branch TEXT NOT NULL,
            year INTEGER NOT NULL
        )
    """)

    # Insert initial data only if table is empty
    count = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    if count == 0:
        students = [
            (101, "Student One", "CSE-AI", 3),
            (102, "Student Two", "CSE", 3),
            (103, "Student Three", "ISE", 3)
        ]

        conn.executemany("""
            INSERT INTO students
            (student_id, name, branch, year)
            VALUES (?, ?, ?, ?)
        """, students)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/students", methods=["GET"])
def get_students():
    conn = get_db()

    rows = conn.execute("""
        SELECT student_id, name, branch, year
        FROM students
        ORDER BY student_id
    """).fetchall()

    conn.close()

    students = [dict(row) for row in rows]

    return jsonify(students)


@app.route("/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    conn = get_db()

    row = conn.execute("""
        SELECT student_id, name, branch, year
        FROM students
        WHERE student_id = ?
    """, (student_id,)).fetchone()

    conn.close()

    if row is None:
        return jsonify({
            "error": "Student not found"
        }), 404

    return jsonify(dict(row))


@app.route("/students", methods=["POST"])
def add_student():
    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    try:
        student_id = int(data["student_id"])
        name = data["name"].strip()
        branch = data["branch"].strip()
        year = int(data["year"])
    except (KeyError, ValueError, TypeError):
        return jsonify({
            "error": "Invalid student data"
        }), 400

    if not name or not branch:
        return jsonify({
            "error": "Name and branch are required"
        }), 400

    if year < 1 or year > 6:
        return jsonify({
            "error": "Year must be between 1 and 6"
        }), 400

    conn = get_db()

    try:
        conn.execute("""
            INSERT INTO students
            (student_id, name, branch, year)
            VALUES (?, ?, ?, ?)
        """, (student_id, name, branch, year))

        conn.commit()

    except sqlite3.IntegrityError:
        conn.close()

        return jsonify({
            "error": "Student ID already exists"
        }), 409

    conn.close()

    return jsonify({
        "message": "Student added successfully",
        "student": {
            "student_id": student_id,
            "name": name,
            "branch": branch,
            "year": year
        }
    }), 201


@app.route("/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    conn = get_db()

    cursor = conn.execute("""
        DELETE FROM students
        WHERE student_id = ?
    """, (student_id,))

    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({
            "error": "Student not found"
        }), 404

    return jsonify({
        "message": "Student deleted successfully"
    })


if __name__ == "__main__":
    init_db()

    app.run(
        host="0.0.0.0",
        port=5001,
        debug=False
    )