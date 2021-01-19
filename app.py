import time
import random
import paho.mqtt.client as mqtt
import sonos_control

owens_room_white_noise_is_on = False
bedroom_white_noise_is_on = False
office_white_noise_is_on = False

last_time_status_check_in = 0
status_checkin_delay = 60.0

MQTT_HOST = "192.168.7.97"
MQTT_PORT = 1883

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
	print("MQTT: Connected with result code "+str(rc))

	# Subscribing in on_connect() means that if we lose the connection and
	# reconnect then subscriptions will be renewed.
	client.subscribe("$SYS/#")
	client.subscribe("home/owensroom/switches/whitenoise/setOn")
	client.subscribe("home/bedroom/switches/whitenoise/setOn")
	client.subscribe("home/office/switches/whitenoise/setOn")

def on_disconnect(client, userdata, rc):
    print("MQTT: disconnecting reason " + str(rc))

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, message):
	if message.topic == "home/bedroom/switches/whitenoise/setOn":
		message_whitenoise("bedroom", message)
	elif message.topic == "home/owensroom/switches/whitenoise/setOn":
		message_whitenoise("owensroom", message)
	elif message.topic == "home/office/switches/whitenoise/setOn":
		message_whitenoise("office", message)

def message_whitenoise(room, message):
	global last_time_status_check_in
	global repeat_command_last_timestamp
	
	repeat_command_last_timestamp = time.monotonic() + 5
	last_time_status_check_in = time.monotonic()

	if str(message.payload.decode("utf-8")) == "ON":
		turnOnWhiteNoise(room, showPrint=True)
		client.publish(f"home/{room}/switches/whitenoise/getOn","ON")
	elif str(message.payload.decode("utf-8")) == "OFF":
		turnOffWhiteNoise(room, showPrint=True)
		client.publish(f"home/{room}/switches/whitenoise/getOn","OFF")

def turnOffWhiteNoise(room, showPrint = False):
	global bedroom_white_noise_is_on
	global owens_room_white_noise_is_on
	global office_white_noise_is_on
	
	if room == "bedroom":
		bedroom_white_noise_is_on = False
		sonos_control.sonos_whitenoise_stop(sonos_control.SONOS_BEDROOM)
	elif room == "owensroom":
		owens_room_white_noise_is_on = False
		sonos_control.sonos_whitenoise_stop(sonos_control.SONOS_OWENS_ROOM)
	elif room == "office":
		office_white_noise_is_on = False
		sonos_control.sonos_whitenoise_stop(sonos_control.SONOS_OFFICE)
	
	if showPrint:
		print(f"turning {room} whitenoise OFF ....")

def turnOnWhiteNoise(room, showPrint = False):
	global bedroom_white_noise_is_on
	global owens_room_white_noise_is_on
	global office_white_noise_is_on
	
	if room == "bedroom":
		bedroom_white_noise_is_on = True
		sonos_control.sonos_whitenoise_start(sonos_control.SONOS_BEDROOM)
	elif room == "owensroom":
		owens_room_white_noise_is_on = True
		sonos_control.sonos_whitenoise_start(sonos_control.SONOS_OWENS_ROOM, 60)
	elif room == "office":
		office_white_noise_is_on = True
		sonos_control.sonos_whitenoise_start(sonos_control.SONOS_OFFICE)

	if showPrint:
		print(f"turning {room} whitenoise ON ....")

def update_status():
	global last_time_status_check_in
	
	bedroom_whitenoise_is_on = sonos_control.sonos_whitenoise_is_on(sonos_control.SONOS_BEDROOM)

	if bedroom_whitenoise_is_on:
		client.publish("home/bedroom/switches/whitenoise/getOn","ON")
	else:
		client.publish("home/bedroom/switches/whitenoise/getOn","OFF")

	owens_whitenoise_is_on = sonos_control.sonos_whitenoise_is_on(sonos_control.SONOS_OWENS_ROOM)

	if owens_whitenoise_is_on:
		client.publish("home/owensroom/switches/whitenoise/getOn","ON")
	else:
		client.publish("home/owensroom/switches/whitenoise/getOn","OFF")

	office_whitenoise_is_on = sonos_control.sonos_whitenoise_is_on(sonos_control.SONOS_OFFICE)

	if office_whitenoise_is_on:
		client.publish("home/office/switches/whitenoise/getOn","ON")
	else:
		client.publish("home/office/switches/whitenoise/getOn","OFF")


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