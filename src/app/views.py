from flask import Blueprint, render_template, request

chat = Blueprint("chat", __name__, template_folder="templates")


@chat.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@chat.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "GET":
        return render_template("login.html")


@chat.route("/register", methods=["GET", "POST"])
def login_page():
    if request.method == "GET":
        return render_template("register.html")
