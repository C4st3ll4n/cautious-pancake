from flask import Blueprint, request, jsonify, make_response
import requests

from models import Order, OrderItem, db

order_blueprint = Blueprint('order_api_routes', __name__, url_prefix="/api/v1/order")
USER_API_URL = "http://user-service-c:5001/api/v1/user/me"


def get_user(api_key):
    headers = {
        "Authorization": api_key
    }

    response = requests.get(USER_API_URL, headers=headers)
    if response.status_code != 200:
        return {"message": "Not Authorized"}

    user = response.json()
    return user


@order_blueprint.route("/", methods=["GET"])
def get_order():
    api_key = request.headers.get("Authorization")
    if not api_key:
        return make_response(jsonify({
            "message": "Not logged in"
        }), 401)

    response = get_user(api_key)
    user = response.get("user")
    if not user:
        return make_response(jsonify({
            "message": "Not logged in"
        }), 401)

    open_order = Order.query.filter_by(user_id=user['id'], is_open=1).first()
    if open_order:
        return make_response(jsonify({
            "order": open_order.serialize()
        }), 200)
    else:
        return make_response(jsonify({
            "message": "No open orders"
        }), 404)


@order_blueprint.route("/all", methods=["GET"])
def all_order():
    orders = Order.query.all()
    all_orders = [o.serialize() for o in orders]
    return make_response(
        jsonify(
            {
                "orders": all_orders
            }
        ), 200
    )


@order_blueprint.route("/", methods=["POST"])
def add_item():
    api_key = request.headers.get("Authorization")
    if not api_key:
        return make_response(jsonify({
            "message": "Not logged in"
        }), 401)

    response = get_user(api_key)
    user = response.get("user")

    if not user:
        return make_response(jsonify({
            "message": "Not logged in"
        }), 401)

    book_id = int(request.form['book'])
    quantity = int(request.form['quantity'])
    user_id = user['id']

    open_order = Order.query.filter_by(user_id=user_id, is_open=1).first()
    if not open_order:
        open_order = Order()
        open_order.is_open = True
        open_order.user_id = user_id

        order_item = OrderItem(book_id, quantity)
        open_order.order_itens.append(order_item)
    else:
        found = False
        for i in open_order.order_itens:
            if i.book_id == book_id:
                i.quantity += quantity
                found = True

        if not found:
            order_item = OrderItem(book_id, quantity)
            open_order.order_itens.append(order_item)

    db.session.add(open_order)
    db.session.commit()
    print(open_order.serialize())
    return make_response(
        jsonify({
            "order": open_order.serialize()
        })
    )


@order_blueprint.route("/checkout", methods=["POST"])
def checkout():
    api_key = request.headers.get("Authorization")
    if not api_key:
        return make_response(jsonify({
            "message": "Not logged in"
        }), 401)

    response = get_user(api_key)
    user = response.get("user")
    if not user:
        return make_response(jsonify({
            "message": "Not logged in"
        }), 401)

    open_order = Order.query.filter_by(user_id=user['id'], is_open=1).first()
    if open_order:
        open_order.is_open = False

        db.session.add(open_order)
        db.session.commit()

        return make_response(jsonify({
            "order": open_order.serialize()
        }))

    else:

        return make_response(jsonify({
            "message": "No order found"
        }))
