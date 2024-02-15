from gpiozero import LED, MotionSensor, OutputDevice
from config import Config

class DeviceController:
    def __init__(self):
        self.led = LED(Config.LED_PIN)
        self.relay = OutputDevice(Config.RELAY_PIN, active_high=False, initial_value=False)
        self.pir = MotionSensor(Config.PIR_PIN)
        self.led_status = False

    def toggle_led(self, state: bool):
        if state:
            self.led.on()
            self.relay.off()
            self.led_status = True
        else:
            self.led.off()
            self.relay.on()
            self.led_status = False
