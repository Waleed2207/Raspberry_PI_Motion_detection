import requests
import socket

class ServerCommunication:
    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port

    def is_server_running(self):
        """Check if the Node.js server is running."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.settimeout(2)  # Set a timeout for the connection attempt
                s.connect((self.server_address, int(self.server_port)))
                s.close()
                print("Server is running.")
                return True
            except socket.error as e:
                print(f"Server check failed: {e}")
                return False

    def send_request_to_node(self, state):
        url = f"http://{self.server_address}:{self.server_port}/motion-detected"
        payload = {"state": state}
        print(f"Sending request to {url} with payload: {payload}")  # Diagnostic log
        try:
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code == 200:
                print(f"Light {state} request successful: {response.status_code}")
                return True
            else:
                print(f"Request failed with status code: {response.status_code}, response: {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Request to Node.js server failed: {e}")
            return False
