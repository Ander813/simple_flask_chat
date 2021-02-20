from flask import Blueprint, render_template, request, Response
from flask_login import login_user
from sqlalchemy.exc import IntegrityError

from src.app.database import db
from src.app.forms import RegisterForm, LoginForm
from src.app.models import User

chat = Blueprint("chat", __name__, template_folder="templates")


@chat.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@chat.route("/login", methods=["GET", "POST"])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.email).first()
        if user:
            if user.check_password(form.password1):
                login_user(user)
        else:
            return Response("Invalid credentials", status=401)
    return render_template("login.html", form=form)


@chat.route("/register", methods=["GET", "POST"])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            db.session.add(User(name=form.email.data, password=form.password1.data))
            db.session.commit()
        except IntegrityError as e:
            return Response("User with such email already exists", 400)
    return render_template("register.html", form=form)
