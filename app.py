from flask import Flask, jsonify
import Adafruit_DHT
import datetime

app = Flask(__name__)

sensor = Adafruit_DHT.DHT11
pin = 4
data_list = []


@app.route("/temperature", methods=["GET"])
def get_temperature():
    humidity, celsius_temperature = Adafruit_DHT.read_retry(sensor, pin)

    if humidity is not None and celsius_temperature is not None:
        fahrenheit_temperature = (celsius_temperature * 9 / 5) + 32

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data_point = {
            "timestamp": timestamp,
            "temperature_C": celsius_temperature,
            "temperature_F": fahrenheit_temperature,
            "humidity": humidity,
        }

        data_list.append(data_point)

        return jsonify(data_point), 200
    else:
        return "Failed to read sensor data.", 500


@app.route("/get-data", methods=["GET"])
def get_data():
    return jsonify(data_list)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
