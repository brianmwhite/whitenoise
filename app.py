import configparser
import pickle
import re
import signal
import time

import paho.mqtt.client as mqtt
import requests.exceptions

import sonos_control
import whitenoise_configparser

config = configparser.ConfigParser()
config.read("config/config.ini")

config_settings = config["SETTINGS"]
config_speakers_section = config["SPEAKERS"]
speaker_collection = whitenoise_configparser.get_speakers_from_config_section(
    config_speakers_section
)

SONOS_API_URL = config_settings.get("SONOS_API_URL")
SONOS_PLAYLIST_NAME = config_settings.get("SONOS_PLAYLIST_NAME")

last_time_status_check_in = 0
status_checkin_delay = config_settings.getfloat("STATUS_CHECKIN_DELAY")
RETRY_RESUME_ON_RESTART_ATTEMPT_LIMIT = config_settings.getint(
    "RETRY_RESUME_ON_RESTART_ATTEMPT_LIMIT"
)
RETRY_RESUME_ATTEMPT_COUNT = 0

PICKLE_FILE_LOCATION = config_settings.get("PICKLE_FILE_LOCATION")

MQTT_HOST = config_settings.get("MQTT_HOST")
MQTT_PORT = config_settings.getint("MQTT_PORT")

MQTT_SETON_PATH = config_settings.get("MQTT_SETON_PATH")
MQTT_SETON_PATH_REGEX = re.compile(
    MQTT_SETON_PATH.replace("/", "\\/").replace("{0}", "(\\w+)")
)

MQTT_GETON_PATH = config_settings.get("MQTT_GETON_PATH")
MQTT_GETONLINE_PATH = config_settings.get("MQTT_GETONLINE_PATH")
MQTT_ONLINEVALUE = config_settings.get("MQTT_ONLINEVALUE")

MQTT_ON_VALUE = config_settings.get("MQTT_ON_VALUE")
MQTT_OFF_VALUE = config_settings.get("MQTT_OFF_VALUE")


class exit_monitor_setup:
    exit_now_flag_raised = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.exit_now_flag_raised = True


def on_connect(client, userdata, flags, rc):
    # The callback for when the client receives a CONNACK response from the server.

    print("MQTT: Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

    # subscribe to all topics that match the pattern
    # a plus sign indicates a wildcard and is must be the only thing between
    # the separators /+/
    # for example this is ok: home/whitenoise/+/set
    # this is not ok: home/whitenoise+/set
    client.subscribe(MQTT_SETON_PATH.format("+"))


def on_disconnect(client, userdata, rc):
    print("MQTT: disconnecting reason " + str(rc))


def on_message(client, userdata, message):
    global speaker_collection
    # The callback for when a PUBLISH message is received from the server.

    topic_matches = MQTT_SETON_PATH_REGEX.match(message.topic)
    if topic_matches is not None:
        mqtt_speaker_name = topic_matches[1]

        if str(message.payload.decode("utf-8")) == MQTT_ON_VALUE:
            turnOnWhiteNoise(mqtt_speaker_name, showPrint=True)
        elif str(message.payload.decode("utf-8")) == MQTT_OFF_VALUE:
            turnOffWhiteNoise(mqtt_speaker_name, showPrint=True)

        try:
            with open(PICKLE_FILE_LOCATION, "wb") as datafile:
                pickle.dump(speaker_collection, datafile)
                print("saved whitenoise state")
        except pickle.UnpicklingError as e:
            print(e)
            pass
        except (AttributeError, EOFError, ImportError, IndexError) as e:
            print(e)
            pass
        except Exception as e:
            print(e)
            pass


def turnOnWhiteNoise(mqtt_speaker_name, showPrint=False):
    global speaker_collection
    success = False

    try:
        sonos_control.sonos_whitenoise_start(
            SONOS_API_URL,
            SONOS_PLAYLIST_NAME,
            speaker_collection[mqtt_speaker_name].sonos_speaker_name,
            speaker_collection[mqtt_speaker_name].volume_on,
        )

        speaker_collection[mqtt_speaker_name].is_speaker_on = True
        client.publish(MQTT_GETON_PATH.format(mqtt_speaker_name), MQTT_ON_VALUE)
        success = True
    except requests.exceptions.ConnectionError as ce:
        print(ce)
        success = False

    if showPrint:
        print(f"turning {mqtt_speaker_name} whitenoise ON ....")

    return success


def turnOffWhiteNoise(mqtt_speaker_name, showPrint=False):
    global speaker_collection
    success = False

    try:
        sonos_control.sonos_whitenoise_stop(
            SONOS_API_URL,
            speaker_collection[mqtt_speaker_name].sonos_speaker_name,
            speaker_collection[mqtt_speaker_name].volume_off,
        )

        speaker_collection[mqtt_speaker_name].is_speaker_on = False
        client.publish(MQTT_GETON_PATH.format(mqtt_speaker_name), MQTT_OFF_VALUE)
        success = True
    except requests.exceptions.ConnectionError as ce:
        print(ce)
        success = False

    if showPrint:
        print(f"turning {mqtt_speaker_name} whitenoise OFF ....")

    return success


def check_saved_state_for_resuming(saved_speaker_state):
    speakers_to_resume_playing = []
    for key, speaker in saved_speaker_state.items():
        if speaker.is_speaker_on is True:
            print(f"{key} = ON")
            speakers_to_resume_playing.append(speaker.mqtt_speaker_name)
        else:
            print(f"{key} = OFF")

    return speakers_to_resume_playing


def resume_speakers_that_were_offline(speakers_to_check_again):
    speaker_indexes_to_clear = []
    for index, mqtt_speaker_name in enumerate(speakers_to_check_again, start=0):
        if turnOnWhiteNoise(mqtt_speaker_name) is True:
            print(f"offline recheck: turned on {mqtt_speaker_name}")
            speaker_indexes_to_clear.append(index)
        else:
            print(f"offline recheck: still offline {mqtt_speaker_name}")

    # sort/reverse indexes to remove from the end first
    speaker_indexes_to_clear.sort(reverse=True)
    for index in speaker_indexes_to_clear:
        del speakers_to_check_again[index]

    return speakers_to_check_again


if __name__ == "__main__":
    exit_monitor = exit_monitor_setup()

    saved_speaker_state = {}

    try:
        with open(PICKLE_FILE_LOCATION, "rb") as datafile:
            saved_speaker_state = pickle.load(datafile)
            print("loaded whitenoise state")
    except (FileNotFoundError, pickle.UnpicklingError) as err:
        print("failed to load whitenoise state, default=OFF")
        print(err)
        pass
    except (AttributeError, EOFError, ImportError, IndexError) as e:
        print(e)
        pass
    except Exception as e:
        print(e)
        pass

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    client.connect(MQTT_HOST, MQTT_PORT, 60)

    client.loop_start()
    # see below, not sure if sleep is needed here, probably not
    time.sleep(0.001)

    whitenoise_speakers_offline = check_saved_state_for_resuming(saved_speaker_state)
    print(f"speakers to resume => {whitenoise_speakers_offline}")

    # for first run make it so the last time status check in
    #  is always larger than the delay
    last_time_status_check_in = -1 * status_checkin_delay

    while not exit_monitor.exit_now_flag_raised:
        # added time.sleep 1 ms after seeing 100% CPU usage
        # found this solution https://stackoverflow.com/a/41749754
        time.sleep(0.001)
        current_seconds_count = time.monotonic()
        if (current_seconds_count - last_time_status_check_in) > status_checkin_delay:

            print(f"current_seconds_count={current_seconds_count}")
            print(f"last_time_status_check_in={last_time_status_check_in}")
            print(f"status_checkin_delay={status_checkin_delay}")

            print("start online and resume checkin")
            last_time_status_check_in = current_seconds_count

            print(f"speakers to resume => {whitenoise_speakers_offline}")

            if (
                len(whitenoise_speakers_offline) > 0
                and RETRY_RESUME_ATTEMPT_COUNT < RETRY_RESUME_ON_RESTART_ATTEMPT_LIMIT
            ):
                whitenoise_speakers_offline = resume_speakers_that_were_offline(
                    whitenoise_speakers_offline
                )
                RETRY_RESUME_ATTEMPT_COUNT += 1
            else:
                whitenoise_speakers_offline = []
                RETRY_RESUME_ATTEMPT_COUNT = 0

            for key, speaker in speaker_collection.items():
                client.publish(
                    MQTT_GETONLINE_PATH.format(speaker.mqtt_speaker_name),
                    MQTT_ONLINEVALUE,
                )

    client.loop_stop()
    client.disconnect()
    print("white noise service ended")
