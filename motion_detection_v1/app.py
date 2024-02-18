# app.py
from flask import Flask, render_template
import threading
from dotenv import load_dotenv
import os
from device_manager import DeviceManager
from server_communication import ServerCommunication

app = Flask(__name__)

# Load .env variables for server configuration
load_dotenv()
NODE_SERVER_ADDRESS = os.getenv('NODE_SERVER_ADDRESS')
NODE_SERVER_PORT = os.getenv('NODE_SERVER_PORT')

# Instantiate device manager and server communication
device_manager = DeviceManager(17, 19, 20)  # Example GPIO pins
server_communication = ServerCommunication(NODE_SERVER_ADDRESS, NODE_SERVER_PORT)

manual_control = False

@app.route("/")
def index():
    return render_template('index.html', manual_control=manual_control)

@app.route("/<action>", methods=['GET', 'POST'])
def action(action):
    global manual_control
    if action == "on":
        device_manager.led_relay_on()
        manual_control = True
    elif action == "off":
        device_manager.led_relay_off()
        manual_control = False
    elif action == "auto":
        manual_control = False
    return render_template('index.html', manual_control=manual_control)

def monitor_pir():
    while True:
        if device_manager.pir.motion_detected and not manual_control:
            device_manager.led_relay_on()
        else:
            device_manager.led_relay_off()

if __name__ == '__main__':
    threading.Thread(target=monitor_pir, daemon=True).start()
    app.run(debug=False, host='0.0.0.0', port=5009)
