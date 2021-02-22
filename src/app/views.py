from flask import Blueprint, render_template, request, Response, redirect, url_for
from flask_login import login_user, login_required, current_user
from sqlalchemy.exc import IntegrityError

from src.app.database import db
from src.app.decorators import logged_in_redirect
from src.app.forms import RegisterForm, LoginForm
from src.app.models import User

chat = Blueprint("chat", __name__, template_folder="templates")


@chat.route("/", methods=["GET"])
@login_required
def index():
    return render_template("index.html")


@chat.route("/login", methods=["GET", "POST"])
@logged_in_redirect("chat.index")
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.email.data).first()
        if user:
            if user.check_password(form.password.data):
                login_user(user)
                return redirect(url_for("chat.index"))
        else:
            return Response("Invalid credentials", status=401)
    return render_template("login.html", form=form)


@chat.route("/register", methods=["GET", "POST"])
@logged_in_redirect("chat.index")
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            db.session.add(User(name=form.email.data, password=form.password1.data))
            db.session.commit()
        except IntegrityError as e:
            return Response("User with such email already exists", 400)
    return render_template("register.html", form=form)
