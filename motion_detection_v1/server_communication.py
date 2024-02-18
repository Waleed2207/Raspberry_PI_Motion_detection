# server_communication.py
import requests
import socket

class ServerCommunication:
    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port

    def is_server_running(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect((self.server_address, int(self.server_port)))
                return True
        except socket.error:
            return False

    def send_request_to_node(self, state):
        url = f"http://{self.server_address}:{self.server_port}/motion-detected"
        try:
            response = requests.post(url, json={"state": state}, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
