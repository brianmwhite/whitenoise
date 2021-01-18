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
WHITE_NOISE_TRACK_TITLE = "Beach with Cross Fade"

def sonos_api_call(action, url):
    json = "{}"
    try:
        r = requests.get(url)
        # print(f"{action}={r.json()}")
        json = r.json()
    except:
        pass
    return json

def sonos_api_check_if_beachisplaying(sonos_player):
    try:
        json = sonos_api_call(f"[{sonos_player}] get state", f"{SONOS_API_URL}/{sonos_player}/state")
        if json["playbackState"] == "PLAYING" and json["currentTrack"]["title"] == WHITE_NOISE_TRACK_TITLE:
            return True
        else:
            return False
    except:
        return False

def sonos_get_white_noise_state_owen():
    if sonos_api_check_if_beachisplaying(SONOS_OWENS_ROOM):
        return '{"white_noise_on":true}'
    else:
        return '{"white_noise_on":false}'

def sonos_sleep_owen():
    sonos_api_call("[owen's room] pause", f"{SONOS_API_URL}/{SONOS_OWENS_ROOM}/pause")
    sonos_api_call("[owen's room] ungroup", f"{SONOS_API_URL}/{SONOS_OWENS_ROOM}/leave")
    sonos_api_call("[owen's room] set volume", f"{SONOS_API_URL}/{SONOS_OWENS_ROOM}/volume/60")
    sonos_api_call("[owen's room] start Sleep playlist", f"{SONOS_API_URL}/{SONOS_OWENS_ROOM}/playlist/Sleep")
    return '{"status":"success"}'

def sonos_wake_owen():
    sonos_api_call("[owen's room] ungroup", f"{SONOS_API_URL}/{SONOS_OWENS_ROOM}/leave")
    sonos_api_call("[owen's room] pause", f"{SONOS_API_URL}/{SONOS_OWENS_ROOM}/pause")
    sonos_api_call("[owen's room] set volume", f"{SONOS_API_URL}/{SONOS_OWENS_ROOM}/volume/20")
    return '{"status":"success"}'

def sonos_get_white_noise_state_bedroom():
    if sonos_api_check_if_beachisplaying(SONOS_BEDROOM):
        return '{"white_noise_on":true}'
    else:
        return '{"white_noise_on":false}'

def sonos_sleep_bedroom():
    sonos_api_call("[bedroom] pause", f"{SONOS_API_URL}/{SONOS_BEDROOM}/pause")       
    sonos_api_call("[bedroom] ungroup", f"{SONOS_API_URL}/{SONOS_BEDROOM}/leave")
    sonos_api_call("[bedroom] set volume", f"{SONOS_API_URL}/{SONOS_BEDROOM}/volume/40")
    sonos_api_call("[bedroom/group] start Sleep playlist", f"{SONOS_API_URL}/{SONOS_BEDROOM}/playlist/Sleep")
    return '{"status":"success"}'

def sonos_wake_bedroom():
    sonos_api_call("[bedroom] pause", f"{SONOS_API_URL}/{SONOS_BEDROOM}/pause")
    sonos_api_call("[bedroom] set volume", f"{SONOS_API_URL}/{SONOS_BEDROOM}/volume/20")
    return '{"status":"success"}'