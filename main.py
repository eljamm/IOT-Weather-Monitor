from flask import Flask, render_template
import Adafruit_DHT
import RPi.GPIO as GPIO
import math
import time

# from celery import Celery
# from multiprocessing import Queue
# import threading
from multiprocessing import Process, Value

app = Flask(__name__)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
# celery = Celery(app.name)

pin_DHT11 = 18
pin_gaz = 27
pin_buzzer = 22
cooler = 13
heater = 19

DHT11 = Adafruit_DHT.DHT11
GPIO.setup(pin_buzzer, GPIO.OUT)
pwm = GPIO.PWM(pin_buzzer, 10)

# Setup GPIO
GPIO.setup(pin_gaz, GPIO.IN)
GPIO.setup(cooler, GPIO.OUT)
GPIO.setup(heater, GPIO.OUT)

# Make it low
GPIO.output(cooler, GPIO.LOW)
GPIO.output(heater, GPIO.LOW)


# Main Route
@app.route("/")
def main():
    # Read humidity and temperature values from sensor
    humidity, temperature = Adafruit_DHT.read_retry(DHT11, pin_DHT11)
    cooler_sts = GPIO.input(cooler)
    heater_sts = GPIO.input(heater)
    gaz_sts = GPIO.input(pin_gaz)
    buzzer_sts = GPIO.input(pin_buzzer)
    template_data = {
        'temperature': temperature,
        'humidity': humidity,
        'cooler': cooler_sts,
        'heater': heater_sts,
        'gaz': gaz_sts,
        'buzzer': buzzer_sts,
    }
    command_action()
    return render_template('main.html', **template_data)


# Manually control the heater and the cooler
def action():
    # Status of the device
    cooler_sts = GPIO.input(cooler)
    heater_sts = GPIO.input(heater)
    gaz_sts = GPIO.input(pin_gaz)
    buzzer_sts = GPIO.input(pin_buzzer)

    template_data = {
        'cooler': cooler_sts,
        'heater': heater_sts,
        'gaz': gaz_sts,
        'buzzer': buzzer_sts,
    }


def command_action():
    humidity, temperature = Adafruit_DHT.read_retry(DHT11, pin_DHT11)
    if humidity is not None and temperature is not None:
        if temperature < 15 or humidity > 60:
            GPIO.output(cooler, GPIO.LOW)
            GPIO.output(heater, GPIO.HIGH)
        elif temperature > 28 or humidity < 20:
            GPIO.output(cooler, GPIO.HIGH)
            GPIO.output(heater, GPIO.LOW)
        else:
            GPIO.output(cooler, GPIO.LOW)
            GPIO.output(heater, GPIO.LOW)
    else:
        print("Null values")


# @celery.task
# def task():
#     with app.app_context():
#         app.logger.info('running my task')


def state(x):
    if x == 1:
        # Safe
        print('* Safe *')
        pwm.stop()
    if x == 0:
        # Danger
        print('* Danger *')
        pwm.start(50)


def loop_gaz():
    status = 1
    while True:
        tmp = GPIO.input(pin_gaz)
        if tmp != status:
            state(tmp)
            status = tmp
        time.sleep(0.2)


if __name__ == "__main__":
    #recording_on = Value('b', True)

    #p_action = Process(target=command_action(), args=(recording_on,))
    #p_action.start()

    #p_gaz = Process(target=loop_gaz(), args=(recording_on,))
    #p_gaz.start()

    app.run(host='0.0.0.0', port=3000, debug=True)
    #p_action.join()
    #p_gaz.join()
