from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

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

    if any(u["email"] == data["email"] for u in users):
        return jsonify({"error": "Пользователь уже существует"})

    user = {
        "id": len(users) + 1,
        "username": data["username"],
        "email": data["email"],
        "password": data["password"]
    }

    users.append(user)
    return jsonify({"message": "OK"})


@app.route("/login", methods=["POST"])
def login():
    data = request.json

    for user in users:
        if user["email"] == data["email"] and user["password"] == data["password"]:
            return jsonify({"user": user})

    return jsonify({"error": "Неверные данные"})


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

    file = request.files.get("image")
    image_url = ""

    if file:
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(filepath)
        image_url = f"http://127.0.0.1:5000/uploads/{file.filename}"

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
    return jsonify({"message": "OK"})


@app.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    global products
    products = [p for p in products if p["id"] != id]
    return jsonify({"message": "Удалено"})


if __name__ == "__main__":
    app.run(debug=True)