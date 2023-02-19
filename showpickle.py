import whitenoise_configparser
import pickle
import configparser

config = configparser.ConfigParser()
config.read("config/config.ini")
config_settings = config["SETTINGS"]

PICKLE_FILE_LOCATION = config_settings.get("PICKLE_FILE_LOCATION")

saved_speaker_state = {}

try:
    with open(PICKLE_FILE_LOCATION, "rb") as datafile:
        saved_speaker_state = pickle.load(datafile)
        print("loaded whitenoise state")
        for key, speaker in saved_speaker_state.items():
            print(f"key:{key}, speaker.is_speaker_on:{speaker.is_speaker_on}")

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
