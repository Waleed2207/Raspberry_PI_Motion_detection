import requests
from config import Config

def send_request_to_node(state):
    url = f"http://{Config.NODE_SERVER_ADDRESS}:{Config.NODE_SERVER_PORT}/motion-detected"
    try:
        response = requests.post(url, json={"state": state}, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False
