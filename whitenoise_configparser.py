class Speaker:
    mqtt_speaker_name = ""
    sonos_speaker_name = ""
    is_speaker_on = False
    volume_on = 40
    volume_off = 20


def get_speakers_from_config_section(config_section):
    speaker_collection = {}
    for individual_config_key in config_section:
        line = config_section.get(individual_config_key)
        config_line_parts = line.strip().split(",")

        mqtt_speaker_name = config_line_parts[0].strip()
        sonos_speaker_name = config_line_parts[1].strip()
        volume_on = int(config_line_parts[2].strip())
        volume_off = int(config_line_parts[3].strip())

        speaker = Speaker()
        speaker.mqtt_speaker_name = mqtt_speaker_name
        speaker.sonos_speaker_name = sonos_speaker_name
        speaker.volume_on = volume_on
        speaker.volume_off = volume_off

        speaker_collection[mqtt_speaker_name] = speaker
    return speaker_collection
