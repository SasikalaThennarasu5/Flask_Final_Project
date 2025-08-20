from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# ====================
# MODELS
# ====================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, default=1)

    product = db.relationship("Product")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ====================
# API ROUTES
# ====================

# ✅ API: Get all products
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # handle login logic here
        return redirect(url_for("home"))
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Example: collect data from form
        username = request.form["username"]
        password = request.form["password"]

        # TODO: Add user saving logic here (with hashing)
        flash("Signup successful! Please log in.")
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/api/products", methods=["GET"])
def api_get_products():
    products = Product.query.all()
    return jsonify([{"id": p.id, "name": p.name, "price": p.price} for p in products])

# ✅ API: Add product
@app.route("/api/products", methods=["POST"])
def api_add_product():
    data = request.json
    if not data.get("name") or not data.get("price"):
        return jsonify({"error": "Missing fields"}), 400
    product = Product(name=data["name"], price=float(data["price"]))
    db.session.add(product)
    db.session.commit()
    return jsonify({"message": "Product added", "id": product.id})

# ✅ API: Update product
@app.route("/api/products/<int:id>", methods=["PUT"])
def api_update_product(id):
    product = Product.query.get_or_404(id)
    data = request.json
    product.name = data.get("name", product.name)
    product.price = data.get("price", product.price)
    db.session.commit()
    return jsonify({"message": "Product updated"})

# ✅ API: Delete product
@app.route("/api/products/<int:id>", methods=["DELETE"])
def api_delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"})

# ✅ API: Get user cart
@app.route("/api/cart", methods=["GET"])
@login_required
def api_get_cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        "id": item.id,
        "product": item.product.name,
        "price": item.product.price,
        "quantity": item.quantity
    } for item in cart_items])

# ✅ API: Add to cart
@app.route("/api/cart", methods=["POST"])
@login_required
def api_add_cart():
    data = request.json
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)
    if not product_id:
        return jsonify({"error": "Product ID required"}), 400

    cart_item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()
    return jsonify({"message": "Item added to cart"})

# ✅ API: Remove item from cart
@app.route("/api/cart/<int:id>", methods=["DELETE"])
@login_required
def api_remove_cart(id):
    cart_item = CartItem.query.get_or_404(id)
    if cart_item.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403
    db.session.delete(cart_item)
    db.session.commit()
    return jsonify({"message": "Item removed"})

# ✅ API: Clear cart
@app.route("/api/cart/clear", methods=["DELETE"])
@login_required
def api_clear_cart():
    CartItem.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return jsonify({"message": "Cart cleared"})

@app.route("/")
def home():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)
