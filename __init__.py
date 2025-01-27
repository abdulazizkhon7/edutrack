from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys
from os.path import abspath, dirname

sys.path.insert(0, abspath(dirname(__file__)))

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///edutrack.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    Migrate(app, db)

    with app.app_context():
        from .models import User, ClassLog, DailyLog
        db.create_all()

    return app
