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

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(200), nullable=False)
    large_image = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


with app.app_context():
    db.create_all()
    if not Item.query.first():
        items = [
            Item(name='Pringles Can', image='pringles_small.jpg', large_image='pringles_large.jpg', price=3.99, description='A can of crispy Pringles chips.'),
            Item(name='Glove', image='glove_small.jpg', large_image='glove_large.jpg', price=7.99, description='A single durable work glove.'),
            Item(name='Sponges', image='sponges_small.jpg', large_image='sponges_large.jpg', price=5.99, description='A pack of three cleaning sponges.')
        ]
        db.session.bulk_save_objects(items)
        db.session.commit()

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

@app.route("/login/", methods=["POST"])
def login_post():
    username = request.form["username"]
    password = request.form["password"]
    
    user = User.query.filter_by(username=username, password=password).first()

    if user:
        return redirect(url_for("items_sum_page"))



@app.route("/items_sum_page/", methods=["GET"])
def item_sum_page():
    return render_template("items_sum_page.html")




