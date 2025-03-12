from flask import Flask, render_template, request, session, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
import os 

app = Flask(__name__)
app.secret_key = r'spe[vzsflm\;SERvsbsdsvgh,;s;scb'

db_name = 'test.db'
sqlite_uri = f'sqlite:///{os.path.abspath(db_name)}'
app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

try:
    from models import User
except ImportError:
    pass  

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(200), nullable=False)
    large_image = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)

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
    allowed_routes = ["login", "register", "static"]
    if "user" not in session and request.endpoint not in allowed_routes:
        return redirect(url_for("login"))

@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        users = User.query.all()  
        login_success = any(user.username == username and user.password == password for user in users)

        if login_success:
            session["username"] = username
            return redirect(url_for("item_sum_page"))
        else:
            return render_template("login.html", message="Wrong username/password")
    
    return render_template("login.html")

@app.route("/register/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["new_username"]
        if User.query.filter_by(username=username).first():
            return render_template("register.html", message="Username already taken.")
        return redirect(url_for("login"))
    
    return render_template("register.html")

@app.route("/items_sum_page/")
def item_sum_page():
    items = Item.query.all()
    return render_template("items_sum_page.html", items=items)

@app.route("/cart/", methods=["GET", "POST"])
def shopping_cart():
    if request.method == "POST":
        item_id = request.form.get("item_id")
        cart = session.get("cart", [])
        cart.append(item_id)
        session["cart"] = cart
        return redirect(url_for("shopping_cart"))
    
    cart = session.get("cart", [])
    items = Item.query.filter(Item.id.in_(cart)).all()
    return render_template("cart.html", cart=items)

@app.route("/add_to_cart/<int:item_id>/", methods=["POST"])
def add_to_cart(item_id):
    cart = session.get("cart", [])
    cart.append(item_id)
    session["cart"] = cart
    return redirect(url_for("shopping_cart"))

@app.route("/checkout/", methods=["GET", "POST"])
def checkout():
    if request.method == "POST":
        cart = session.get('cart', [])
        email = request.form.get('email')
        ccn = request.form.get('ccn')

        with open("orders.txt", 'a') as order_file:
            order_file.write(f"Order by {email}\n")
            for item_id in cart:
                order_file.write(f"Item ID: {item_id}\n")
            order_file.write(f"Credit Card: {ccn}\n\n")

        session["cart"] = []
        return render_template("checkout.html", message="Your items are on the way!")
    
    return render_template("checkout.html")

@app.route("/orders/")
def orders():
    try:
        with open("orders.txt", "r") as orders_file:
            content = orders_file.readlines()
        return render_template("orders.html", message=content)
    except FileNotFoundError:
        return render_template("orders.html", message="No orders found.")

if __name__ == "__main__":
    app.run(debug=True)

