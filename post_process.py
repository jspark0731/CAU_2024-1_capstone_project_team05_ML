import xml.etree.ElementTree as ET
from collections import Counter
import logging

# 로깅 설정
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def post_process(xml_file_path, instrument_type):
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Collect all octave and step data to determine the most common octave and step
    pitch_data = [(int(note.find('pitch/octave').text), note.find('pitch/step').text) for note in root.findall('.//note/pitch')]
    octave_counter = Counter([data[0] for data in pitch_data])
    most_common_octave = octave_counter.most_common(1)[0][0]
    step_counter = Counter([step for octave, step in pitch_data if octave == most_common_octave])
    most_common_step = step_counter.most_common(1)[0][0]

    # Log the most common octave and step
    logging.info(f"Most common octave: {most_common_octave}")
    logging.info(f"Most common step: {most_common_step}")

    # Determine the pitches for removal based on instrument type
    notes_to_remove = []
    for note in root.findall('.//note'):
        pitch = note.find('pitch')
        if pitch is not None:
            octave = int(pitch.find('octave').text)
            step = pitch.find('step').text
            if instrument_type == 'bass' and is_higher(step, octave, most_common_step, most_common_octave):
                notes_to_remove.append(note)
                logging.debug(f"Removing higher note: {step}{octave}")
            elif instrument_type == 'guitar' and is_lower(step, octave, most_common_step, most_common_octave):
                notes_to_remove.append(note)
                logging.debug(f"Removing lower note: {step}{octave}")

    # Log the total number of notes removed
    logging.info(f"Total notes removed: {len(notes_to_remove)}")

    # Remove notes
    for note in notes_to_remove:
        root.remove(note)

    return ET.tostring(root, encoding='unicode')

def is_higher(step, octave, ref_step, ref_octave):
    return semitone_distance(step, octave, ref_step, ref_octave) > 12  # 1 octave in semitones

def is_lower(step, octave, ref_step, ref_octave):
    return semitone_distance(step, octave, ref_step, ref_octave) < -18  # 1 octave in semitones

def semitone_distance(step, octave, ref_step, ref_octave):
    note_values = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}
    semitones = (octave - ref_octave) * 12 + (note_values[step] - note_values[ref_step])
    logging.debug(f"Semitone distance between {step}{octave} and {ref_step}{ref_octave}: {semitones}")
    return semitones

# # 예제 사용
# xml_data = post_process("path/to/your/music.xml", "guitar")
