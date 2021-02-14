"""
Run this once to create tables in your database
"""
if __name__ == "__main__":
    from src.app.models import Chat, User, Message
    from src.app.database import db

    db.create_all()
