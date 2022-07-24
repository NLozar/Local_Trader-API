from flask import Flask, Response, jsonify
from flask_restful import Api
from DBHandler import DBHandler
from decouple import config
import traceback
import json

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, ssl_context=("certs/cert.pem", "certs/key.pem"))