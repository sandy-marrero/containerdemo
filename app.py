from flask import Flask, jsonify, render_template, request
import Adafruit_DHT
import requests
import time
import threading

app = Flask(__name__)

# Sensor configuration
sensor = Adafruit_DHT.DHT11
pin = 4
receiver_url = "http://receiver-pi-ip:5000/store-data"  # Replace with the IP of the receiver Raspberry Pi

# Create an empty list to store received data
received_data = []


def read_and_send_data():
    while True:
        try:
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
                    response = requests.post(receiver_url + "/store-data", json=data)
                    if response.status_code == 200:
                        print("Data sent to receiver:", data)
                    else:
                        print("Failed to send data to the receiver Raspberry Pi.")
                except Exception as e:
                    print(f"Error sending data: {str(e)}")

                # Add the data to the received_data list
                received_data.append(data)

            time.sleep(10)  # Read and send data every 10 seconds
        except Exception as e:
            print(f"Error reading and sending data: {str(e)}")


# Start a background thread to continuously read and send data
data_thread = threading.Thread(target=read_and_send_data)
data_thread.daemon = True
data_thread.start()


@app.route("/")
def index():
    return render_template("index.html", data=received_data)


@app.route("/send-data", methods=["POST"])
def send_data_manually():
    try:
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
                response = requests.post(receiver_url + "/store-data", json=data)
                if response.status_code == 200:
                    print("Data sent to receiver:", data)
                else:
                    print("Failed to send data to the receiver Raspberry Pi.")
            except Exception as e:
                print(f"Error sending data: {str(e)}")

            # Add the data to the received_data list
            received_data.append(data)

        return "Data sent to the receiver Raspberry Pi.", 200
    except Exception as e:
        return f"Error reading and sending data: {str(e)}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
