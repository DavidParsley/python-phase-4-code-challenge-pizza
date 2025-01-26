#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# Fetch all restaurants
@app.route("/restaurants", methods=["GET"])
def fetch_restaurants():
    restaurants = Restaurant.query.all()
    restaurant_list = []

    for restaurant in restaurants:
        restaurant_list.append(restaurant.to_dict(only=("id", "name", "address")))

    return jsonify(restaurant_list)

# Fetch a single restaurant
@app.route("/restaurants/<int:id>", methods=["GET"])
def fetch_restaurant(id):
    restaurant = Restaurant.query.get(id)
    restaurant_pizza = RestaurantPizza.query.filter(RestaurantPizza.restaurant_id==id).all()
    
    if restaurant:
        restaurant_data = {
            "address": restaurant.address,
            "id": restaurant.id,
            "name": restaurant.name,
            "restaurant_pizza": []
        }

        for rp in restaurant_pizza:
            pizza = rp.pizza
            restaurant_data["restaurant_pizza"].append({
                "id": rp.id,
                "pizza": {
                    "id": pizza.id,
                    "ingredients": pizza.ingredients,
                    "name": pizza.name
                },
                "pizza_id": rp.pizza_id,
                "price": rp.price,
                "restaurant_id": rp.restaurant_id
            })
        return jsonify(restaurant_data), 200
    
    return jsonify({ "error": "Restaurant not found"}), 404

# Delete a restaurant
@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)

    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return '', 200
    
    return jsonify({"error": "Restaurant not found"}), 404

# Fetch all restaurants
@app.route("/pizzas", methods=["GET"])
def fetch_pizzas():
    pizzas = Pizza.query.all()
    pizza_list = []

    for pizza in pizzas:
        pizza_list.append(pizza.to_dict(only=("id", "ingredients", "name")))

    return jsonify(pizza_list)

# Create a new RestaurantPizza
@app.route("/restaurant_pizzas", methods=["POST"])
def add_restaurant_pizzas():

    data = request.get_json()
    price = data["price"]
    pizza_id = data["pizza_id"]
    restaurant_id = data["restaurant_id"]

    check_pizza_id = Pizza.query.get(pizza_id)
    check_restaurant_id = Restaurant.query.get(restaurant_id)

    if not check_pizza_id:
        return jsonify({"errors": ["Pizza not found"]}), 404

    if not check_restaurant_id:
        return jsonify({"errors": ["Restaurant not found"]}), 404

    new_restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)
    db.session.add(new_restaurant_pizza)
    db.session.commit()
    if new_restaurant_pizza:
        return jsonify(new_restaurant_pizza.to_dict()), 201
    else:
        return jsonify({ "errors": ["validation errors"]})

if __name__ == "__main__":
    app.run(port=5555, debug=True)
