import os
from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from models import get_dashboard_stats, get_db, init_db

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "scholarship-bridge-admin-secret-2026")

init_db()


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)

    return decorated


def time_ago(dt_str):
    try:
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    except ValueError:
        try:
            dt = datetime.strptime(dt_str, "%Y-%m-%d")
        except ValueError:
            return dt_str
    diff = datetime.now() - dt
    minutes = int(diff.total_seconds() / 60)
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    return f"{days}d ago"


app.jinja_env.filters["time_ago"] = time_ago


@app.route("/")
def home():
    return redirect(url_for("admin_login"))


@app.route("/admin", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_logged_in"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db()
        admin = conn.execute(
            "SELECT * FROM admin WHERE username = ?", (username,)
        ).fetchone()
        conn.close()

        if admin and (
            admin["password"] == password
            or check_password_hash(admin["password"], password)
        ):
            session["admin_logged_in"] = True
            session["admin_name"] = admin["name"]
            session["admin_username"] = admin["username"]
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "error")

    return render_template("admin/login.html")


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.route("/admin/dashboard")
@login_required
def dashboard():
    stats = get_dashboard_stats()
    conn = get_db()
    recent = conn.execute(
        "SELECT * FROM scholarships ORDER BY created_at DESC LIMIT 5"
    ).fetchall()
    conn.close()
    return render_template(
        "admin/dashboard.html", stats=stats, recent_scholarships=recent
    )


@app.route("/admin/scholarships")
@login_required
def scholarships():
    search = request.args.get("q", "").strip()
    level = request.args.get("level", "")
    country = request.args.get("country", "")
    sort = request.args.get("sort", "newest")

    query = "SELECT * FROM scholarships WHERE 1=1"
    params = []

    if search:
        query += " AND (title LIKE ? OR university LIKE ? OR country LIKE ?)"
        params.extend([f"%{search}%"] * 3)
    if level and level != "All Levels":
        query += " AND degree_level = ?"
        params.append(level)
    if country and country != "All Countries":
        query += " AND country = ?"
        params.append(country)

    if sort == "deadline":
        query += " ORDER BY deadline ASC"
    elif sort == "title":
        query += " ORDER BY title ASC"
    else:
        query += " ORDER BY created_at DESC"

    conn = get_db()
    items = conn.execute(query, params).fetchall()
    countries = conn.execute(
        "SELECT DISTINCT country FROM scholarships ORDER BY country"
    ).fetchall()
    conn.close()

    return render_template(
        "admin/scholarships.html",
        scholarships=items,
        countries=countries,
        search=search,
        level=level,
        country=country,
        sort=sort,
    )


@app.route("/admin/scholarships/add", methods=["GET", "POST"])
@login_required
def add_scholarship():
    if request.method == "POST":
        conn = get_db()
        conn.execute(
            """INSERT INTO scholarships
            (title, university, country, degree_level, vacancies, deadline,
             funding_type, status, description, benefits, requirements, image_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                request.form["title"],
                request.form["university"],
                request.form["country"],
                request.form["degree_level"],
                int(request.form.get("vacancies") or 0),
                request.form["deadline"],
                request.form["funding_type"],
                request.form["status"],
                request.form.get("description", ""),
                request.form.get("benefits", ""),
                request.form.get("requirements", ""),
                request.form.get(
                    "image_url",
                    "https://images.unsplash.com/photo-1562774053-701939374585?w=800&q=80",
                ),
            ),
        )
        conn.commit()
        conn.close()
        flash("Scholarship saved successfully!", "success")
        return redirect(url_for("scholarships"))

    return render_template("admin/add_scholarship.html")


@app.route("/admin/scholarships/<int:sch_id>")
@login_required
def scholarship_detail(sch_id):
    conn = get_db()
    item = conn.execute(
        "SELECT * FROM scholarships WHERE id = ?", (sch_id,)
    ).fetchone()
    conn.close()
    if not item:
        flash("Scholarship not found.", "error")
        return redirect(url_for("scholarships"))
    return render_template("admin/scholarship_detail.html", scholarship=item)


@app.route("/admin/scholarships/<int:sch_id>/edit", methods=["GET", "POST"])
@login_required
def edit_scholarship(sch_id):
    conn = get_db()
    item = conn.execute(
        "SELECT * FROM scholarships WHERE id = ?", (sch_id,)
    ).fetchone()
    if not item:
        conn.close()
        flash("Scholarship not found.", "error")
        return redirect(url_for("scholarships"))

    if request.method == "POST":
        conn.execute(
            """UPDATE scholarships SET
            title=?, university=?, country=?, degree_level=?, vacancies=?,
            deadline=?, funding_type=?, status=?, description=?, benefits=?,
            requirements=?, image_url=? WHERE id=?""",
            (
                request.form["title"],
                request.form["university"],
                request.form["country"],
                request.form["degree_level"],
                int(request.form.get("vacancies") or 0),
                request.form["deadline"],
                request.form["funding_type"],
                request.form["status"],
                request.form.get("description", ""),
                request.form.get("benefits", ""),
                request.form.get("requirements", ""),
                request.form.get("image_url", item["image_url"]),
                sch_id,
            ),
        )
        conn.commit()
        conn.close()
        flash("Scholarship updated!", "success")
        return redirect(url_for("scholarship_detail", sch_id=sch_id))

    conn.close()
    return render_template("admin/edit_scholarship.html", scholarship=item)


@app.route("/admin/scholarships/<int:sch_id>/delete", methods=["POST"])
@login_required
def delete_scholarship(sch_id):
    conn = get_db()
    conn.execute("DELETE FROM scholarships WHERE id = ?", (sch_id,))
    conn.commit()
    conn.close()
    flash("Scholarship deleted.", "success")
    return redirect(url_for("scholarships"))


@app.route("/admin/students")
@login_required
def students():
    search = request.args.get("q", "").strip()
    status = request.args.get("status", "")

    query = "SELECT * FROM students WHERE 1=1"
    params = []
    if search:
        query += " AND (name LIKE ? OR email LIKE ? OR country LIKE ?)"
        params.extend([f"%{search}%"] * 3)
    if status:
        query += " AND status = ?"
        params.append(status)

    query += " ORDER BY name ASC"
    conn = get_db()
    items = conn.execute(query, params).fetchall()
    conn.close()
    return render_template("admin/students.html", students=items, search=search, status=status)


@app.route("/admin/students/<int:stu_id>")
@login_required
def student_profile(stu_id):
    conn = get_db()
    student = conn.execute(
        "SELECT * FROM students WHERE id = ?", (stu_id,)
    ).fetchone()
    apps = conn.execute(
        """SELECT a.*, s.title as scholarship_title
        FROM applications a JOIN scholarships s ON a.scholarship_id = s.id
        WHERE a.student_id = ? ORDER BY a.applied_on DESC""",
        (stu_id,),
    ).fetchall()
    conn.close()
    if not student:
        flash("Student not found.", "error")
        return redirect(url_for("students"))
    return render_template(
        "admin/student_profile.html", student=student, applications=apps
    )


@app.route("/admin/applications")
@login_required
def applications():
    tab = request.args.get("tab", "All")
    query = """SELECT a.*, s.title as scholarship_title, st.name as student_name
               FROM applications a
               JOIN scholarships s ON a.scholarship_id = s.id
               JOIN students st ON a.student_id = st.id"""
    params = []
    if tab != "All":
        query += " WHERE a.status = ?"
        params.append(tab)
    query += " ORDER BY a.applied_on DESC"

    conn = get_db()
    items = conn.execute(query, params).fetchall()
    conn.close()
    return render_template("admin/applications.html", applications=items, tab=tab)


@app.route("/admin/notifications")
@login_required
def notifications():
    conn = get_db()
    items = conn.execute(
        "SELECT * FROM notifications ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return render_template("admin/notifications.html", notifications=items)


@app.route("/admin/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "change_password":
            current = request.form.get("current_password", "")
            new_pass = request.form.get("new_password", "")
            confirm = request.form.get("confirm_password", "")
            if new_pass != confirm:
                flash("New passwords do not match.", "error")
            elif len(new_pass) < 6:
                flash("Password must be at least 6 characters.", "error")
            else:
                conn = get_db()
                admin = conn.execute(
                    "SELECT * FROM admin WHERE username = ?",
                    (session["admin_username"],),
                ).fetchone()
                if admin and (
                    admin["password"] == current
                    or check_password_hash(admin["password"], current)
                ):
                    conn.execute(
                        "UPDATE admin SET password = ? WHERE username = ?",
                        (generate_password_hash(new_pass), session["admin_username"]),
                    )
                    conn.commit()
                    flash("Password updated successfully!", "success")
                else:
                    flash("Current password is incorrect.", "error")
                conn.close()
        elif action == "update_profile":
            name = request.form.get("name", "Admin")
            conn = get_db()
            conn.execute(
                "UPDATE admin SET name = ? WHERE username = ?",
                (name, session["admin_username"]),
            )
            conn.commit()
            conn.close()
            session["admin_name"] = name
            flash("Profile updated!", "success")

    return render_template("admin/settings.html")


@app.route("/admin/more")
@login_required
def more():
    return render_template("admin/more.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=True)