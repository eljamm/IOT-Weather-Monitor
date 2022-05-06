import json
import random
import time
from datetime import datetime

from flask import Flask, Response, render_template, stream_with_context


# ------------------- #
# Flask Configuration #
# ------------------- #
application = Flask(__name__)
random.seed()   # Initialize the random number generator


# ----------------------- #
# Raspberry Configuration #
# ----------------------- #
# pin_DHT11 = 18
# pin_gaz = 27
# pin_buzzer = 22
# cooler = 13
# heater = 19

# GPIO.setmode(GPIO.BCM)
# GPIO.setwarnings(False)
# GPIO.setup(pin_buzzer, GPIO.OUT)
# GPIO.setup(pin_gaz, GPIO.IN)
# GPIO.setup(cooler, GPIO.OUT)
# GPIO.setup(heater, GPIO.OUT)
# GPIO.output(cooler, GPIO.LOW)
# GPIO.output(heater, GPIO.LOW)

# DHT11 = Adafruit_DHT.DHT11
# pwm = GPIO.PWM(pin_buzzer, 10)


# --------- #
# Debugging #
# --------- #
DEBUG = False


@application.route('/')
def index():
    return render_template('index.html')


@application.route('/chart-data')
def chart_data():
    def generate_random_data():
        while True:
            # Read humidity and temperature values from sensor and detect gaz
            # -- Raspberry -- #
            # humidity, temperature = Adafruit_DHT.read_retry(DHT11, pin_DHT11)
            # gaz = GPIO.input(pin_gaz)

            # -- Simulation -- #
            temperature = random.randrange(-10, 35)
            humidity = random.randrange(20, 65)
            # Weighted probabilities: '0'->20% and '1'->80%, read more:
            # https://pynative.com/python-weighted-random-choices-with-probability/
            gaz = random.choices([0, 1], weights=(20, 80), k=1)[0]

            # Get the states for the display/action
            state_action = check_action(temperature, humidity)
            state_gaz = check_gaz(gaz)

            # Load all information in a json
            json_data = json.dumps(
                {'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                 'temperature': temperature,
                 'humidity': humidity,
                 'state_gaz': state_gaz,
                 'state_action': state_action
                 })

            # Return each json data, read more:
            # https://www.tutorialsteacher.com/python/python-generator)
            yield f"data:{json_data}\n\n"
            time.sleep(1)   # Waiting to not clutter the output

    # More about streaming content:
    # https://flask.palletsprojects.com/en/1.1.x/patterns/streaming/#streaming-with-context
    response = Response(stream_with_context(
        generate_random_data()), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["X-Accel-Buffering"] = "no"
    return response


def check_action(temperature, humidity):
    if humidity is not None and temperature is not None:
        if temperature < 15 or humidity > 60:
            if DEBUG is True:
                print("Heater ON")
            # GPIO.output(cooler, GPIO.LOW)
            # GPIO.output(heater, GPIO.HIGH)
            return 1
        elif temperature > 28 or humidity < 20:
            if DEBUG is True:
                print("Cooler ON")
            # GPIO.output(cooler, GPIO.HIGH)
            # GPIO.output(heater, GPIO.LOW)
            return 2
        else:
            if DEBUG is True:
                print("Normal Conditions")
            # GPIO.output(cooler, GPIO.LOW)
            # GPIO.output(heater, GPIO.LOW)
            return 3
    else:
        print("Null values")


def check_gaz(gaz):
    off = 1
    if gaz != off:
        if DEBUG is True:
            print('* Danger *')
        # pwm.start(10)
        return 1
    else:
        if DEBUG is True:
            print('* Safe *')
        # pwm.stop()
        return 2


if __name__ == '__main__':
    application.run(debug=True, threaded=True)
