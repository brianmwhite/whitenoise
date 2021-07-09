from collections import namedtuple
Speaker = namedtuple('Speaker', 'mqtt_speaker_name sonos_speaker_name is_speaker_on')


def get_speakers_from_config_section(config_section):
    speaker_collection = {}
    for individual_config_key in config_section:
        line = config_section.get(individual_config_key)
        config_line_parts = line.strip().split(",")

        mqtt_speaker_name = config_line_parts[0].strip()
        sonos_speaker_name = config_line_parts[1].strip()
        speaker_default_is_speaker_on = False

        speaker_collection[mqtt_speaker_name] = Speaker(mqtt_speaker_name, sonos_speaker_name, speaker_default_is_speaker_on)
    return speaker_collection
