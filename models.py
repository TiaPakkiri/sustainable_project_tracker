from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    role = db.Column(db.String(50), default="student", nullable=False)  # student/staff/admin
    password_hash = db.Column(db.String(255), nullable=False)

    projects = db.relationship("Project", backref="user", lazy=True)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Campus(db.Model):
    __tablename__ = "campuses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

    projects = db.relationship("Project", backref="campus", lazy=True)


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

    projects = db.relationship("Project", backref="category", lazy=True)


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    short_description = db.Column(db.String(300), nullable=False)
    detailed_description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default="Pending", nullable=False)  # Pending/Approved/Completed

    campus_id = db.Column(db.Integer, db.ForeignKey("campuses.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)