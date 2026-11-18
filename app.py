import sqlite3
from pathlib import Path

import os
from werkzeug.utils import secure_filename
from flask import send_from_directory, abort

from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash
from flask_wtf.csrf import CSRFProtect
app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "temporary-development-key-change-before-deployment")

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

csrf = CSRFProtect(app)

DATABASE = Path(__file__).parent / "instance" / "securecourse.db"

BASE_DIR = Path(__file__).parent

UPLOAD_FOLDERS = {
    "materials": BASE_DIR / "materials",
    "assignments": BASE_DIR / "assignments",
    "public": BASE_DIR / "public"
}
SUBMISSIONS_FOLDER = BASE_DIR / "submissions"
SUBMISSIONS_FOLDER.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {
    "pdf", "doc", "docx", "ppt", "pptx",
    "txt", "png", "jpg", "jpeg"
}

app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

for folder in UPLOAD_FOLDERS.values():
    folder.mkdir(parents=True, exist_ok=True)

def get_database():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        connection = get_database()

        user = connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        connection.close()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            return redirect(url_for("dashboard"))

        error = "Invalid username or password."

    return render_template("login.html", error=error)


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        username=session["username"],
        role=session["role"]
    )

@app.route("/materials")
def materials():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] not in ("faculty", "student"):
        abort(403)

    files = sorted(os.listdir(UPLOAD_FOLDERS["materials"]))

    return render_template(
        "resources.html",
        title="Course Materials",
        files=files,
        category="materials"
    )


@app.route("/assignments")
def assignments():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] not in ("faculty", "student"):
        abort(403)

    files = sorted(os.listdir(UPLOAD_FOLDERS["assignments"]))

    return render_template(
        "resources.html",
        title="Assignments",
        files=files,
        category="assignments"
    )

@app.route("/public")
def public_resources():
    files = sorted(os.listdir(UPLOAD_FOLDERS["public"]))

    return render_template(
        "resources.html",
        title="Public Resources",
        files=files,
        category="public"
    )

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "faculty":
        abort(403)

    message = None
    error = None

    if request.method == "POST":
        uploaded_file = request.files.get("file")
        category = request.form.get("category")

        if category not in UPLOAD_FOLDERS:
            error = "Invalid upload category."

        elif not uploaded_file or uploaded_file.filename == "":
            error = "Please select a file."

        elif not allowed_file(uploaded_file.filename):
            error = "That file type is not allowed."

        else:
            filename = secure_filename(uploaded_file.filename)

            if not filename:
                error = "Invalid filename."
            else:
                destination = UPLOAD_FOLDERS[category] / filename

                if destination.exists():
                    error = "A file with that name already exists."
                else:
                    uploaded_file.save(destination)
                    message = "File uploaded successfully."

    return render_template(
        "upload.html",
        message=message,
        error=error
    )

@app.route("/submit", methods=["GET", "POST"])
def submit_assignment():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "student":
        abort(403)

    message = None
    error = None

    student_folder = SUBMISSIONS_FOLDER / str(session["user_id"])
    student_folder.mkdir(parents=True, exist_ok=True)

    if request.method == "POST":
        uploaded_file = request.files.get("file")

        if not uploaded_file or uploaded_file.filename == "":
            error = "Please select a file."

        elif not allowed_file(uploaded_file.filename):
            error = "That file type is not allowed."

        else:
            filename = secure_filename(uploaded_file.filename)

            if not filename:
                error = "Invalid filename."

            else:
                destination = student_folder / filename

                if destination.exists():
                    error = "You have already submitted a file with that name."

                else:
                    uploaded_file.save(destination)
                    message = "Assignment submitted successfully."

    return render_template(
        "submit.html",
        message=message,
        error=error
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/download/<category>/<filename>")
def download_file(category, filename):

    if category not in UPLOAD_FOLDERS:
        abort(404)

    # Public files are available to everyone.
    if category == "public":
        return send_from_directory(
            UPLOAD_FOLDERS[category],
            filename,
            as_attachment=True
        )

    # Course materials and assignments require login.
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] not in ("faculty", "student"):
        abort(403)

    return send_from_directory(
        UPLOAD_FOLDERS[category],
        filename,
        as_attachment=True
    )
@app.route("/submissions")
def view_submissions():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "faculty":
        abort(403)

    submissions = []

    for student_folder in SUBMISSIONS_FOLDER.iterdir():
        if student_folder.is_dir():
            for file in student_folder.iterdir():
                if file.is_file():
                    submissions.append({
                        "student_id": student_folder.name,
                        "filename": file.name
                    })

    return render_template(
        "submissions.html",
        submissions=submissions
    )


@app.route("/submissions/<student_id>/<filename>")
def download_submission(student_id, filename):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "faculty":
        abort(403)

    student_folder = (SUBMISSIONS_FOLDER / student_id).resolve()

    if student_folder.parent != SUBMISSIONS_FOLDER.resolve():
        abort(404)

    return send_from_directory(
        student_folder,
        filename,
        as_attachment=True
    )

if __name__ == "__main__":
    app.run(debug=False)
