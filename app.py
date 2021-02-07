import os
import signal
import time
import random
import paho.mqtt.client as mqtt
import sonos_control

owens_room_white_noise_is_on = False
bedroom_white_noise_is_on = False
office_white_noise_is_on = False
livingroom_white_noise_is_on = False
basement_white_noise_is_on = False

last_time_status_check_in = 0
status_checkin_delay = 60.0

MQTT_HOST = os.environ["MQTT_HOST"]
MQTT_PORT = int(os.environ["MQTT_PORT"])

MQTT_SETON_PATH = "home/{0}/switches/whitenoise/setOn"
MQTT_GETON_PATH = "home/{0}/switches/whitenoise/getOn"

BEDROOM_VALUE = "bedroom"
OFFICE_VALUE = "office"
OWENSROOM_VALUE = "owensroom"
LIVINGROOM_VALUE = "livingroom"
BASEMENT_VALUE = "basement"

ON_VALUE = "ON"
OFF_VALUE = "OFF"


class exit_monitor_setup:
    exit_now_flag_raised = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.exit_now_flag_raised = True

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("MQTT: Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")
    client.subscribe(MQTT_SETON_PATH.format(OWENSROOM_VALUE))
    client.subscribe(MQTT_SETON_PATH.format(BEDROOM_VALUE))
    client.subscribe(MQTT_SETON_PATH.format(OFFICE_VALUE))
    client.subscribe(MQTT_SETON_PATH.format(LIVINGROOM_VALUE))
    client.subscribe(MQTT_SETON_PATH.format(BASEMENT_VALUE))


def on_disconnect(client, userdata, rc):
    print("MQTT: disconnecting reason " + str(rc))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, message):
    if message.topic == MQTT_SETON_PATH.format(BEDROOM_VALUE):
        whitenoise_message_response_action(BEDROOM_VALUE, message)
    elif message.topic == MQTT_SETON_PATH.format(OWENSROOM_VALUE):
        whitenoise_message_response_action(OWENSROOM_VALUE, message)
    elif message.topic == MQTT_SETON_PATH.format(OFFICE_VALUE):
        whitenoise_message_response_action(OFFICE_VALUE, message)
    elif message.topic == MQTT_SETON_PATH.format(LIVINGROOM_VALUE):
        whitenoise_message_response_action(LIVINGROOM_VALUE, message)
    elif message.topic == MQTT_SETON_PATH.format(BASEMENT_VALUE):
        whitenoise_message_response_action(BASEMENT_VALUE, message)


def whitenoise_message_response_action(room, message):
    global last_time_status_check_in
    last_time_status_check_in = time.monotonic()

    if str(message.payload.decode("utf-8")) == ON_VALUE:
        turnOnWhiteNoise(room, showPrint=True)
        client.publish(MQTT_GETON_PATH.format(room), ON_VALUE)
    elif str(message.payload.decode("utf-8")) == OFF_VALUE:
        turnOffWhiteNoise(room, showPrint=True)
        client.publish(MQTT_GETON_PATH.format(room), OFF_VALUE)


def turnOffWhiteNoise(room, showPrint=False):
    global bedroom_white_noise_is_on
    global owens_room_white_noise_is_on
    global office_white_noise_is_on
    global livingroom_white_noise_is_on
    global basement_white_noise_is_on

    if room == BEDROOM_VALUE:
        bedroom_white_noise_is_on = False
        sonos_control.sonos_whitenoise_stop(sonos_control.SONOS_BEDROOM)
    elif room == OWENSROOM_VALUE:
        owens_room_white_noise_is_on = False
        sonos_control.sonos_whitenoise_stop(sonos_control.SONOS_OWENS_ROOM)
    elif room == OFFICE_VALUE:
        office_white_noise_is_on = False
        sonos_control.sonos_whitenoise_stop(sonos_control.SONOS_OFFICE)
    elif room == LIVINGROOM_VALUE:
        livingroom_white_noise_is_on = False
        sonos_control.sonos_whitenoise_stop(sonos_control.SONOS_LIVINGROOM)
    elif room == BASEMENT_VALUE:
        basement_white_noise_is_on = False
        sonos_control.sonos_whitenoise_stop(sonos_control.SONOS_BASEMENT)

    if showPrint:
        print(f"turning {room} whitenoise OFF ....")


def turnOnWhiteNoise(room, showPrint=False):
    global bedroom_white_noise_is_on
    global owens_room_white_noise_is_on
    global office_white_noise_is_on
    global livingroom_white_noise_is_on
    global basement_white_noise_is_on

    if room == BEDROOM_VALUE:
        bedroom_white_noise_is_on = True
        sonos_control.sonos_whitenoise_start(sonos_control.SONOS_BEDROOM)
    elif room == OWENSROOM_VALUE:
        owens_room_white_noise_is_on = True
        sonos_control.sonos_whitenoise_start(
            sonos_control.SONOS_OWENS_ROOM, 60)
    elif room == OFFICE_VALUE:
        office_white_noise_is_on = True
        sonos_control.sonos_whitenoise_start(sonos_control.SONOS_OFFICE)
    elif room == LIVINGROOM_VALUE:
        livingroom_white_noise_is_on = True
        sonos_control.sonos_whitenoise_start(sonos_control.SONOS_LIVINGROOM)
    elif room == BASEMENT_VALUE:
        basement_white_noise_is_on = True
        sonos_control.sonos_whitenoise_start(sonos_control.SONOS_BASEMENT)

    if showPrint:
        print(f"turning {room} whitenoise ON ....")


def update_status_action(speaker, room):
    if sonos_control.sonos_whitenoise_is_on(speaker):
        client.publish(MQTT_GETON_PATH.format(room), ON_VALUE)
    else:
        client.publish(MQTT_GETON_PATH.format(room), OFF_VALUE)


def update_status():
    global last_time_status_check_in

    update_status_action(sonos_control.SONOS_BEDROOM, BEDROOM_VALUE)
    update_status_action(sonos_control.SONOS_OFFICE, OFFICE_VALUE)
    update_status_action(sonos_control.SONOS_OWENS_ROOM, OWENSROOM_VALUE)
    update_status_action(sonos_control.SONOS_LIVINGROOM, LIVINGROOM_VALUE)
    update_status_action(sonos_control.SONOS_BASEMENT, BASEMENT_VALUE)

    last_time_status_check_in = time.monotonic()


if __name__ == '__main__':
    exit_monitor = exit_monitor_setup()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    client.connect(MQTT_HOST, MQTT_PORT, 60)

    update_status()

    client.loop_start()
    # see below, not sure if sleep is needed here, probably not
    time.sleep(0.001)

    while not exit_monitor.exit_now_flag_raised:
        # added time.sleep 1 ms after seeing 100% CPU usage
        # found this solution https://stackoverflow.com/a/41749754
        time.sleep(0.001)
        current_seconds_count = time.monotonic()
        if current_seconds_count - last_time_status_check_in > status_checkin_delay:
            update_status()

    client.loop_stop()
    client.disconnect()
    print("white noise service ended")
