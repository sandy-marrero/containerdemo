from flask import Flask, request, jsonify, render_template
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


received_data = []


@app.route("/")
def index():
    return render_template("index.html", data=received_data)


@app.route("/store-data", methods=["POST"])
def store_data():
    try:
        data = request.json
        data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        received_data.append(data)  # Add the received data to the list
        return "Data received and stored successfully.", 200
    except Exception as e:
        return f"Error processing and storing data: {str(e)}", 500


@app.route("/get-data", methods=["GET"])
def get_data():
    return jsonify(received_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
