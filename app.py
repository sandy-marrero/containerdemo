import time
from gpiozero import OneWireTemperature

# Define the GPIO pin where the sensor is connected (use the actual GPIO pin number you connected the sensor to)
sensor = OneWireTemperature(4)

try:
    while True:
        temperature = sensor.temperature
        print(f"Temperature: {temperature}°C")
        time.sleep(1)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    sensor.close()
