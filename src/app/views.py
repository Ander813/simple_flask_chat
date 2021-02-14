from flask import Blueprint, render_template

chat = Blueprint("chat", __name__, template_folder="templates")


@chat.route("/", methods=["GET"])
def index():
    return render_template("index.html")
