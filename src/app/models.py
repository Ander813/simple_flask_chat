from datetime import datetime

from flask_login import UserMixin
from passlib.context import CryptContext

from .database import db
from .model_types import ChoiceType

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

association_table = db.Table(
    "users_chats",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("chat_id", db.Integer, db.ForeignKey("chats.id")),
)


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    registered = db.Column(db.DateTime(), default=datetime.utcnow)
    messages = db.relationship("Message", backref="sender")

    def __init__(self, email, password):
        self.email = email
        self.password = pwd_context.hash(password)

    def __repr__(self):
        return f"{self.email}"

    def check_password(self, password):
        return pwd_context.verify(password, self.password)


class Chat(db.Model):
    __tablename__ = "chats"
    id = db.Column(db.Integer, primary_key=True)
    messages = db.relationship("Message", backref="chat")
    users = db.relationship("User", secondary=association_table, backref="chats")
    chat_type = db.Column(ChoiceType({"pm": "pm", "cn": "cn"}))

    def __init__(self, chat_type):
        self.chat_type = chat_type


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    chat_id = db.Column(db.Integer, db.ForeignKey("chats.id"))
    text = db.Column(db.String(500), nullable=False)
    sent = db.Column(db.DateTime(), default=datetime.utcnow)

    def __init__(self, sender_id, text, chat):
        if chat:
            self.chat_id = chat
        self.sender_id = sender_id
        self.text = text

    def as_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "sent": str(self.sent),
            "sender": self.sender.email,
        }
