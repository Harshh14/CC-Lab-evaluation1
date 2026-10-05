from flask import Flask, jsonify, render_template

app = Flask(__name__)


# Course data
courses = {
    "CC301": {
        "courseId": "CC301",
        "courseName": "Cloud Computing",
        "credits": 4,
        "department": "CSE"
    },

    "PC302": {
        "courseId": "PC302",
        "courseName": "Parallel Computing & GPU",
        "credits": 4,
        "department": "CSE"
    },

    "CNS303": {
        "courseId": "CNS303",
        "courseName": "Cryptography & Network Security",
        "credits": 4,
        "department": "CSE"
    }
}


# Web interface
@app.route("/")
def home():
    return render_template("index.html")


# API endpoint to get course details
@app.route("/courses/<course_id>", methods=["GET"])
def get_course(course_id):

    course = courses.get(course_id)

    if course:
        return jsonify(course)

    return jsonify({
        "error": "Course not found"
    }), 404


# Health check
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "service": "course-service",
        "status": "healthy"
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5002
    )