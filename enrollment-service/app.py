from flask import Flask, jsonify, request, render_template
import sqlite3
import os
import requests

app = Flask(__name__)

DB_PATH = "/data/enrollments.db"

STUDENT_SERVICE_URL = os.getenv(
    "STUDENT_SERVICE_URL",
    "http://student-service:5001"
)

COURSE_SERVICE_URL = os.getenv(
    "COURSE_SERVICE_URL",
    "http://course-service:5002"
)


def get_db():

    os.makedirs("/data", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    conn.row_factory = sqlite3.Row

    return conn


def init_db():

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id TEXT NOT NULL,
            UNIQUE(student_id, course_id)
        )
    """)

    count = conn.execute(
        "SELECT COUNT(*) FROM enrollments"
    ).fetchone()[0]

    if count == 0:

        enrollments = [
            (101, "CC301"),
            (102, "PC302"),
            (103, "CNS303")
        ]

        conn.executemany("""
            INSERT INTO enrollments
            (student_id, course_id)
            VALUES (?, ?)
        """, enrollments)

    conn.commit()
    conn.close()


def get_student(student_id):

    try:

        response = requests.get(
            f"{STUDENT_SERVICE_URL}/students/{student_id}",
            timeout=5
        )

        if response.status_code != 200:
            return None

        return response.json()

    except requests.exceptions.RequestException:

        return None


def get_course(course_id):

    try:

        response = requests.get(
            f"{COURSE_SERVICE_URL}/courses/{course_id}",
            timeout=5
        )

        if response.status_code != 200:
            return None

        return response.json()

    except requests.exceptions.RequestException:

        return None


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/enrollments", methods=["GET"])
def get_enrollments():

    conn = get_db()

    rows = conn.execute("""
        SELECT student_id, course_id
        FROM enrollments
        ORDER BY id
    """).fetchall()

    conn.close()

    result = []

    for row in rows:

        student = get_student(row["student_id"])

        course = get_course(row["course_id"])

        result.append({

            "student_id": row["student_id"],

            "course_id": row["course_id"],

            "student": student,

            "course": course

        })

    return jsonify(result)


@app.route("/enrollment/<int:student_id>")
def get_enrollment(student_id):

    conn = get_db()

    rows = conn.execute("""
        SELECT course_id
        FROM enrollments
        WHERE student_id = ?
    """, (student_id,)).fetchall()

    conn.close()

    if not rows:

        return jsonify({
            "error": "Enrollment not found"
        }), 404

    student = get_student(student_id)

    if student is None:

        return jsonify({
            "error": "Student service unavailable or student not found"
        }), 503

    enrollments = []

    for row in rows:

        course = get_course(row["course_id"])

        if course is None:

            return jsonify({
                "error": "Course service unavailable or course not found"
            }), 503

        enrollments.append({

            "student": student,

            "course": course

        })

    return jsonify({

        "student_id": student_id,

        "enrollments": enrollments

    })


@app.route("/enrollments", methods=["POST"])
def add_enrollment():

    data = request.get_json()

    if not data:

        return jsonify({
            "error": "Request body is required"
        }), 400

    try:

        student_id = int(data["student_id"])

        course_id = data["course_id"].strip().upper()

    except (KeyError, ValueError, TypeError):

        return jsonify({
            "error": "Invalid enrollment data"
        }), 400

    # Check Student Service
    student = get_student(student_id)

    if student is None:

        return jsonify({
            "error": "Student does not exist"
        }), 404

    # Check Course Service
    course = get_course(course_id)

    if course is None:

        return jsonify({
            "error": "Course does not exist"
        }), 404

    conn = get_db()

    try:

        conn.execute("""
            INSERT INTO enrollments
            (student_id, course_id)
            VALUES (?, ?)
        """, (student_id, course_id))

        conn.commit()

    except sqlite3.IntegrityError:

        conn.close()

        return jsonify({
            "error": "Student is already enrolled in this course"
        }), 409

    conn.close()

    return jsonify({

        "message": "Enrollment successful",

        "student": student,

        "course": course

    }), 201


@app.route(
    "/enrollments/<int:student_id>/<course_id>",
    methods=["DELETE"]
)
def delete_enrollment(student_id, course_id):

    conn = get_db()

    cursor = conn.execute("""
        DELETE FROM enrollments
        WHERE student_id = ?
        AND course_id = ?
    """, (student_id, course_id))

    conn.commit()
    conn.close()

    if cursor.rowcount == 0:

        return jsonify({
            "error": "Enrollment not found"
        }), 404

    return jsonify({
        "message": "Enrollment deleted successfully"
    })


if __name__ == "__main__":

    init_db()

    app.run(
        host="0.0.0.0",
        port=5003,
        debug=False
    )