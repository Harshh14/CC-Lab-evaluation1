from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)

CORS(app)

DB_PATH = "/data/courses.db"


def get_db():
    os.makedirs("/data", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    return conn


def init_db():

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            course_id TEXT PRIMARY KEY,
            course_name TEXT NOT NULL,
            credits INTEGER NOT NULL,
            department TEXT NOT NULL
        )
    """)

    count = conn.execute(
        "SELECT COUNT(*) FROM courses"
    ).fetchone()[0]

    if count == 0:

        courses = [

            (
                "CC301",
                "Cloud Computing",
                4,
                "CSE"
            ),

            (
                "PC302",
                "Parallel Computing & GPU",
                4,
                "CSE"
            ),

            (
                "CNS303",
                "Cryptography & Network Security",
                4,
                "CSE"
            )

        ]

        conn.executemany("""
            INSERT INTO courses
            (course_id, course_name, credits, department)
            VALUES (?, ?, ?, ?)
        """, courses)

    conn.commit()
    conn.close()


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/courses", methods=["GET"])
def get_courses():

    conn = get_db()

    rows = conn.execute("""
        SELECT course_id,
               course_name,
               credits,
               department
        FROM courses
        ORDER BY course_id
    """).fetchall()

    conn.close()

    return jsonify([
        dict(row)
        for row in rows
    ])


@app.route("/courses/<course_id>", methods=["GET"])
def get_course(course_id):

    conn = get_db()

    row = conn.execute("""
        SELECT course_id,
               course_name,
               credits,
               department
        FROM courses
        WHERE course_id = ?
    """, (course_id,)).fetchone()

    conn.close()

    if row is None:

        return jsonify({
            "error": "Course not found"
        }), 404

    return jsonify(dict(row))


@app.route("/courses", methods=["POST"])
def add_course():

    data = request.get_json()

    if not data:

        return jsonify({
            "error": "Request body is required"
        }), 400

    try:

        course_id = data["course_id"].strip().upper()
        course_name = data["course_name"].strip()
        credits = int(data["credits"])
        department = data["department"].strip()

    except (KeyError, ValueError, TypeError):

        return jsonify({
            "error": "Invalid course data"
        }), 400

    if not course_id or not course_name or not department:

        return jsonify({
            "error": "All fields are required"
        }), 400

    if credits < 1 or credits > 10:

        return jsonify({
            "error": "Credits must be between 1 and 10"
        }), 400

    conn = get_db()

    try:

        conn.execute("""
            INSERT INTO courses
            (course_id, course_name, credits, department)
            VALUES (?, ?, ?, ?)
        """, (
            course_id,
            course_name,
            credits,
            department
        ))

        conn.commit()

    except sqlite3.IntegrityError:

        conn.close()

        return jsonify({
            "error": "Course ID already exists"
        }), 409

    conn.close()

    return jsonify({

        "message": "Course added successfully",

        "course": {

            "course_id": course_id,
            "course_name": course_name,
            "credits": credits,
            "department": department

        }

    }), 201


@app.route("/courses/<course_id>", methods=["DELETE"])
def delete_course(course_id):

    conn = get_db()

    cursor = conn.execute("""
        DELETE FROM courses
        WHERE course_id = ?
    """, (course_id,))

    conn.commit()
    conn.close()

    if cursor.rowcount == 0:

        return jsonify({
            "error": "Course not found"
        }), 404

    return jsonify({
        "message": "Course deleted successfully"
    })


if __name__ == "__main__":

    init_db()

    app.run(
        host="0.0.0.0",
        port=5002,
        debug=False
    )