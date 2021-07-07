import os
import sys
import time

import requests
import requests.exceptions

# jishi / node-sonos-http-api
# https://github.com/jishi/node-sonos-http-api

SONOS_API_IP = os.environ["SONOS_API_IP"]
SONOS_API_URL = f"http://{SONOS_API_IP}"

SONOS_OWENS_ROOM = "Owen%E2%80%99s%20Room"
SONOS_BEDROOM = "Bedroom"
SONOS_LIVINGROOM = "Living%20Room"
SONOS_OFFICE = "Office"
SONOS_BASEMENT = "Downstairs"

WHITE_NOISE_TRACK_TITLE = "Beach with Cross Fade"


def sonos_api_call(action, url):
    json = "{}"
    # try:
    r = requests.get(url)
    json = r.json()
    if check_for_error(json):
        raise requests.exceptions.ConnectionError("Sonos speaker is offline")
    # except Exception:
        # print(sys.exc_info()[0])
        # pass
    return json


def check_for_error(json_response):
    error = False
    if json_response["status"] == "error":
        error = True
        print(json_response["error"])
        if str(json_response["error"]).startswith("") == "connect EHOSTUNREACH":
            print("Sonos speaker is offline")
    return error


def sonos_whitenoise_is_on(sonos_player):
    try:
        json = sonos_api_call(f"[{sonos_player}] get state", f"{SONOS_API_URL}/{sonos_player}/state")
        if json["playbackState"] == "PLAYING" and json["currentTrack"]["title"] == WHITE_NOISE_TRACK_TITLE:
            return True
        else:
            return False
    except Exception:
        print(sys.exc_info()[0])
        return False

# {
#     "status": "error",
#     "error": "connect EHOSTUNREACH 192.168.7.168:1400",
#     "stack": "Error: connect EHOSTUNREACH 192.168.7.168:1400\n    at TCPConnectWrap.afterConnect [as oncomplete] (node:net:1138:16)"
# }


def sonos_whitenoise_start(speaker, volume=40):
    sonos_api_call(f"[{speaker}] pause", f"{SONOS_API_URL}/{speaker}/pause")
    sonos_api_call(f"[{speaker}] ungroup", f"{SONOS_API_URL}/{speaker}/leave")
    time.sleep(2)
    sonos_api_call(f"[{speaker}] set volume", f"{SONOS_API_URL}/{speaker}/volume/{volume}")
    sonos_api_call(f"[{speaker}] unmute", f"{SONOS_API_URL}/{speaker}/unmute")
    sonos_api_call(f"[{speaker}] start Sleep playlist", f"{SONOS_API_URL}/{speaker}/playlist/Sleep")


def sonos_whitenoise_stop(speaker, volume=20):
    sonos_api_call(f"[{speaker}] pause", f"{SONOS_API_URL}/{speaker}/pause")
    sonos_api_call(f"[{speaker}] set volume", f"{SONOS_API_URL}/{speaker}/volume/{volume}")
