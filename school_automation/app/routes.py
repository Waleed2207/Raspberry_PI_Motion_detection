from flask import Blueprint, render_template, redirect, url_for
from devices.controller import DeviceController

bp = Blueprint('main', __name__, template_folder='templates')

controller = DeviceController()

@bp.route("/")
def index():
    return render_template('index.html', led_status=controller.led_status)

@bp.route("/toggle/<state>", methods=['GET'])
def toggle_led(state):
    if state == 'on':
        controller.toggle_led(True)
    elif state == 'off':
        controller.toggle_led(False)
    return redirect(url_for('main.index'))
