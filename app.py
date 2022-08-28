from flask import Flask, jsonify, request
from flask_restful import Api
from DBHandler import DBHandler
from decouple import config
import traceback
import bcrypt
import uuid
import jwt
from datetime import datetime, timedelta, timezone

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
            return jsonify({"username taken": True}), 200
    except Exception:
        traceback.print_exc()
        return jsonify({"message": "internal server error"}), 500
    try:
        db.register_user(username, bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()), str(uuid.uuid4()))
    except Exception:
        traceback.print_exc()
        return jsonify({"message": "registering a user into database failed"}), 500
    return jsonify({"username taken": False}), 200

@app.route("/login", methods=["POST"])
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
            token = jwt.encode({
                "username": username,
                "userUuid": user_dets["uuid"],
                "exp": str(int(datetime.timestamp(datetime.now(timezone.utc) + timedelta(minutes=15))))
            }, config("JWT_SECRET_KEY"), algorithm="HS512")
            return jsonify({"bad creds": False, "token": token})
        else:
            return jsonify({"bad creds": True}), 200 # wrong password
    return jsonify({"bad creds": True}), 200    # unknown username

@app.route("/postItem", methods=["POST"])
def post_item():
    try:
        token = request.headers["token"]
        title = request.headers["title"]
        contact_info = request.headers["contact_info"]
    except KeyError:
        return jsonify({"missing required headers": True}), 400
    except Exception:
        return jsonify({"invernal server error": True}), 500
    try:
        descr = request.headers["descr"]
    except KeyError:
        descr = None
    try:
        price = request.headers["price"]
    except KeyError:
        price = None
    except Exception:
        return jsonify({"internal server error": True}), 500
    try:
        jwt_data = jwt.decode(token, config("JWT_SECRET_KEY"), algorithms=["HS512"])
    except jwt.exceptions.InvalidTokenError:
        traceback.print_exc()
        return jsonify({"bad jwt": True}), 200
    except Exception:
        traceback.print_exc()
        return jsonify({"internal server error": True}), 500
    try:
        db.post_item(title, jwt_data["username"], str(uuid.uuid4()), jwt_data["userUuid"], descr, price, contact_info)
        return "", 204  # SUCCESS
    except Exception:
        traceback.print_exc()
        return jsonify({"internal server error": True}), 500

@app.route("/editProfile", methods=["POST"])
def edit_profile():
    currName = request.headers["currentUsername"]   # never None
    currPw = request.headers["currentPw"]   # never None
    try:
        newPw = request.headers["newPw"]
    except KeyError:
        newPw = None
    try:
        newUsername = request.headers["newUsername"]
    except KeyError:
        newUsername = None
    try:
        user_details = db.get_user_details(currName)
        if bcrypt.checkpw(currPw.encode("utf-8"), user_details["hashed_pw"]):
            if newUsername in db.get_all_usernames():
                return jsonify({"username taken": True, "wrong password": False})
            db.update_user_info(user_details["uuid"], newUsername, newPw)
            return "", 204 # SUCCESS
        else:
            return jsonify({"wrong password": True, "username taken": False})
    except Exception:
        traceback.print_exc()
        raise

@app.route("/editItem", methods=["POST"])
def edit_item():
    token = request.headers["token"]
    item_uuid = request.headers["item_uuid"]
    title = request.headers["title"]
    contact_info = request.headers["contact_info"]
    try:
        descr = request.headers["descr"]
    except KeyError:
        descr = None
    try:
        price = request.headers["price"]
    except KeyError:
        price = None
    try:
        jwt_data = jwt.decode(token, config("JWT_SECRET_KEY"), algorithms=["HS512"])
    except jwt.exceptions.InvalidTokenError:
        traceback.print_exc()
        return jsonify({"bad jwt": True})
    seller_uuid = db.get_seller_uuid_of_item(item_uuid)
    if seller_uuid:
        if (jwt_data["userUuid"] == seller_uuid):
            db.edit_item(item_uuid, title, descr, price, contact_info)
            return ("", 204)    # SUCCESS
        return ({"uuid mismatch": True})
    return ({"item missing": True}, 400)

@app.route("/deleteItem", methods=["DELETE"])
def delete_item():
    token = request.headers["token"]
    item_uuid = request.headers["uuid"]
    try:
        jwt_data = jwt.decode(token, config("JWT_SECRET_KEY"), algorithms=["HS512"])
    except jwt.exceptions.InvalidTokenError:
        traceback.print_exc()
        return jsonify({"bad jwt": True})
    seller_uuid = db.get_seller_uuid_of_item(item_uuid)
    if seller_uuid:
        if (jwt_data["userUuid"] == seller_uuid):
            db.delete_item(item_uuid)
            return ("", 204) # SUCCESS
        else:
            return ({"uuid mismatch": True}, 400)
    return ({"item missing": True}, 400)

@app.route("/deleteUser", methods=["DELETE"])
def delete_user():
    username = request.headers["username"]
    password = request.headers["password"]
    user_dets = db.get_user_details(username)
    if not bcrypt.checkpw(password.encode("utf-8"), user_dets["hashed_pw"]):
        return ({"wrong password": True, "username taken": False})
    db.delete_user_and_their_listings(user_dets["uuid"])
    return ("", 204)    # SUCCESS

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, ssl_context=("certs/cert.pem", "certs/key.pem"))