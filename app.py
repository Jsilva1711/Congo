from flask import Flask, render_template, request, session, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
import os 

app = Flask(__name__)
app.secret_key = 'spe[vzsflm\;SERvsbsdsvgh,;s;scb'

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
            Item(name='Pringles Can', image='static/img/pringles_small.jpg', large_image='static/img/pringles_large.jpg', price=3.99, description='A can of crispy Pringles chips.'),
            Item(name='Glove', image='static/img/glove_small.jpg', large_image='static/img/glove_large.jpg', price=7.99, description='A single durable work glove.'),
            Item(name='Sponges', image='static/img/sponges_small.jpg', large_image='static/img/sponges_large.jpg', price=5.99, description='A pack of three cleaning sponges.')
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
    username = request.args.get("username")
    if username:
        existing_user = User.query.filter_by(username).first()
        if existing_user:
            return render_template("register.html", message="Username already taken.")
    return render_template("register.html")


@app.route("/items_sum_page/", methods=["GET"])
def item_sum_page():
    return render_template("items_sum_page.html")

@app.route("/cart/", methods=["GET", "POST"])
def shopping_cart():
    if request.method == "POST":
        item_id =requestform.get("item_id")
        cart = session.get("cart", [])
        cart.append(item_id)
        session["cart"] = cart
        return redirect(url_for("shopping_cart"))
    
    cart = session.get("cart", [])
    items = Item.query.fillter(Item.id.in_(cart)).all()
    return render_template("cart.html", cart=items)

@app.route("/add_to_cart/<int:item_id>/", methods=["POST"])
def add_to_cart(item_id):
    cart = session.get("cart", [])
    cart.append(item_id)
    session["cart"] = cart
    return redirect(url_for("Shopping_cart"))

@app.route("/checkout/", methods=["GET, POST"])
def checkout():
    if request.method == "GET":
        return render_template("checkout.html")
    elif rewuest.method == "POST":
        cart = session['cart']
        email = request.form['email']
        ccn = request.form['ccn']
        with open("orders.txt", 'a') as order:
            for key, value in cart.items():
                order.write(f"{key.title()} : {value}\n")
            order.write("Email: " + email + '\n')
            order.write("Credit Card Number: " + ccn + '\n' + '\n')
        session["cart"] = session["cart"].clear()
        return render_template("checkout.html", message="Your items are on the way!")


@app.route("/orders/", methods=["GET"])
def orders():
    with open("orders.txt", "r") as orders:
        content = orders.readlines()
    return render_template("orders.html", message=content)



    





