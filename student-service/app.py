from flask import Flask, jsonify, render_template

app = Flask(__name__)


# Sample student data
students = {
    101: {
        "id": 101,
        "name": "Student One",
        "department": "CSE-AI",
        "year": 3
    },
    102: {
        "id": 102,
        "name": "Student Two",
        "department": "CSE",
        "year": 3
    },
    103: {
        "id": 103,
        "name": "Student Three",
        "department": "ISE",
        "year": 3
    }
}

@app.route("/")
def home():
    return render_template("index.html")

# API endpoint to get student details
@app.route("/students/<int:student_id>", methods=["GET"])
def get_student(student_id):

    student = students.get(student_id)

    if student:
        return jsonify(student)

    return jsonify({
        "error": "Student not found"
    }), 404


# Health check endpoint
@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "service": "student-service",
        "status": "running"
    })


# Start the Flask server
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )