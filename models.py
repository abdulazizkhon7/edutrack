from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


db = SQLAlchemy()

class ClassLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    period = db.Column(db.String(20), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    teacher = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    attendance = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class DailyLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    after_class_notes = db.Column(db.Text, nullable=True)
    impressions = db.Column(db.Text, nullable=True)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # admin yoki student
    logs = db.relationship('DailyLog', backref='user', lazy=True)
