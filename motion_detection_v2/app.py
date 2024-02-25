from flask import Flask, render_template
import threading
from dotenv import load_dotenv
import os
from device_manager import DeviceManager
from server_communication import ServerCommunication
import time

app = Flask(__name__)

# Load .env variables for server configuration
load_dotenv()
NODE_SERVER_ADDRESS = os.getenv('NODE_SERVER_ADDRESS')
NODE_SERVER_PORT = os.getenv('NODE_SERVER_PORT')

# Instantiate device manager and server communication
device_manager = DeviceManager(17, 19, 20)  # Example GPIO pins
server_communication = ServerCommunication(NODE_SERVER_ADDRESS, NODE_SERVER_PORT)

# Use threading.Event for manual control flag
manual_control_flag = threading.Event()

@app.route("/")
def index():
    manual_control = manual_control_flag.is_set()
    return render_template('index.html', manual_control=manual_control)

@app.route("/<action>", methods=['GET', 'POST'])
def action(action):
    if action == "on":
        device_manager.led_relay_on()
        server_communication.send_request_to_node("on")  # Send state update to Node.js server
        manual_control_flag.set()
    elif action == "off":
        device_manager.led_relay_off()
        server_communication.send_request_to_node("off")  # Send state update to Node.js server
        manual_control_flag.clear()
    elif action == "auto":
        manual_control_flag.clear()
    return render_template('index.html', manual_control=manual_control_flag.is_set())

def monitor_pir(device_manager, manual_control_flag, server_communication, sensor_id):
    last_motion_time = None
    motion_detected = False

    while True:
        try:
            if device_manager.pir.motion_detected and not manual_control_flag.is_set():
                if not motion_detected:
                    print("Motion detected")
                    motion_detected = True
                    device_manager.led_relay_off()
                    server_communication.send_request_to_node("on", sensor_id)  # Include sensor_id
                last_motion_time = time.time()

            elif motion_detected and (time.time() - last_motion_time) > 10 and not manual_control_flag.is_set():
                print("No motion detected for 10 seconds")
                device_manager.led_relay_on()
                motion_detected = False
                server_communication.send_request_to_node("off", sensor_id)  # Include sensor_id

        except RuntimeError as e:
            print(f"Caught RuntimeError during PIR monitoring: {e}")
        time.sleep(0.1)

sensor_id = "247"  # Define your sensor ID here

if __name__ == '__main__':
    # Start the monitor_pir thread with required arguments including server_communication and sensor_id
    threading.Thread(target=monitor_pir, args=(device_manager, manual_control_flag, server_communication, sensor_id), daemon=True).start()
    app.run(debug=False, host='0.0.0.0', port=5009)
