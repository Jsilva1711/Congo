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

@app.route("/login/"), methods=["GET"])
def login():
    return render_template ("login.html")

@app.route("/login/", methods=["POST"])
def login_post():
    username = request.form["username"]
    password = request.form["password"]
    
    user = User.query.filter_by(username=username, password=password).first()

    if user:
        return redirect(url_for("items_sum_page"))



@app.route("/items_sum_page/"), methods=["GET"])
def item_sum_page():
    return render_template("items_sum_page.html")




