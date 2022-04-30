from flask import Flask, render_template
import Adafruit_DHT
import RPi.GPIO as GPIO

app = Flask(__name__)
DHT11 = Adafruit_DHT.DHT11
pin_DHT11 = 18
cooler = 13
heater = 19

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(cooler, GPIO.OUT)
GPIO.setup(heater, GPIO.OUT)
GPIO.OUTPUT(cooler, GPIO.LOW)
GPIO.OUTPUT(heater, GPIO.LOW)


@app.route("/")
def main():
    humidity, temperature = Adafruit_DHT.read_retry(DHT11, pin_DHT11)
    template_data = {
        'temperature': temperature,
        'humidity': humidity
    }
    return render_template('main.html', **template_data)


@app.route("/<deviceName>/<action>")
def action(deviceName, action):
    # Get device name
    if deviceName == 'cooler':
        pointer = cooler
    if deviceName == 'heater':
        pointer = heater
        
    # Turn device on or off
    if action == "on":
        GPIO.output(pointer, GPIO.HIGH)
    if action == "off":
        GPIO.output(pointer, GPIO.LOW)

    # Status of the device
    cooler_sts = GPIO.input(cooler)
    heater_sts = GPIO.input(heater)

    template_data = {
        'cooler': cooler_sts,
        'heater': heater_sts,
    }
    return render_template('index.html', **template_data)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)
