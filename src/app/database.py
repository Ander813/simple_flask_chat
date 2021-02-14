from flask_sqlalchemy import SQLAlchemy

from src.main import app


db = SQLAlchemy(app)
