from flask import Flask, render_template, request, session, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = r'spe[vzsflm\;SERvsbsdsvgh,;s;scb'

# Database setup
db_name = 'test.db'
sqlite_uri = f'sqlite:///{os.path.join(os.getcwd(), db_name)}'
app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Plain text password

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(200), nullable=False)
    large_image = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)

# Initialize database
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

# Before request authentication check
@app.before_request
def check_login():
    if "user" not in session and request.endpoint not in ["login", "register", "static"]:
        return redirect(url_for("login"))

# Routes
@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:  # Check plain text password
            session["user"] = username
            return redirect(url_for("item_sum_page"))
        else:
            return render_template("login.html", message="Wrong username/password")
    return render_template("login.html")

@app.route("/register/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["new_username"]
        password = request.form["new_password"]

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template("register.html", message="Username already taken.")

        new_user = User(username=username, password=password)  # Store plain text password
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))

    return render_template("register.html", message=None)

@app.route("/items_sum_page/", methods=["GET"])
def item_sum_page():
    items = Item.query.all()
    return render_template("items_sum_page.html", items=items)

@app.route("/item/<int:item_id>/", methods=["GET"])
def item_detail(item_id):
    item = Item.query.get(item_id)
    if item:
        return render_template("item_detail.html", item=item)
    else:
        return redirect(url_for("item_sum_page"))


@app.route("/cart/", methods=["GET", "POST"])
def shopping_cart():
    if request.method == "POST":
        item_id = request.form.get("item_id")
        cart = session.get("cart", {})
        cart[item_id] = cart.get(item_id, 0) + 1
        session["cart"] = cart
        return redirect(url_for("shopping_cart"))

    cart = session.get("cart", {})
    items_dict = {str(item.id): item for item in Item.query.all()}
    return render_template("cart.html", cart=cart, items_dict=items_dict)

@app.route("/add_to_cart/<int:item_id>/", methods=["POST"])
def add_to_cart(item_id):
    cart = session.get("cart", {})
    cart[str(item_id)] = cart.get(str(item_id), 0) + 1
    session["cart"] = cart
    return redirect(url_for("shopping_cart"))

@app.route("/checkout/", methods=["GET", "POST"])
def checkout():
    if request.method == "POST":
        cart = session.get("cart", {})
        email = request.form['email']
        ccn = request.form['ccn']
        
        with open("orders.txt", 'a') as order_file:
            for item_id, quantity in cart.items():
                item = Item.query.get(int(item_id))
                order_file.write(f"{item.name} : {quantity}\n")
            order_file.write(f"Email: {email}\n")
            order_file.write(f"Credit Card Number: {ccn}\n\n")
        
        session["cart"] = {}  # Clear cart
        return render_template("checkout.html", message="Your items are on the way!")

    return render_template("checkout.html")

@app.route("/orders/", methods=["GET"])
def orders():
    with open("orders.txt", "r") as orders_file:
        content = orders_file.readlines()
    return render_template("orders.html", message=content)

# Run app
if __name__ == "__main__":
    app.run(debug=True)
