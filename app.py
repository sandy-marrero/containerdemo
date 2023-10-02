from flask import Flask, jsonify
import Adafruit_DHT

app = Flask(__name__)

# Sensor configuration
sensor = Adafruit_DHT.DHT11  # Use the DHT11 sensor
pin = 4  # GPIO pin where the sensor is connected


@app.route("/temperature", methods=["GET"])
def get_temperature():
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

    if humidity is not None and temperature is not None:
        data = {"temperature": temperature, "humidity": humidity}
        return jsonify(data), 200
    else:
        return "Failed to read sensor data.", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
