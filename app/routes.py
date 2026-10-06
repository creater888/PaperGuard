import os
import io

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    send_file,
    abort
)

from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

from .models import get_db
from .security import encrypt_file, decrypt_file
from .utils import create_folders, generate_filename


main = Blueprint("main", __name__)

create_folders()


# ---------------- HOME ----------------

@main.route("/")
def home():
    return render_template("index.html")


# ---------------- LOGIN ----------------

@main.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        db = get_db()

        user = db.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        db.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            return redirect(
                url_for("main.dashboard")
            )

        return render_template(
            "login.html",
            error="Invalid username or password"
        )

    return render_template("login.html")


# ---------------- LOGOUT ----------------

@main.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("main.home")
    )


# ---------------- DASHBOARD ----------------

@main.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("main.login"))

    db = get_db()

    # ---------------- PAPERS ----------------

    if session["role"] == "admin":

        papers = db.execute(
            """
            SELECT papers.*, users.username AS faculty_username
            FROM papers
            LEFT JOIN users
            ON papers.assigned_to = users.id
            ORDER BY papers.id DESC
            """
        ).fetchall()

    else:

        papers = db.execute(
            """
            SELECT papers.*, users.username AS faculty_username
            FROM papers
            LEFT JOIN users
            ON papers.assigned_to = users.id
            WHERE papers.assigned_to = ?
            ORDER BY papers.id DESC
            """,
            (session["user_id"],)
        ).fetchall()

    # ---------------- ADMIN SECURITY DATA ----------------

    stats = None
    suspicious_users = []

    if session["role"] == "admin":

        total_papers = db.execute(
            "SELECT COUNT(*) AS count FROM papers"
        ).fetchone()["count"]

        total_faculty = db.execute(
            """
            SELECT COUNT(*) AS count
            FROM users
            WHERE role = 'faculty'
            """
        ).fetchone()["count"]

        authorized_access = db.execute(
            """
            SELECT COUNT(*) AS count
            FROM access_logs
            WHERE action = 'PAPER_ACCESS'
            """
        ).fetchone()["count"]

        unauthorized_attempts = db.execute(
            """
            SELECT COUNT(*) AS count
            FROM access_logs
            WHERE action = 'UNAUTHORIZED_ACCESS'
            """
        ).fetchone()["count"]

        # Users with 3 or more unauthorized attempts
        suspicious_users = db.execute(
            """
            SELECT
                username,
                COUNT(*) AS attempts
            FROM access_logs
            WHERE action = 'UNAUTHORIZED_ACCESS'
            GROUP BY username
            HAVING COUNT(*) >= 3
            ORDER BY attempts DESC
            """
        ).fetchall()

        stats = {
            "total_papers": total_papers,
            "total_faculty": total_faculty,
            "authorized_access": authorized_access,
            "unauthorized_attempts": unauthorized_attempts,
            "suspicious_users": len(suspicious_users)
        }

    # ---------------- LOGS ----------------

    if session["role"] == "admin":

        logs = db.execute(
            """
            SELECT *
            FROM access_logs
            ORDER BY id DESC
            LIMIT 30
            """
        ).fetchall()

    else:

        logs = []

    db.close()

    return render_template(
        "dashboard.html",
        papers=papers,
        logs=logs,
        stats=stats,
        suspicious_users=suspicious_users
    )


# ---------------- ADD FACULTY ----------------

@main.route("/add-faculty", methods=["GET", "POST"])
def add_faculty():

    if "user_id" not in session:
        return redirect(url_for("main.login"))

    if session["role"] != "admin":
        abort(403)

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        if not username or not password:

            return render_template(
                "add_faculty.html",
                error="Username and password are required."
            )

        db = get_db()

        existing_user = db.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if existing_user:

            db.close()

            return render_template(
                "add_faculty.html",
                error="Username already exists."
            )

        hashed_password = generate_password_hash(
            password,
            method="pbkdf2:sha256"
        )

        db.execute(
            """
            INSERT INTO users
            (username, password, role)
            VALUES (?, ?, ?)
            """,
            (
                username,
                hashed_password,
                "faculty"
            )
        )

        db.commit()
        db.close()

        return redirect(
            url_for("main.dashboard")
        )

    return render_template(
        "add_faculty.html"
    )


# ---------------- UPLOAD PAPER ----------------

@main.route("/upload", methods=["GET", "POST"])
def upload():

    if "user_id" not in session:
        return redirect(url_for("main.login"))

    if session["role"] != "admin":
        abort(403)

    db = get_db()

    faculty_members = db.execute(
        """
        SELECT id, username
        FROM users
        WHERE role = 'faculty'
        ORDER BY username
        """
    ).fetchall()

    if request.method == "POST":

        title = request.form["title"]

        assigned_to = request.form.get(
            "assigned_to"
        )

        file = request.files["paper"]

        if not file or file.filename == "":

            db.close()

            return render_template(
                "upload.html",
                faculty_members=faculty_members,
                error="Please select a PDF."
            )

        if not assigned_to:

            db.close()

            return render_template(
                "upload.html",
                faculty_members=faculty_members,
                error="Please assign the paper to a faculty member."
            )

        faculty = db.execute(
            """
            SELECT id
            FROM users
            WHERE id = ?
            AND role = 'faculty'
            """,
            (assigned_to,)
        ).fetchone()

        if not faculty:

            db.close()

            return render_template(
                "upload.html",
                faculty_members=faculty_members,
                error="Invalid faculty selected."
            )

        temp_filename = generate_filename(
            file.filename
        )

        BASE_DIR = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        upload_path = os.path.join(
            BASE_DIR,
            "uploads",
            temp_filename
        )

        encrypted_path = os.path.join(
            BASE_DIR,
            "encrypted_papers",
            temp_filename + ".enc"
        )

        file.save(upload_path)

        encrypt_file(
            upload_path,
            encrypted_path
        )

        os.remove(upload_path)

        db.execute(
            """
            INSERT INTO papers
            (title, filename, uploaded_by, assigned_to)
            VALUES (?, ?, ?, ?)
            """,
            (
                title,
                temp_filename + ".enc",
                session["user_id"],
                assigned_to
            )
        )

        db.commit()
        db.close()

        return redirect(
            url_for("main.dashboard")
        )

    db.close()

    return render_template(
        "upload.html",
        faculty_members=faculty_members
    )


# ---------------- ACCESS PAPER ----------------

@main.route("/paper/<int:paper_id>")
def access_paper(paper_id):

    if "user_id" not in session:
        return redirect(url_for("main.login"))

    db = get_db()

    paper = db.execute(
        """
        SELECT *
        FROM papers
        WHERE id = ?
        """,
        (paper_id,)
    ).fetchone()

    if not paper:

        db.close()
        abort(404)

    # ---------------- AUTHORIZATION CHECK ----------------

    if (
        session["role"] != "admin"
        and paper["assigned_to"] != session["user_id"]
    ):

        db.execute(
            """
            INSERT INTO access_logs
            (username, paper_id, action, ip_address)
            VALUES (?, ?, ?, ?)
            """,
            (
                session["username"],
                paper_id,
                "UNAUTHORIZED_ACCESS",
                request.remote_addr
            )
        )

        db.commit()
        db.close()

        return """
        <h1>Access Denied</h1>
        <p>You are not authorized to access this exam paper.</p>
        <p>This attempt has been recorded.</p>
        <a href="/dashboard">Back to Dashboard</a>
        """, 403

    # ---------------- CHECK FILE ----------------

    BASE_DIR = os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )

    encrypted_path = os.path.join(
        BASE_DIR,
        "encrypted_papers",
        paper["filename"]
    )

    if not os.path.exists(encrypted_path):

        db.close()
        abort(404)

    # ---------------- LOG AUTHORIZED ACCESS ----------------

    db.execute(
        """
        INSERT INTO access_logs
        (username, paper_id, action, ip_address)
        VALUES (?, ?, ?, ?)
        """,
        (
            session["username"],
            paper_id,
            "PAPER_ACCESS",
            request.remote_addr
        )
    )

    db.commit()
    db.close()

    # ---------------- DECRYPT IN MEMORY ----------------

    decrypted_data = decrypt_file(
        encrypted_path
    )

    return send_file(
        io.BytesIO(decrypted_data),
        mimetype="application/pdf",
        as_attachment=False,
        download_name="exam_paper.pdf"
    )


# ---------------- LOGS ----------------

@main.route("/logs")
def logs():

    if "user_id" not in session:
        return redirect(url_for("main.login"))

    if session["role"] != "admin":
        abort(403)

    db = get_db()

    logs = db.execute(
        """
        SELECT *
        FROM access_logs
        ORDER BY id DESC
        """
    ).fetchall()

    db.close()

    return render_template(
        "dashboard.html",
        papers=[],
        logs=logs,
        stats=None,
        suspicious_users=[]
    )