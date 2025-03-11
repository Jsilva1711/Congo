from flask import Flask, render_template, request, session, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
import os 

app = Flask(__name__)
app.secret_key = 'REPLACE_ME_WITH_RANDOM_CHARACTERS'

db_name = 'test.db'
sqlite_uri = f'sqlite:///{os.path.abspath(os.path.curdir)}/{db_name}'
app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import User

with app.app_context():
    db.create_all()

@app.before_request
def check_login():
    if "user" not in session and request.path != url_for("login"):
        return redirect(url_for("login"))
    else:
        return redirect(url_for("items_sum_page"))

@app.route("/login/", methods=["GET"])
def login():
    return render_template("login.html")

@app.route("/login/", methods=["POST"])
def do_login():
    username = request.form["username"]
    password = request.form["password"]
    users = get_users()
    login = False
    for user in users:
        if user.username == username and user.password == password:
            session["username"] = username
            login = True
            break
    if login:
        return redirect(url_for("item_sum_page.html"))
    else:
        return render_template("login.html", message="Wrong username/password")

@app.route("/register/", methods=["GET"])
def register():
    return render_template("register.html")


@app.route("/items_sum_page/", methods=["GET"])
def item_sum_page():
    return render_template("items_sum_page.html")




