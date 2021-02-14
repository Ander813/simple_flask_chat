from datetime import datetime

from .database import db


association_table = db.Table(
    "users_chats",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("chat_id", db.Integer, db.ForeignKey("chats.id")),
)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    registered = db.Column(db.DateTime(), default=datetime.utcnow)
    chats = db.relationship("Chat", secondary=association_table, back_populates="users")
    messages = db.relationship("Message", backref="sender")


class Chat(db.Model):
    __tablename__ = "chats"
    id = db.Column(db.Integer, primary_key=True)
    messages = db.relationship("Message", backref="chat")
    users = db.relationship("User", secondary=association_table, back_populates="chats")


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    text = db.Column(db.String(500), nullable=False)
    sent = db.Column(db.DateTime(), default=datetime.utcnow)
