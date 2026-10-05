from flask import Flask, jsonify, render_template
import requests
import os

app = Flask(__name__)


# URLs of the other microservices
# Docker service names are used for inter-service communication.
STUDENT_SERVICE_URL = os.getenv(
    "STUDENT_SERVICE_URL",
    "http://student-service:5001"
)

COURSE_SERVICE_URL = os.getenv(
    "COURSE_SERVICE_URL",
    "http://course-service:5002"
)


# Enrollment data
# Student ID -> Course IDs
enrollments = {
    101: ["CC301"],
    102: ["PC302"],
    103: ["CNS303"]
}


# Web interface
@app.route("/")
def home():
    return render_template("index.html")


# Get enrollment details for a student
@app.route("/enrollment/<int:student_id>", methods=["GET"])
def get_enrollment(student_id):

    try:

        # Check whether student has an enrollment
        course_ids = enrollments.get(student_id)

        if course_ids is None:
            return jsonify({
                "error": "Enrollment not found"
            }), 404


        # Request student information from Student Service
        student_response = requests.get(
            f"{STUDENT_SERVICE_URL}/students/{student_id}",
            timeout=5
        )

        if student_response.status_code != 200:
            return jsonify({
                "error": "Student Service unavailable"
            }), 503


        student = student_response.json()


        # Get course information from Course Service
        courses = []

        for course_id in course_ids:

            course_response = requests.get(
                f"{COURSE_SERVICE_URL}/courses/{course_id}",
                timeout=5
            )

            if course_response.status_code != 200:
                return jsonify({
                    "error": f"Course {course_id} not found"
                }), 404

            courses.append(course_response.json())


        # Return combined enrollment information
        return jsonify({
            "student": student,
            "courses": courses
        })


    except requests.exceptions.RequestException as e:

        return jsonify({
            "error": "Unable to communicate with Student or Course Service",
            "details": str(e)
        }), 503


# Health check
@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "service": "enrollment-service",
        "status": "healthy"
    })


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5003
    )