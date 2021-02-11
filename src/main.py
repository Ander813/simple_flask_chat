from app import create_app
from flask_sqlalchemy import SQLAlchemy

app = create_app()
db = SQLAlchemy(app)


if __name__ == "__main__":
    app.run()
