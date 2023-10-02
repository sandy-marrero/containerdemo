from flask import Flask, jsonify
import Adafruit_DHT
import requests  # Import the requests library

app = Flask(__name__)

# Sensor configuration
sensor = Adafruit_DHT.DHT11
pin = 4
receiver_url = "http://172.17.0.1:5000/store-data"  # Replace with the IP of the receiver Raspberry Pi


@app.route("/temperature", methods=["GET"])
def get_temperature():
    humidity, celsius_temperature = Adafruit_DHT.read_retry(sensor, pin)

    if humidity is not None and celsius_temperature is not None:
        # Convert temperature to Fahrenheit
        fahrenheit_temperature = (celsius_temperature * 9 / 5) + 32

        data = {
            "temperature_C": celsius_temperature,
            "temperature_F": fahrenheit_temperature,
            "humidity": humidity,
        }

        # Send the data to the receiver Raspberry Pi
        try:
            response = requests.post(receiver_url, json=data)
            if response.status_code == 200:
                return jsonify(data), 200
            else:
                return "Failed to send data to the receiver Raspberry Pi.", 500
        except Exception as e:
            return f"Error sending data: {str(e)}", 500
    else:
        return "Failed to read sensor data.", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
