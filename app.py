from flask import Flask, render_template, request
import Adafruit_DHT
import requests
import time
import threading

app = Flask(__name__)

# Sensor configuration
sensor = Adafruit_DHT.DHT11
pin = 4
receiver_url = (
    "http://169.254.204.19:5000"  # Replace with the IP of the receiver Raspberry Pi
)
# Receiver Raspberry Pi URL
# RPI1:169.254.204.19:5000 (White and Red case)
# RPI2:169.254.79.226:5000 (Black Case)

# Create an empty list to store received data
received_data = []

# Flag to control data sending
send_data_flag = False


def read_and_send_data():
    global send_data_flag

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

                if send_data_flag:
                    # Send the data to the receiver Raspberry Pi
                    try:
                        response = requests.post(
                            receiver_url + "/store-data", json=data
                        )
                        if response.status_code == 200:
                            print("Data sent to the other Raspberry Pi:", data)
                        else:
                            print("Failed to send data to the other Raspberry Pi.")
                    except Exception as e:
                        print(f"Error sending data: {str(e)}")

                    # Add the data to the received_data list
                    received_data.append(data)

                send_data_flag = False

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
    global send_data_flag
    send_data_flag = True  # Set the flag to send data

    return (
        jsonify(
            {
                "message": "Data will be sent to the receiver Raspberry Pi.",
                "data": received_data[-1],
            }
        ),
        200,
    )


@app.route("/store-data", methods=["POST"])
def store_data():
    try:
        data = request.json
        data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        received_data.append(data)  # Add the received data to the list

        # Reset the list when it reaches 10 entries
        if len(received_data) >= 10:
            received_data.clear()

        return "Data received and stored successfully.", 200
    except Exception as e:
        return f"Error processing and storing data: {str(e)}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
