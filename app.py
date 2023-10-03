from flask import Flask, render_template, request
import Adafruit_DHT
import requests
import time
import pandas as pd

app = Flask(__name__)

sensor = Adafruit_DHT.DHT11
pin = 4

received_data_df = pd.DataFrame(
    columns=["Timestamp", "Temperature (C)", "Temperature (F)", "Humidity", "Origin"]
)
# Receiver Raspberry Pi URL
# RPI1:169.254.204.19:5000 (White and Red case)
# RPI2:169.254.79.226:5000 (Black Case)
receiver_url = "http://169.254.204.19:5000"

send_data_flag = True


def read_and_send_data():
    global send_data_flag

    while True:
        try:
            if send_data_flag:
                humidity, celsius_temperature = Adafruit_DHT.read_retry(sensor, pin)

                if humidity is not None and celsius_temperature is not None:
                    fahrenheit_temperature = (celsius_temperature * 9 / 5) + 32

                    data = {
                        "temperature_C": celsius_temperature,
                        "temperature_F": fahrenheit_temperature,
                        "humidity": humidity,
                        "origin": "Raspberry Pi 1",
                    }

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

                    received_data_df = received_data_df.append(data, ignore_index=True)

                send_data_flag = False

            time.sleep(10)
        except Exception as e:
            print(f"Error reading and sending data: {str(e)}")


@app.route("/")
def index():
    global received_data_df

    data_html = received_data_df.to_html(
        classes="table table-bordered table-striped", escape=False, index=False
    )

    return render_template("index.html", data_html=data_html)


@app.route("/send-data", methods=["POST"])
def send_data_manually():
    global send_data_flag

    try:
        if send_data_flag:
            humidity, celsius_temperature = Adafruit_DHT.read_retry(sensor, pin)

            if humidity is not None and celsius_temperature is not None:
                fahrenheit_temperature = (celsius_temperature * 9 / 5) + 32

                data = {
                    "temperature_C": celsius_temperature,
                    "temperature_F": fahrenheit_temperature,
                    "humidity": humidity,
                    "origin": "Raspberry Pi 1",
                }

                try:
                    response = requests.post(receiver_url + "/store-data", json=data)
                    if response.status_code == 200:
                        print("Data sent to the other Raspberry Pi:", data)
                    else:
                        print("Failed to send data to the other Raspberry Pi.")
                except Exception as e:
                    print(f"Error sending data: {str(e)}")

                received_data_df = received_data_df.append(data, ignore_index=True)

            send_data_flag = False

        return "Data sent to the other Raspberry Pi.", 200
    except Exception as e:
        return f"Error reading and sending data: {str(e)}", 500


@app.route("/store-data", methods=["POST"])
def store_data():
    try:
        data = request.json
        data["Timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")

        global received_data_df
        received_data_df = received_data_df.append(data, ignore_index=True)

        if len(received_data_df) >= 10:
            received_data_df = pd.DataFrame(
                columns=[
                    "Timestamp",
                    "Temperature (C)",
                    "Temperature (F)",
                    "Humidity",
                    "Origin",
                ]
            )

        return "Data received and stored successfully.", 200
    except Exception as e:
        return f"Error processing and storing data: {str(e)}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
