import os
import requests

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
    try:
        r = requests.get(url)
        json = r.json()
    except:
        pass
    return json

def sonos_whitenoise_is_on(sonos_player):
    try:
        json = sonos_api_call(f"[{sonos_player}] get state", f"{SONOS_API_URL}/{sonos_player}/state")
        if json["playbackState"] == "PLAYING" and json["currentTrack"]["title"] == WHITE_NOISE_TRACK_TITLE:
            return True
        else:
            return False
    except:
        return False

def sonos_whitenoise_start(speaker, volume = 40):
    sonos_api_call(f"[{speaker}] pause", f"{SONOS_API_URL}/{speaker}/pause")
    sonos_api_call(f"[{speaker}] ungroup", f"{SONOS_API_URL}/{speaker}/leave")
    sonos_api_call(f"[{speaker}] set volume", f"{SONOS_API_URL}/{speaker}/volume/{volume}")
    sonos_api_call(f"[{speaker}] unmute", f"{SONOS_API_URL}/{speaker}/unmute")
    sonos_api_call(f"[{speaker}] start Sleep playlist", f"{SONOS_API_URL}/{speaker}/playlist/Sleep")

def sonos_whitenoise_stop(speaker, volume = 20):
    sonos_api_call(f"[{speaker}] pause", f"{SONOS_API_URL}/{speaker}/pause")
    sonos_api_call(f"[{speaker}] set volume", f"{SONOS_API_URL}/{speaker}/volume/{volume}")
