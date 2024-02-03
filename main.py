from flask import Flask, render_template
import threading
import time
import requests
import socket
from gpiozero import LED, MotionSensor, OutputDevice
from dotenv import load_dotenv
import os

app = Flask(__name__)

# GPIO Pins (BCM numbering)
LED_PIN = 17     # Corresponds to GPIO 2
PIR_PIN = 20    # Corresponds to GPIO 17
RELAY_PIN = 19  # Corresponds to GPIO 27 (use BCM numbering)

manual_control = False
led_status = False

# Initialize GPIO Zero devices
led = LED(LED_PIN)
relay = OutputDevice(RELAY_PIN, active_high=False, initial_value=True)  # Relay OFF initially, active_high=False means relay is ON when output is False
pir = MotionSensor(PIR_PIN)

load_dotenv()  # This loads the variables from .env

NODE_SERVER_ADDRESS = os.getenv('NODE_SERVER_ADDRESS')
NODE_SERVER_PORT = os.getenv('NODE_SERVER_PORT')

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
        response = requests.post(url, json={"state": state})
        print(f"Light {state} request successful: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request to Node.js server failed: {e}")
def led_relay_on():
    """Turn the LED and relay on."""
    global led_status
    if not led_status:
        server_running = is_server_running(NODE_SERVER_ADDRESS, NODE_SERVER_PORT)
        if server_running:
            try:
                led.on()
                relay.on()  # Relay ON
                led_status = True
                print("Bulb ON, Relay LOW")
                send_request_to_node("on")
            except Exception as e:
                print(f"An error occurred while turning on the LED/Relay: {e}")
        else:
            print("Cannot turn on the bulb. The server is down or unreachable.")

def led_relay_off():
    """Turn the LED and relay off."""
    global led_status
    if led_status:
        led.off()
        relay.off()  # Relay OFF
        led_status = False
        print("Bulb OFF, Relay HIGH")
        send_request_to_node("off")

def monitor_pir():
    global manual_control, led_status
    last_motion_time = None
    motion_detected = False
    while True:
        if pir.motion_detected:
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
        led_relay_off()  # Ensure LED/Relay are in the correct state at startup
        threading.Thread(target=monitor_pir, daemon=True).start()
        app.run(debug=False, host='0.0.0.0', port=5009)
    except KeyboardInterrupt:
        print("Program stopped")
    finally:
        # No need for GPIO.cleanup() as GPIO Zero handles cleanup automatically
        pass


