import os
import glob
import time
import RPi.GPIO as GPIO

# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin where the sensor is connected
sensor_pin = 4  # Change this to the actual GPIO pin you've connected the sensor to

# DS18B20 sensor directory
sensor_dir = "/sys/bus/w1/devices/"


# Function to read temperature from DS18B20
def read_temperature():
    try:
        sensor_file = glob.glob(sensor_dir + "28*")[0] + "/w1_slave"

        with open(sensor_file, "r") as file:
            lines = file.readlines()

        while lines[0].strip()[-3:] != "YES":
            time.sleep(0.2)
            lines = read_temperature()

        temperature_line = lines[1].find("t=")
        if temperature_line != -1:
            temperature_str = lines[1][temperature_line + 2 :]
            temperature_celsius = float(temperature_str) / 1000.0
            return temperature_celsius

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


try:
    GPIO.setup(sensor_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    while True:
        temperature = read_temperature()
        if temperature is not None:
            print(f"Temperature: {temperature}°C")
        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    GPIO.cleanup()
