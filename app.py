from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from threading import Lock
import os
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()

app = Flask(__name__)

# --- Database Configuration ---
db_user = os.environ.get('DB_USER', 'inventory_user')
db_password = os.environ.get('DB_PASSWORD', 'inventory_pass')
db_host = os.environ.get('DB_HOST', '127.0.0.1')  # Change if needed
db_name = os.environ.get('DB_NAME', 'inventory_db')

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
order_lock = Lock()

# --- Database Models ---
class Product(db.Model):
    __tablename__ = 'Products'
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)

class Order(db.Model):
    __tablename__ = 'Orders'
    order_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    order_date = db.Column(db.DateTime, server_default=db.func.now())
    status = db.Column(db.String(50), nullable=False)
    items = db.relationship('OrderItem', backref='order', cascade="all, delete-orphan")

class OrderItem(db.Model):
    __tablename__ = 'Order_Items'
    order_item_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('Orders.order_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('Products.product_id'))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

# --- Routes ---

@app.route('/')
def index():
    return "Hello, Inventory Management System!"

@app.route('/add_product', methods=['POST'])
def add_product():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400
    try:
        product = Product(
            name=data.get('name'),
            description=data.get('description', ''),
            price=data.get('price'),
            stock_quantity=data.get('stock_quantity')
        )
        db.session.add(product)
        db.session.commit()
        return jsonify({"message": "Product added", "product_id": product.product_id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/place_order', methods=['POST'])
def place_order():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400
    customer_id = data.get('customer_id')
    items = data.get('items')  # Expected to be a list of {"product_id": ..., "quantity": ...}
    if not customer_id or not items:
        return jsonify({"error": "Missing customer_id or items"}), 400
    with order_lock:
        try:
            order = Order(customer_id=customer_id, status="Processing")
            db.session.add(order)
            db.session.flush()  # Ensure order_id is available

            for item in items:
                product_id = item.get('product_id')
                quantity = item.get('quantity')
                product = Product.query.filter_by(product_id=product_id).with_for_update().first()
                if product and product.stock_quantity >= quantity:
                    product.stock_quantity -= quantity
                    order_item = OrderItem(
                        order_id=order.order_id,
                        product_id=product_id,
                        quantity=quantity,
                        price=product.price
                    )
                    db.session.add(order_item)
                else:
                    db.session.rollback()
                    return jsonify({"error": f"Insufficient stock for product {product_id}"}), 400

            order.status = "Completed"
            db.session.commit()
            return jsonify({"message": "Order placed", "order_id": order.order_id}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

@app.route('/report', methods=['GET'])
def report():
    try:
        products = Product.query.all()
        orders = Order.query.all()
        product_list = [
            {"product_id": p.product_id, "name": p.name, "stock_quantity": p.stock_quantity}
            for p in products
        ]
        order_list = [
            {"order_id": o.order_id, "customer_id": o.customer_id, "status": o.status, "order_date": o.order_date}
            for o in orders
        ]
        return jsonify({"products": product_list, "orders": order_list}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Uncomment the following lines to create/update tables on first run:
    # with app.app_context():
    #     db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
