import time

import requests
import requests.exceptions

# jishi / node-sonos-http-api
# https://github.com/jishi/node-sonos-http-api


def sonos_api_call(action, url):
    json = "{}"
    # try:
    r = requests.get(url)
    json = r.json()
    if check_for_error(json):
        raise requests.exceptions.ConnectionError("Sonos speaker is offline")
    return json


def check_for_error(json_response):
    error = False
    # also check if json response is not empty
    if not json_response:
        error = True
        print("Empty JSON error response")
    else:
        status = json_response.get("status")
        error_message = json_response.get("error")
        if status and status == "error":
            # could instead check to see the player state is before blindly
            # calling specific methods like pause
            # pause will throw an error if the player has no queue
            if error_message and str(error_message).startswith(
                "Got status 500 when invoking /MediaRenderer/AVTransport/Control"
            ):
                print(error_message)
            elif error_message and str(error).startswith("connect EHOSTUNREACH"):
                error = True
                print("Sonos speaker is offline")
            else:
                error = True
                print(json_response)

    return error


def sonos_whitenoise_start(sonos_api_url, playlist_name, speaker, volume=40):
    # pause will throw an error if the player has no queue
    sonos_api_call(f"[{speaker}] pause", f"{sonos_api_url}/{speaker}/pause")
    sonos_api_call(f"[{speaker}] ungroup", f"{sonos_api_url}/{speaker}/leave")
    time.sleep(2)
    sonos_api_call(
        f"[{speaker}] set volume", f"{sonos_api_url}/{speaker}/volume/{volume}"
    )
    sonos_api_call(f"[{speaker}] unmute", f"{sonos_api_url}/{speaker}/unmute")
    sonos_api_call(
        f"[{speaker}] start {playlist_name} playlist",
        f"{sonos_api_url}/{speaker}/playlist/{playlist_name}",
    )
    time.sleep(1)
    sonos_api_call(f"[{speaker}] play", f"{sonos_api_url}/{speaker}/play")


def sonos_whitenoise_stop(sonos_api_url, speaker, volume=20):
    sonos_api_call(f"[{speaker}] pause", f"{sonos_api_url}/{speaker}/pause")
    sonos_api_call(
        f"[{speaker}] set volume", f"{sonos_api_url}/{speaker}/volume/{volume}"
    )


# def sonos_whitenoise_is_on(sonos_player):
#     try:
#         json = sonos_api_call(
#             f"[{sonos_player}] get state", f"{SONOS_API_URL}/{sonos_player}/state"
#         )
#         if (
#             json["playbackState"] == "PLAYING"
#             and json["currentTrack"]["title"] == WHITE_NOISE_TRACK_TITLE
#         ):
#             return True
#         else:
#             return False
#     except Exception:
#         print(sys.exc_info()[0])
#         return False
