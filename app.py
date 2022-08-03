from flask import Flask, Response, jsonify, request
from flask_restful import Api
from DBHandler import DBHandler
from decouple import config
import traceback
import json
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
        return Response(json.dumps({"message": "internal server error"}), status=500, mimetype="application/json")
    return jsonify(all_items)

@app.route("/itemDetails/<uuid>", methods=["GET"])
def get_item_details(uuid):
    try:
        details = db.get_item_details(uuid)
        if not details:
            return Response(json.dumps({"message": "item uuid invalid"}), status=400, mimetype="application/json")
    except Exception:
        print(traceback.print_exc())
        return Response(json.dumps({"message": "internal server error"}), status=500, mimetype="application/json")
    return jsonify(details)

@app.route("/registerUser", methods=["POST"])
def register_user():
    try:
        username = request.headers["username"]
        password = request.headers["password"]
    except KeyError:
        return Response(json.dumps({"message": "username or password retrival failed"}), status=400, mimetype="application/json")
    except Exception:
        return Response(json.dumps({"message": "internal server error"}), status=500, mimetype="application/json") 
    try:
        usernames = db.get_all_usernames()
        if username in usernames:
            return Response(json.dumps({"message": f"Username '{username}' is already taken."}), status=409, mimetype="application/json")
    except Exception:
        return Response(json.dumps({"message": "internal server error"}), status=500, mimetype="application/json")
    try:
        db.register_user(username, bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()), str(uuid.uuid4()))
    except Exception:
        return Response(json.dumps({"message": "registering a user into database failed"}), status=500, mimetype="application/json")
    return Response(json.dumps({"message": "User registered"}), status=204, mimetype="application/json")

@app.route("/logUserIn", methods=["GET"])
def log_user_in():
    try:
        username = request.headers["username"]
        password = request.headers["password"]
    except KeyError:
        return Response(json.dumps({"message": "username or password retrival failed"}), status=400, mimetype="application/json")
    except Exception:
        return Response(json.dumps({"message": "internal server error"}), status=500, mimetype="application/json")
    try:
        usernames = db.get_all_usernames()
    except Exception:
        return Response(json.dumps({"message": "internal server error"}), status=500, mimetype="application/json")
    if username in usernames:
        user_dets = db.get_user_details(username)
        if bcrypt.checkpw(password.encode("utf-8"), user_dets["hashed_pw"]):
            # TODO
            return jsonify({"msg": "good login"})
        else:
            return Response(json.dumps({"message": "bad creds"}), status=404, mimetype="application/json")
    return Response(json.dumps({"message": "bad creds"}), status=404, mimetype="application/json")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, ssl_context=("certs/cert.pem", "certs/key.pem"))