from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import json

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "sqlite:///collectibles.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

BASE_URL = "https://collectibles-backend-hcey.onrender.com"

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.String(50), nullable=False)
    seller = db.Column(db.String(50))
    category = db.Column(db.String(100))
    image_url = db.Column(db.Text)


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    payment_method = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.Text)
    total = db.Column(db.String(50), nullable=False)
    items = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default="Created")


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return "API работает 🚀 PostgreSQL подключен"


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/register", methods=["POST"])
def register():
    data = request.json

    if not data:
        return jsonify({"error": "Нет данных"}), 400

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Заполните все поля"}), 400

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({"error": "Пользователь уже существует"}), 400

    user = User(username=username, email=email, password=password)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "OK"})


@app.route("/login", methods=["POST"])
def login():
    data = request.json

    if not data:
        return jsonify({"error": "Нет данных"}), 400

    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email, password=password).first()

    if not user:
        return jsonify({"error": "Неверные данные"}), 401

    return jsonify({
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    })


@app.route("/products", methods=["GET"])
def get_products():
    products = Product.query.order_by(Product.id.desc()).all()

    result = []

    for product in products:
        result.append({
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "seller": product.seller,
            "category": product.category,
            "image_url": product.image_url
        })

    return jsonify(result)


@app.route("/products", methods=["POST"])
def add_product():
    name = request.form.get("name")
    description = request.form.get("description")
    price = request.form.get("price")
    seller_id = request.form.get("seller_id")
    category = request.form.get("category")

    if not name or not price:
        return jsonify({"error": "Название и цена обязательны"}), 400

    image_url = ""
    file = request.files.get("image")

    if file and file.filename:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        image_url = f"{BASE_URL}/uploads/{filename}"

    product = Product(
        name=name,
        description=description,
        price=price,
        seller=seller_id,
        category=category,
        image_url=image_url
    )

    db.session.add(product)
    db.session.commit()

    return jsonify({"message": "OK"})


@app.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    product = Product.query.get(id)

    if not product:
        return jsonify({"error": "Товар не найден"}), 404

    db.session.delete(product)
    db.session.commit()

    return jsonify({"message": "Удалено"})


@app.route("/orders", methods=["POST"])
def create_order():
    data = request.json

    if not data:
        return jsonify({"error": "Нет данных"}), 400

    customer_name = data.get("customer_name")
    phone = data.get("phone")
    address = data.get("address")
    payment_method = data.get("payment_method")
    comment = data.get("comment", "")
    total = data.get("total")
    items = data.get("items", [])

    if not customer_name or not phone or not address or not payment_method:
        return jsonify({"error": "Заполните данные заказа"}), 400

    order = Order(
        customer_name=customer_name,
        phone=phone,
        address=address,
        payment_method=payment_method,
        comment=comment,
        total=str(total),
        items=json.dumps(items, ensure_ascii=False),
        status="Paid" if payment_method != "Cash on delivery" else "Created"
    )

    db.session.add(order)
    db.session.commit()

    return jsonify({
        "message": "ORDER_CREATED",
        "order_id": order.id
    })


@app.route("/orders", methods=["GET"])
def get_orders():
    orders = Order.query.order_by(Order.id.desc()).all()

    result = []

    for order in orders:
        result.append({
            "id": order.id,
            "customer_name": order.customer_name,
            "phone": order.phone,
            "address": order.address,
            "payment_method": order.payment_method,
            "comment": order.comment,
            "total": order.total,
            "items": json.loads(order.items),
            "status": order.status
        })

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)