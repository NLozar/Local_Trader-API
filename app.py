from flask import Flask, jsonify, request
from flask_restful import Api
from DBHandler import DBHandler
from decouple import config
import traceback
import bcrypt
import uuid

PORT = 14443

db = DBHandler("root", config("MYSQL_PW"), "localhost", 13306, "local_trader")

app = Flask("local_trader_API")
api = Api(app)

@app.route("/itemsList", methods=["GET"])
def get_items_list():
    try:
        all_items = db.get_all_items()
    except Exception:
        traceback.print_exc()
        return jsonify({"message": "internal server error"}), 500
    return jsonify(all_items)

@app.route("/itemDetails/<uuid>", methods=["GET"])
def get_item_details(uuid):
    try:
        details = db.get_item_details(uuid)
        if not details:
            return jsonify({"message": "item uuid invalid"}), 400
    except Exception:
        traceback.print_exc()
        return jsonify({"message": "internal server error"}), 500
    return jsonify(details)

@app.route("/registerUser", methods=["POST"])
def register_user():
    try:
        username = request.headers["username"]
        password = request.headers["password"]
    except KeyError:
        return jsonify({"message": "username or password retrival failed"}), 400
    except Exception:
        traceback.print_exc()
        return jsonify({"message": "internal server error"}), 500
    try:
        usernames = db.get_all_usernames()
        if username in usernames:
            return jsonify({"message": f"Username '{username}' is already taken."}), 409
    except Exception:
        traceback.print_exc()
        return jsonify({"message": "internal server error"}), 500
    try:
        db.register_user(username, bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()), str(uuid.uuid4()))
    except Exception:
        traceback.print_exc()
        return jsonify({"message": "registering a user into database failed"}), 500
    return jsonify({"message": "User registered"}), 204

@app.route("/logUserIn", methods=["GET"])
def log_user_in():
    try:
        username = request.headers["username"]
        password = request.headers["password"]
    except KeyError:
        return jsonify({"message": "username or password retrival failed"}), 400
    except Exception:
        traceback.print_exc()
        return jsonify({"message": "internal server error"}), 500
    try:
        usernames = db.get_all_usernames()
    except Exception:
        traceback.print_exc()
        return jsonify({"message": "internal server error"}), 500
    if username in usernames:
        user_dets = db.get_user_details(username)
        if bcrypt.checkpw(password.encode("utf-8"), user_dets["hashed_pw"]):
            # TODO
            return jsonify({"msg": "good login"})
        else:
            return jsonify({"message": "bad creds"}), 404
    return jsonify({"message": "bad creds"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, ssl_context=("certs/cert.pem", "certs/key.pem"))