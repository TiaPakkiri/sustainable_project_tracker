from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user
)
from models import db, User, Campus, Category, Project

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tracker.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def roles_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if current_user.role not in roles:
                abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator


@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


# --------------------
# AUTH
# --------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        full_name = (request.form.get("full_name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        confirm = request.form.get("confirm") or ""

        if not full_name:
            flash("Full name is required.", "error")
            return render_template("signup.html")

        if not email or not password:
            flash("Email and password are required.", "error")
            return render_template("signup.html")

        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("signup.html")

        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists.", "error")
            return render_template("signup.html")

        user = User(full_name=full_name, email=email, role="student")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Account created. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        login_user(user)
        flash("Logged in successfully.", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


# --------------------
# MAIN PAGES
# --------------------
@app.route("/dashboard")
@login_required
def dashboard():
    projects = Project.query.filter_by(status="Approved").all()
    campuses = Campus.query.order_by(Campus.name).all()
    categories = Category.query.order_by(Category.name).all()
    return render_template("dashboard.html", projects=projects, campuses=campuses, categories=categories)


# Students ONLY can submit
@app.route("/submit-project", methods=["GET", "POST"])
@login_required
@roles_required("student")
def submit_project():
    campuses = Campus.query.order_by(Campus.name).all()
    categories = Category.query.order_by(Category.name).all()

    if request.method == "POST":
        title = request.form["title"]
        short_description = request.form["short_description"]
        detailed_description = request.form["detailed_description"]
        campus_id = request.form["campus_id"]
        category_id = request.form["category_id"]

        new_project = Project(
            title=title,
            short_description=short_description,
            detailed_description=detailed_description,
            campus_id=int(campus_id),
            category_id=int(category_id),
            user_id=current_user.id,
            status="Pending"
        )

        db.session.add(new_project)
        db.session.commit()
        flash("Project submitted successfully. Awaiting approval.", "success")
        return redirect(url_for("dashboard"))

    return render_template("submit_project.html", campuses=campuses, categories=categories)


@app.route("/project/<int:project_id>")
@login_required
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template("project_detail.html", project=project)


# --------------------
# STAFF/ADMIN APPROVAL ONLY
# --------------------
@app.route("/admin/pending")
@login_required
@roles_required("staff", "admin")
def admin_pending():
    pending_projects = Project.query.filter_by(status="Pending").all()
    return render_template("admin_pending.html", projects=pending_projects)


@app.route("/admin/approve/<int:project_id>", methods=["POST"])
@login_required
@roles_required("staff", "admin")
def approve_project(project_id):
    project = Project.query.get_or_404(project_id)
    project.status = "Approved"
    db.session.commit()
    flash("Project approved.", "success")
    return redirect(url_for("admin_pending"))


@app.route("/admin/reject/<int:project_id>", methods=["POST"])
@login_required
@roles_required("staff", "admin")
def reject_project(project_id):
    project = Project.query.get_or_404(project_id)
    project.status = "Rejected"
    db.session.commit()
    flash("Project rejected.", "success")
    return redirect(url_for("admin_pending"))


# Admin page (admin only)
@app.route("/admin")
@login_required
@roles_required("admin")
def admin_page():
    total_users = User.query.count()
    total_projects = Project.query.count()
    pending_projects = Project.query.filter_by(status="Pending").count()
    approved_projects = Project.query.filter_by(status="Approved").count()

    return render_template(
        "admin.html",
        total_users=total_users,
        total_projects=total_projects,
        pending_projects=pending_projects,
        approved_projects=approved_projects
    )


# Setup route to create sample users + campuses + categories
@app.route("/setup")
def setup():
    db.create_all()

    if not Campus.query.first():
        db.session.add_all([
            Campus(name="Steve Biko"),
            Campus(name="ML Sultan"),
            Campus(name="Ritson")
        ])

    if not Category.query.first():
        db.session.add_all([
            Category(name="Energy"),
            Category(name="Recycling")
        ])

    if not User.query.filter_by(email="admin@dut.ac.za").first():
        admin = User(full_name="Admin User", email="admin@dut.ac.za", role="admin")
        admin.set_password("Admin123!")
        db.session.add(admin)

    if not User.query.filter_by(email="staff@dut.ac.za").first():
        staff = User(full_name="Staff User", email="staff@dut.ac.za", role="staff")
        staff.set_password("Staff123!")
        db.session.add(staff)

    if not User.query.filter_by(email="student@dut.ac.za").first():
        student = User(full_name="Student User", email="student@dut.ac.za", role="student")
        student.set_password("Student123!")
        db.session.add(student)

    db.session.commit()
    return "Setup complete. Admin: admin@dut.ac.za/Admin123! Staff: staff@dut.ac.za/Staff123! Student: student@dut.ac.za/Student123!"


@app.errorhandler(403)
def forbidden(_):
    return render_template("403.html"), 403


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)