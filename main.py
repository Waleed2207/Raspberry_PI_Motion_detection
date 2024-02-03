# from flask import Flask, render_template
# import RPi.GPIO as GPIO
# import threading
# import time
# import requests
# import socket
# from dotenv import load_dotenv
# import os
#
# app = Flask(__name__)
#
# # GPIO Pins (BOARD numbering)
# LED_PIN = 3    # Corresponds to GPIO 2
# PIR_PIN = 11   # Corresponds to GPIO 17
# RELAY_PIN = 13 # Relay PIN
# manual_control = False
# led_status = False
#
#
# load_dotenv()  # This loads the variables from .env
#
# NODE_SERVER_ADDRESS = os.getenv('NODE_SERVER_ADDRESS')
# NODE_SERVER_PORT = os.getenv('NODE_SERVER_PORT')
#
# # GPIO setup
# try:
#     GPIO.setwarnings(False)
#     GPIO.setmode(GPIO.BOARD)
#     GPIO.setup(LED_PIN, GPIO.OUT)   # LED output pin
#     GPIO.setup(RELAY_PIN, GPIO.OUT) # Relay output pin
#     GPIO.setup(PIR_PIN, GPIO.IN)    # PIR sensor input pin
#     GPIO.output(RELAY_PIN, GPIO.HIGH)  # Initialize Relay OFF
# except Exception as e:
#     print(f"Error accessing GPIO: {e}")
#
# def is_server_running(host, port):
#     """Check if the Node.js server is running."""
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         try:
#             s.settimeout(2)  # Set a timeout for the connection attempt
#             s.connect((host, int(port)))
#             s.close()
#             print("Server is running.")
#             return True
#         except socket.error as e:
#             print(f"Server check failed: {e}")
#             return False
#
# def send_request_to_node(state):
#     """Send request to the Node.js server."""
#     url = f"http://{NODE_SERVER_ADDRESS}:{NODE_SERVER_PORT}/motion-detected"
#     try:
#         response = requests.post(url, json={"state": state})
#         print(f"Light {state} request successful: {response.status_code}")
#     except requests.exceptions.RequestException as e:
#         print(f"Request to Node.js server failed: {e}")
#
# def led_relay_on():
#     """Turn the LED and relay on."""
#     global led_status
#     if not led_status:
#         server_running = is_server_running(NODE_SERVER_ADDRESS, NODE_SERVER_PORT)
#         if server_running:
#             try:
#                 GPIO.output(LED_PIN, GPIO.HIGH)
#                 GPIO.output(RELAY_PIN, GPIO.LOW)  # Relay ON
#                 led_status = True
#                 print("Bulb ON, Relay LOW")
#                 send_request_to_node("on")
#             except Exception as e:
#                 print(f"An error occurred while turning on the LED/Relay: {e}")
#         else:
#             print("Cannot turn on the bulb. The server is down or unreachable.")
#
#
# def led_relay_off():
#     """Turn the LED and relay off."""
#     global led_status
#     if led_status:
#         GPIO.output(LED_PIN, GPIO.LOW)
#         GPIO.output(RELAY_PIN, GPIO.HIGH)  # Relay OFF
#         led_status = False
#         print("Bulb OFF, Relay HIGH")
#         send_request_to_node("off")
#
# def read_pir():
#     """Read the PIR sensor value."""
#     return GPIO.input(PIR_PIN)
#
# def monitor_pir():
#     global manual_control, led_status
#     last_motion_time = None
#     motion_detected = False
#     while True:
#         pir_value = read_pir()
#         if pir_value:
#             last_motion_time = time.time()
#             motion_detected = True
#             if not led_status and not manual_control:
#                 led_relay_on()
#
#         elif motion_detected and (time.time() - last_motion_time > 10):
#             motion_detected = False
#             if not manual_control:
#                 led_relay_off()
#
#         time.sleep(0.1)
#
# @app.route("/")
# def index():
#     return render_template('index.html', manual_control=manual_control)
#
# @app.route("/<action>", methods=['GET', 'POST'])
# def action(action):
#     global manual_control
#     if action == "on":
#         led_relay_on()
#         manual_control = True
#     elif action == "off":
#         led_relay_off()
#         manual_control = False
#     elif action == "auto":
#         manual_control = False
#     return render_template('index.html', manual_control=manual_control)
#
# if __name__ == '__main__':
#     try:
#         led_relay_off()
#         threading.Thread(target=monitor_pir, daemon=True).start()
#         app.run(debug=False, host='0.0.0.0', port=5009)
#     except KeyboardInterrupt:
#         print("Program stopped")
#     finally:
#         GPIO.cleanup()
#------------------------- NEW VERSION---------------------------------------
from flask import Flask, render_template
import RPi.GPIO as GPIO
import threading
import time
import requests
import socket
from dotenv import load_dotenv
import os

app = Flask(__name__)

# GPIO Pins (BOARD numbering)
LED_PIN = 3    # Corresponds to GPIO 2
PIR_PIN = 11   # Corresponds to GPIO 17
RELAY_PIN = 13 # Relay PIN
manual_control = False
led_status = False

# Node.js Server Address
#NODE_SERVER_ADDRESS = "10.0.0.9"
#NODE_SERVER_PORT = "5001"

load_dotenv()  # This loads the variables from .env

NODE_SERVER_ADDRESS = os.getenv('NODE_SERVER_ADDRESS')
NODE_SERVER_PORT = os.getenv('NODE_SERVER_PORT')

# GPIO setup
try:
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(LED_PIN, GPIO.OUT)   # LED output pin
    GPIO.setup(RELAY_PIN, GPIO.OUT) # Relay output pin
    GPIO.setup(PIR_PIN, GPIO.IN)    # PIR sensor input pin
    GPIO.output(RELAY_PIN, GPIO.HIGH)  # Initialize Relay OFF
except Exception as e:
    print(f"Error accessing GPIO: {e}")

def is_server_running(host, port):
    """Check if the Node.js server is running."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(2)  # Set a timeout for the connection attempt
            s.connect((host, int(port)))
            s.close()
            print("Server is running.")
            return True
        except socket.error as e:
            print(f"Server check failed: {e}")
            return False

def send_request_to_node(state):
    """Send request to the Node.js server."""
    url = f"http://{NODE_SERVER_ADDRESS}:{NODE_SERVER_PORT}/motion-detected"
    try:
        response = requests.post(url, json={"state": state}, timeout=5)  # Set a reasonable timeout
        if response.status_code == 200:
            print(f"Light {state} request successful: {response.status_code}")
            return True
    except requests.exceptions.RequestException as e:
        print(f"Request to Node.js server failed: {e}")
    return False

def led_relay_on():
    """Turn the LED and relay on."""
    global led_status
    if not led_status:
        server_running = is_server_running(NODE_SERVER_ADDRESS, NODE_SERVER_PORT)
        if server_running and send_request_to_node("on"):
            try:
                GPIO.output(LED_PIN, GPIO.HIGH)
                GPIO.output(RELAY_PIN, GPIO.LOW)  # Relay ON
                led_status = True
                print("Bulb ON, Relay LOW")
            except Exception as e:
                print(f"An error occurred while turning on the LED/Relay: {e}")
        else:
            print("Cannot turn on the bulb. The server is down or unreachable.")


def led_relay_off():
    """Turn the LED and relay off."""
    global led_status
    if led_status:
        GPIO.output(LED_PIN, GPIO.LOW)
        GPIO.output(RELAY_PIN, GPIO.HIGH)  # Relay OFF
        led_status = False
        print("Bulb OFF, Relay HIGH")
        send_request_to_node("off")

def read_pir():
    """Read the PIR sensor value."""
    return GPIO.input(PIR_PIN)

def monitor_pir():
    global manual_control, led_status
    last_motion_time = None
    motion_detected = False
    while True:
        pir_value = read_pir()
        if pir_value:
            last_motion_time = time.time()
            motion_detected = True
            if not led_status and not manual_control:
                led_relay_on()

        elif motion_detected and (time.time() - last_motion_time > 10):
            motion_detected = False
            if not manual_control:
                led_relay_off()

        time.sleep(0.1)

@app.route("/")
def index():
    return render_template('index.html', manual_control=manual_control)

@app.route("/<action>", methods=['GET', 'POST'])
def action(action):
    global manual_control
    if action == "on":
        led_relay_on()
        manual_control = True
    elif action == "off":
        led_relay_off()
        manual_control = False
    elif action == "auto":
        manual_control = False
    return render_template('index.html', manual_control=manual_control)

if __name__ == '__main__':
    try:
        led_relay_off()
        threading.Thread(target=monitor_pir, daemon=True).start()
        app.run(debug=False, host='0.0.0.0', port=5009)
    except KeyboardInterrupt:
        print("Program stopped")
    finally:
        GPIO.cleanup()
