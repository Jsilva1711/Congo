from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  


db_name = 'test.db'
sqlite_uri = f'sqlite:///{os.path.join(os.getcwd(), db_name)}'
app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    ccn = db.Column(db.String(16), nullable=True)

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
            Item(name='Pringles Can', image='img/Pringles_Can.jpg', large_image='img/Pringles_Can.jpg', price=3.99, description='A can of crispy Pringles chips.'),
            Item(name='Glove', image='img/glove.jpg', large_image='img/glove.jpg', price=7.99, description='A single durable work glove.'),
            Item(name='Sponges', image='img/sponges.jpg', large_image='img/sponges.jpg', price=5.99, description='A pack of three cleaning sponges.')
        ]
        db.session.bulk_save_objects(items)
        db.session.commit()


@app.route("/")
def home():
    return render_template("login.html")

@app.before_request
def check_login():
    allowed_routes = ["login", "register", "static", "item_sum_page", "item_detail"]
    if "user" not in session and request.endpoint not in allowed_routes:
        return redirect(url_for("login"))

@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:  
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
        email = request.form["email"]
        ccn = request.form["ccn"]  

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template("register.html", message="Username already taken.")

        new_user = User(username=username, password=password, email=email, ccn=ccn)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))

    return render_template("register.html", message=None)

@app.route("/logout")
def logout():
    session.pop('user', None)  
    return redirect(url_for('login'))

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
    user = User.query.filter_by(username=session["user"]).first()
    if request.method == "POST":
        item_id = request.form.get("item_id")
        cart = session.get("cart", {})
        cart[item_id] = cart.get(item_id, 0) + 1
        session["cart"] = cart
        return redirect(url_for("shopping_cart"))

    cart = session.get("cart", {})
    items_dict = {str(item.id): item for item in Item.query.all()}

    
    cart_items = [
        {
            "item": items_dict.get(item_id),
            "quantity": quantity
        }
        for item_id, quantity in cart.items()
    ]

    return render_template("cart.html", cart=cart_items, user=user)
@app.route("/add_to_cart/<int:item_id>/", methods=["POST"])
def add_to_cart(item_id):
    cart = session.get("cart", {})
    cart[str(item_id)] = cart.get(str(item_id), 0) + 1
    session["cart"] = cart
    return redirect(url_for("shopping_cart"))

@app.route("/checkout/", methods=["GET", "POST"])
def checkout():
    if 'user' in session:
        user = User.query.filter_by(username=session['user']).first()

        if request.method == "POST":
            email = request.form.get("email")
            ccn = request.form.get("ccn")

            # Update user details if they exist
            if email and ccn:
                user.email = email
                user.ccn = ccn
                db.session.commit()

            cart = session.get("cart", {})
            if not cart:
                return render_template("checkout.html", message="Your cart is empty. Please add items to your cart.", user=user)

            
            with open("orders.txt", 'a') as order_file:
                for item_id, quantity in cart.items():
                    item = Item.query.get(int(item_id))
                    order_file.write(f"{item.name} : {quantity}\n")
                order_file.write(f"Email: {email}\n")
                order_file.write(f"Credit Card Number: {ccn}\n\n")

            session["cart"] = {}  
            return render_template("checkout.html", message="Your items are on the way!", user=user)

        return render_template("checkout.html", user=user)

    return redirect(url_for('login'))

@app.route("/orders/", methods=["GET"])
def orders():
    with open("orders.txt", "r") as orders_file:
        content = orders_file.readlines()
    return render_template("orders.html", message=content)


if __name__ == "__main__":
    app.run(debug=True)

