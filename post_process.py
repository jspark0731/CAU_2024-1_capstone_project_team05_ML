import xml.etree.ElementTree as ET

def post_process(xml_file, reference_pitch):
        # XML 파일 로드
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # MusicXML 파일에서 pitch 정보를 가지는 모든 note 요소 찾기
        notes_to_remove = []
        for note in root.findall('.//note'):
                pitch = note.find('pitch')
                if pitch is not None:
                        step = pitch.find('step').text
                        alter = pitch.find('alter')
                        if alter is not None:
                                alter = int(alter.text)
                        else:
                                alter = 0
                        octave = int(pitch.find('octave').text)

                        # 음 높이를 생성 (예: 'D#3')
                        full_pitch = f"{step}{alter:+d}" if alter != 0 else step + str(octave)

                        if is_higher(full_pitch, reference_pitch):
                                notes_to_remove.append(note)

        # 기준음보다 높은 음 제거
        for note in notes_to_remove:
                root.remove(note)

        # 변경된 XML 파일 저장
        tree.write('output_post_processed.xml')


def is_higher(pitch, reference):
        # 음 높이 비교 함수
        pitch_order = {'C': 0, 'C#': 1, 'D-': 1, 'D': 2, 'D#': 3, 'E-': 3, 'E': 4, 'F': 5, 'F#': 6, 'G-': 6, 'G': 7,
                       'G#': 8, 'A-': 8, 'A': 9, 'A#': 10, 'B-': 10, 'B': 11}
        pitch_octave = int(pitch[-1])
        ref_octave = int(reference[-1])
        pitch_note = pitch[:-1]
        ref_note = reference[:-1]

        if pitch_octave > ref_octave:
                return True
        elif pitch_octave == ref_octave:
                return pitch_order[pitch_note] > pitch_order[ref_note]
        return False
