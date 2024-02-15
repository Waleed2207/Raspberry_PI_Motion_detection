from dotenv import load_dotenv
import os

# Ensure .env variables are loaded
load_dotenv()

class Config:
    LED_PIN = os.getenv('LED_PIN', 17)
    PIR_PIN = os.getenv('PIR_PIN', 20)
    RELAY_PIN = os.getenv('RELAY_PIN', 19)
    NODE_SERVER_ADDRESS = os.getenv('NODE_SERVER_ADDRESS')
    NODE_SERVER_PORT = os.getenv('NODE_SERVER_PORT', '5000')
