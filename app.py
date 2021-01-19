import os
import time
import random
import paho.mqtt.client as mqtt
import sonos_control

owens_room_white_noise_is_on = False
bedroom_white_noise_is_on = False
office_white_noise_is_on = False

last_time_status_check_in = 0
status_checkin_delay = 60.0

MQTT_HOST = os.environ["MQTT_HOST"]
MQTT_PORT = int(os.environ["MQTT_PORT"])

MQTT_SETON_PATH = "home/{0}/switches/whitenoise/setOn"
MQTT_GETON_PATH = "home/{0}/switches/whitenoise/getOn"

BEDROOM_VALUE = "bedroom"
OFFICE_VALUE = "office"
OWENSROOM_VALUE = "owensroom"

ON_VALUE = "ON"
OFF_VALUE = "OFF"

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
	print("MQTT: Connected with result code "+str(rc))

	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	client.subscribe("$SYS/#")
	client.subscribe(MQTT_SETON_PATH.format(OWENSROOM_VALUE))
	client.subscribe(MQTT_SETON_PATH.format(BEDROOM_VALUE))
	client.subscribe(MQTT_SETON_PATH.format(OFFICE_VALUE))

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

def whitenoise_message_response_action(room, message):
	global last_time_status_check_in
	global repeat_command_last_timestamp
	
	repeat_command_last_timestamp = time.monotonic() + 5
	last_time_status_check_in = time.monotonic()

	if str(message.payload.decode("utf-8")) == ON_VALUE:
		turnOnWhiteNoise(room, showPrint=True)
		client.publish(MQTT_GETON_PATH.format(room),ON_VALUE)
	elif str(message.payload.decode("utf-8")) == OFF_VALUE:
		turnOffWhiteNoise(room, showPrint=True)
		client.publish(MQTT_GETON_PATH.format(room),OFF_VALUE)

def turnOffWhiteNoise(room, showPrint = False):
	global bedroom_white_noise_is_on
	global owens_room_white_noise_is_on
	global office_white_noise_is_on
	
	if room == BEDROOM_VALUE:
		bedroom_white_noise_is_on = False
		sonos_control.sonos_whitenoise_stop(sonos_control.SONOS_BEDROOM)
	elif room == OWENSROOM_VALUE:
		owens_room_white_noise_is_on = False
		sonos_control.sonos_whitenoise_stop(sonos_control.SONOS_OWENS_ROOM)
	elif room == OFFICE_VALUE:
		office_white_noise_is_on = False
		sonos_control.sonos_whitenoise_stop(sonos_control.SONOS_OFFICE)
	
	if showPrint:
		print(f"turning {room} whitenoise OFF ....")

def turnOnWhiteNoise(room, showPrint = False):
	global bedroom_white_noise_is_on
	global owens_room_white_noise_is_on
	global office_white_noise_is_on
	
	if room == BEDROOM_VALUE:
		bedroom_white_noise_is_on = True
		sonos_control.sonos_whitenoise_start(sonos_control.SONOS_BEDROOM)
	elif room == OWENSROOM_VALUE:
		owens_room_white_noise_is_on = True
		sonos_control.sonos_whitenoise_start(sonos_control.SONOS_OWENS_ROOM, 60)
	elif room == OFFICE_VALUE:
		office_white_noise_is_on = True
		sonos_control.sonos_whitenoise_start(sonos_control.SONOS_OFFICE)

	if showPrint:
		print(f"turning {room} whitenoise ON ....")

def update_status():
	global last_time_status_check_in
	
	if sonos_control.sonos_whitenoise_is_on(sonos_control.SONOS_BEDROOM):
		client.publish(MQTT_GETON_PATH.format(BEDROOM_VALUE),ON_VALUE)
	else:
		client.publish(MQTT_GETON_PATH.format(BEDROOM_VALUE),OFF_VALUE)

	if sonos_control.sonos_whitenoise_is_on(sonos_control.SONOS_OWENS_ROOM):
		client.publish(MQTT_GETON_PATH.format(OWENSROOM_VALUE),ON_VALUE)
	else:
		client.publish(MQTT_GETON_PATH.format(OWENSROOM_VALUE),OFF_VALUE)

	if sonos_control.sonos_whitenoise_is_on(sonos_control.SONOS_OFFICE):
		client.publish(MQTT_GETON_PATH.format(OFFICE_VALUE),ON_VALUE)
	else:
		client.publish(MQTT_GETON_PATH.format(OFFICE_VALUE),OFF_VALUE)

	last_time_status_check_in = time.monotonic()

client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

client.connect(MQTT_HOST, MQTT_PORT, 60)

update_status()

client.loop_start()
# see below, not sure if sleep is needed here, probably not
time.sleep(0.001)

try:

	while True:
		# added time.sleep 1 ms after seeing 100% CPU usage
		# found this solution https://stackoverflow.com/a/41749754
		time.sleep(0.001)
		current_seconds_count = time.monotonic()
		if current_seconds_count - last_time_status_check_in > status_checkin_delay:
			update_status()

except KeyboardInterrupt:
	pass

client.loop_stop()
client.disconnect()