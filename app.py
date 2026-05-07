from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

BASE_URL = "https://collectibles-backend-hcey.onrender.com"

users = []
products = []


@app.route("/")
def home():
    return "API работает 🚀"


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


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

    if any(u["email"] == email for u in users):
        return jsonify({"error": "Пользователь уже существует"}), 400

    user = {
        "id": len(users) + 1,
        "username": username,
        "email": email,
        "password": password
    }

    users.append(user)
    return jsonify({"message": "OK"})


@app.route("/login", methods=["POST"])
def login():
    data = request.json

    if not data:
        return jsonify({"error": "Нет данных"}), 400

    email = data.get("email")
    password = data.get("password")

    for user in users:
        if user["email"] == email and user["password"] == password:
            return jsonify({"user": user})

    return jsonify({"error": "Неверные данные"}), 401


@app.route("/products", methods=["GET"])
def get_products():
    return jsonify(products)


@app.route("/products", methods=["POST"])
def add_product():
    name = request.form.get("name")
    description = request.form.get("description")
    price = request.form.get("price")
    seller_id = request.form.get("seller_id")
    category = request.form.get("category")

    image_url = ""

    file = request.files.get("image")

    if file and file.filename:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        image_url = f"{BASE_URL}/uploads/{filename}"

    product = {
        "id": len(products) + 1,
        "name": name,
        "description": description,
        "price": price,
        "seller": seller_id,
        "category": category,
        "image_url": image_url
    }

    products.append(product)
    return jsonify({"message": "OK", "product": product})


@app.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    global products
    products = [p for p in products if p["id"] != id]
    return jsonify({"message": "Удалено"})


if __name__ == "__main__":
    app.run(debug=True)