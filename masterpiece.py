# -*- coding: utf-8 -*-

import json

from midiutil.MidiFile import MIDIFile

from randomnote import RandomNote


class Masterpiece(object):
    def __init__(self, rules_path="rules.json", verse_length=2, chorus_length=2, tempo=90):
        self.rules_path = rules_path
        self.verse_length = verse_length
        self.chorus_length = chorus_length
        self.tempo = tempo

        rules_file = open(rules_path, "r")
        rules = json.load(rules_file)
        rules_file.close()
        self.verse_rhythm = rules["verse_rhythm"]
        self.chorus_rhythm = rules["chorus_rhythm"]
        self.verse_seq_chord = rules["verse_seq_chord"]
        self.chorus_seq_chord = rules["chorus_seq_chord"]
        self.verse_seq_bass = rules["verse_seq_bass"]
        self.chorus_seq_bass = rules["chorus_seq_bass"]
        self.verse_seq_perc = rules["verse_seq_perc"]
        self.chorus_seq_perc = rules["chorus_seq_perc"]
        self.velocity = rules["velocity"]
        self.verse_rn = RandomNote(rules["verse_notes"], rules["interval_upper"], rules["interval_lower"])
        self.chorus_rn = RandomNote(rules["chorus_notes"], rules["interval_upper"], rules["interval_lower"])

        self.MyMIDI = MIDIFile(8)
        self.current_track_number = 0

    def verse_create_melody_sequence(self):
        seq_melody = []
        for i in range(self.verse_length):
            for phrase in self.verse_rhythm:
                self.verse_rn.reset()
                for duration in phrase:
                    seq_melody.append((self.verse_rn.random_note(), duration))
        return seq_melody
    
    def chorus_create_melody_sequence(self):
        seq_melody = []
        for i in range(self.chorus_length):
            for phrase in self.chorus_rhythm:
                self.chorus_rn.reset()
                for duration in phrase:
                    seq_melody.append((self.chorus_rn.random_note(), duration))
        return seq_melody

    def verse_create_melody_track(self):
        seq_melody = self.verse_create_melody_sequence()

        self.MyMIDI.addTrackName(
            track=self.current_track_number,
            time=0, trackName="piano")
        self.MyMIDI.addTempo(
            track=self.current_track_number,
            time=0, tempo=self.tempo)
        self.MyMIDI.addProgramChange(
            tracknum=self.current_track_number,
            channel=0, time=0, program=9)

        pos = 0
        for pitch, duration in seq_melody:
            relative_pos = pos - int(pos / 4) * 4
            if 0 <= relative_pos < 1:
                vol = self.velocity["strong"]
            elif 2 <= relative_pos < 3:
                vol = self.velocity["intermediate"]
            else:
                vol = self.velocity["weak"]
            self.MyMIDI.addNote(
                track=self.current_track_number,
                channel=0, pitch=pitch, time=pos, duration=duration, volume=vol)
            if relative_pos in [0, 2]:
                self.MyMIDI.addControllerEvent(
                    track=self.current_track_number,
                    channel=0, time=pos, controller_number=64, parameter=127)
                self.MyMIDI.addControllerEvent(
                    track=self.current_track_number,
                    channel=0, time=pos + 1.96875, controller_number=64, parameter=0)
            self.MyMIDI.addNote(
                track=self.current_track_number,
                channel=0, pitch=pitch, time=pos + self.chorus_length * 16 + self.verse_length * 16, duration=duration, volume=vol)
            if relative_pos in [0, 2]:
                self.MyMIDI.addControllerEvent(
                    track=self.current_track_number,
                    channel=0, time=pos + self.chorus_length * 16 + self.verse_length * 16, controller_number=64, parameter=127)
                self.MyMIDI.addControllerEvent(
                    track=self.current_track_number,
                    channel=0, time=pos + 1.96875 + self.chorus_length * 16 + self.verse_length * 16, controller_number=64, parameter=0)
            pos += duration
        self.current_track_number += 1
        
    def chorus_create_melody_track(self):
        seq_melody = self.chorus_create_melody_sequence()

        self.MyMIDI.addTrackName(
            track=self.current_track_number,
            time=0, trackName="piano")
        self.MyMIDI.addTempo(
            track=self.current_track_number,
            time=0, tempo=self.tempo)
        self.MyMIDI.addProgramChange(
            tracknum=self.current_track_number,
            channel=0, time=0, program=9)

        pos = self.verse_length * 16
        for pitch, duration in seq_melody:
            relative_pos = pos - int(pos / 4) * 4
            if 0 <= relative_pos < 1:
                vol = self.velocity["strong"]
            elif 2 <= relative_pos < 3:
                vol = self.velocity["intermediate"]
            else:
                vol = self.velocity["weak"]
            self.MyMIDI.addNote(
                track=self.current_track_number,
                channel=0, pitch=pitch, time=pos, duration=duration, volume=vol)
            if relative_pos in [0, 2]:
                self.MyMIDI.addControllerEvent(
                    track=self.current_track_number,
                    channel=0, time=pos, controller_number=64, parameter=127)
                self.MyMIDI.addControllerEvent(
                    track=self.current_track_number,
                    channel=0, time=pos + 1.96875, controller_number=64, parameter=0)
            self.MyMIDI.addNote(
                track=self.current_track_number,
                channel=0, pitch=pitch, time=pos + self.verse_length * 16 + self.chorus_length * 16, duration=duration, volume=vol)
            if relative_pos in [0, 2]:
                self.MyMIDI.addControllerEvent(
                    track=self.current_track_number,
                    channel=0, time=pos + self.verse_length * 16 + self.chorus_length * 16, controller_number=64, parameter=127)
                self.MyMIDI.addControllerEvent(
                    track=self.current_track_number,
                    channel=0, time=pos + 1.96875 + self.verse_length * 16 + self.chorus_length * 16, controller_number=64, parameter=0)
            pos += duration
        self.current_track_number += 1

    def verse_create_chord_track(self):
        self.MyMIDI.addTrackName(
            track=self.current_track_number,
            time=0, trackName="chords")
        self.MyMIDI.addTempo(
            track=self.current_track_number,
            time=0, tempo=self.tempo)
        self.MyMIDI.addProgramChange(
            tracknum=self.current_track_number,
            channel=1, time=0, program=0)

        # C  D  E  F  G  A  B  | C  D  E  F  G  A  B  | C
        # 48 50 52 53 55 57 59 | 60 62 64 65 67 69 71 | 72

        pos = 0
        while pos < self.verse_length * 16:
            for item in self.verse_seq_chord:
                delay = 0
                for pitch in item:
                    # VERSE 1-2
                    self.MyMIDI.addControllerEvent(
                        track=self.current_track_number,
                        channel=1, time=pos, controller_number=64, parameter=127)
                    self.MyMIDI.addControllerEvent(
                        track=self.current_track_number,
                        channel=1, time=pos + 3.96875, controller_number=64, parameter=0)
                    self.MyMIDI.addNote(
                        track=self.current_track_number,
                        channel=1, pitch=pitch, time=pos + delay, duration=4 - delay, volume=76)
                    # VERSE 3-4
                    self.MyMIDI.addControllerEvent(
                        track=self.current_track_number,
                        channel=1, time=pos + self.verse_length * 16 + self.chorus_length * 16, controller_number=64, parameter=127)
                    self.MyMIDI.addControllerEvent(
                        track=self.current_track_number,
                        channel=1, time=pos + 3.96875 + self.verse_length * 16 + self.chorus_length * 16, controller_number=64, parameter=0)
                    self.MyMIDI.addNote(
                        track=self.current_track_number,
                        channel=1, pitch=pitch, time=pos + delay + self.verse_length * 16 + self.chorus_length * 16, duration=4 - delay, volume=76)
                    delay += 1
                pos += 4
        self.current_track_number += 1
        
    def chorus_create_chord_track(self):
        self.MyMIDI.addTrackName(
            track=self.current_track_number,
            time=0, trackName="chords")
        self.MyMIDI.addTempo(
            track=self.current_track_number,
            time=0, tempo=self.tempo)
        self.MyMIDI.addProgramChange(
            tracknum=self.current_track_number,
            channel=1, time=0, program=0)

        # C  D  E  F  G  A  B  | C  D  E  F  G  A  B  | C
        # 48 50 52 53 55 57 59 | 60 62 64 65 67 69 71 | 72

        pos = self.verse_length * 16
        while pos < self.chorus_length * 16 + self.verse_length * 16:
            for item in self.chorus_seq_chord:
                delay = 0
                for pitch in item:
                    # CHORUS 1-2
                    self.MyMIDI.addControllerEvent(
                        track=self.current_track_number,
                        channel=1, time=pos, controller_number=64, parameter=127)
                    self.MyMIDI.addControllerEvent(
                        track=self.current_track_number,
                        channel=1, time=pos + 3.96875, controller_number=64, parameter=0)
                    self.MyMIDI.addNote(
                        track=self.current_track_number,
                        channel=1, pitch=pitch, time=pos + delay, duration=4 - delay, volume=76)
                    # CHORUS 3-4
                    self.MyMIDI.addControllerEvent(
                        track=self.current_track_number,
                        channel=1, time=pos + self.verse_length * 16 + self.chorus_length * 16, controller_number=64, parameter=127)
                    self.MyMIDI.addControllerEvent(
                        track=self.current_track_number,
                        channel=1, time=pos + 3.96875 + self.verse_length * 16 + self.chorus_length * 16, controller_number=64, parameter=0)
                    self.MyMIDI.addNote(
                        track=self.current_track_number,
                        channel=1, pitch=pitch, time=pos + delay + self.verse_length * 16 + self.chorus_length * 16, duration=4 - delay, volume=76)
                    delay += 1
                pos += 4
        self.current_track_number += 1
        
    def verse_create_bass_track(self):
        self.MyMIDI.addTrackName(
            track=self.current_track_number,
            time=0, trackName="bass")
        self.MyMIDI.addTempo(
            track=self.current_track_number,
            time=0, tempo=self.tempo)
        self.MyMIDI.addProgramChange(
            tracknum=self.current_track_number,
            channel=2, time=0, program=32)

        # C  D  E  F  G  A  B  | C  D  E  F  G  A  B  | C
        # 48 50 52 53 55 57 59 | 60 62 64 65 67 69 71 | 72

        pos = 0
        while pos < self.verse_length * 16:
            for item in self.verse_seq_bass:
                for pitch in item:
                    # VERSE 1-2
                    self.MyMIDI.addControllerEvent(
                        track=self.current_track_number,
                        channel=2, time=pos, controller_number=64, parameter=127)
                    self.MyMIDI.addControllerEvent(
                        track=self.current_track_number,
                        channel=2, time=pos + 1.96875, controller_number=64, parameter=0)
                    self.MyMIDI.addNote(
                        track=self.current_track_number,
                        channel=2, pitch=pitch, time=pos, duration=2, volume=76)
                    self.MyMIDI.addControllerEvent(
                        track=self.current_track_number,
                        channel=2, time=pos + 2, controller_number=64, parameter=127)
                    self.MyMIDI.addControllerEvent(
                        track=self.current_track_number,
                        channel=2, time=pos + 3.96875, controller_number=64, parameter=0)
                    self.MyMIDI.addNote(
                        track=self.current_track_number,
                        channel=2, pitch=pitch, time=pos + 2, duration=2, volume=68)
                    # VERSE 3-4
                    self.MyMIDI.addControllerEvent(
                        track=self.current_track_number,
                        channel=2, time=pos + self.verse_length * 16 + self.chorus_length * 16, controller_number=64, parameter=127)
                    self.MyMIDI.addControllerEvent(
                        track=self.current_track_number,
                        channel=2, time=pos + 1.96875 + self.verse_length * 16 + self.chorus_length * 16, controller_number=64, parameter=0)
                    self.MyMIDI.addNote(
                        track=self.current_track_number,
                        channel=2, pitch=pitch, time=pos + self.verse_length * 16 + self.chorus_length * 16, duration=2, volume=76)
                    self.MyMIDI.addControllerEvent(
                        track=self.current_track_number,
                        channel=2, time=pos + 2 + self.verse_length * 16 + self.chorus_length * 16, controller_number=64, parameter=127)
                    self.MyMIDI.addControllerEvent(
                        track=self.current_track_number,
                        channel=2, time=pos + 3.96875 + self.verse_length * 16 + self.chorus_length * 16, controller_number=64, parameter=0)
                    self.MyMIDI.addNote(
                        track=self.current_track_number,
                        channel=2, pitch=pitch, time=pos + 2 + self.verse_length * 16 + self.chorus_length * 16, duration=2, volume=68)
                pos += 4
        self.current_track_number += 1
        
    def chorus_create_bass_track(self):
        self.MyMIDI.addTrackName(
            track=self.current_track_number,
            time=0, trackName="bass")
        self.MyMIDI.addTempo(
            track=self.current_track_number,
            time=0, tempo=self.tempo)
        self.MyMIDI.addProgramChange(
            tracknum=self.current_track_number,
            channel=2, time=0, program=32)

        # C  D  E  F  G  A  B  | C  D  E  F  G  A  B  | C
        # 48 50 52 53 55 57 59 | 60 62 64 65 67 69 71 | 72

        pos = self.verse_length * 16
        while pos < self.chorus_length * 16 + self.verse_length * 16:
            for item in self.chorus_seq_bass:
                for pitch in item:
                    # CHORUS 1-2
                    self.MyMIDI.addControllerEvent(
                        track=self.current_track_number,
                        channel=2, time=pos, controller_number=64, parameter=127)
                    self.MyMIDI.addControllerEvent(
                        track=self.current_track_number,
                        channel=2, time=pos + 1.96875, controller_number=64, parameter=0)
                    self.MyMIDI.addNote(
                        track=self.current_track_number,
                        channel=2, pitch=pitch, time=pos, duration=2, volume=76)
                    self.MyMIDI.addControllerEvent(
                        track=self.current_track_number,
                        channel=2, time=pos + 2, controller_number=64, parameter=127)
                    self.MyMIDI.addControllerEvent(
                        track=self.current_track_number,
                        channel=2, time=pos + 3.96875, controller_number=64, parameter=0)
                    self.MyMIDI.addNote(
                        track=self.current_track_number,
                        channel=2, pitch=pitch, time=pos + 2, duration=2, volume=68)
                    # CHORUS 3-4
                    self.MyMIDI.addControllerEvent(
                        track=self.current_track_number,
                        channel=2, time=pos + self.verse_length * 16 + self.chorus_length * 16, controller_number=64, parameter=127)
                    self.MyMIDI.addControllerEvent(
                        track=self.current_track_number,
                        channel=2, time=pos + 1.96875 + self.verse_length * 16 + self.chorus_length * 16, controller_number=64, parameter=0)
                    self.MyMIDI.addNote(
                        track=self.current_track_number,
                        channel=2, pitch=pitch, time=pos + self.verse_length * 16 + self.chorus_length * 16, duration=2, volume=76)
                    self.MyMIDI.addControllerEvent(
                        track=self.current_track_number,
                        channel=2, time=pos + 2 + self.verse_length * 16 + self.chorus_length * 16, controller_number=64, parameter=127)
                    self.MyMIDI.addControllerEvent(
                        track=self.current_track_number,
                        channel=2, time=pos + 3.96875 + self.verse_length * 16 + self.chorus_length * 16, controller_number=64, parameter=0)
                    self.MyMIDI.addNote(
                        track=self.current_track_number,
                        channel=2, pitch=pitch, time=pos + 2 + self.verse_length * 16 + self.chorus_length * 16, duration=2, volume=68)
                pos += 4
        self.current_track_number += 1

    def verse_create_perc_track(self):
        self.MyMIDI.addTrackName(
            track=self.current_track_number,
            time=0, trackName="perc")
        self.MyMIDI.addTempo(
            track=self.current_track_number,
            time=0, tempo=self.tempo)
        self.MyMIDI.addProgramChange(
            tracknum=self.current_track_number,
            channel=9, time=0, program=0)

        pos = 0
        while pos < self.verse_length * 16:
            if pos != 0:
                # VERSE 1-2
                self.MyMIDI.addNote(
                    track=self.current_track_number,
                    channel=9, pitch=49, time=pos, duration=0.5, volume=102)
                # VERSE 3-4
                self.MyMIDI.addNote(
                    track=self.current_track_number,
                    channel=9, pitch=49, time=pos + self.verse_length * 16 + self.chorus_length * 16, duration=0.5, volume=102)
            for pitch, duration in self.verse_seq_perc:
                relative_pos = pos - int(pos / 4) * 4
                if 0 <= relative_pos < 1:
                    vol = 102
                elif 2 <= relative_pos < 3:
                    vol = 96
                else:
                    vol = 92
                # VERSE 1-2
                self.MyMIDI.addNote(
                    track=self.current_track_number,
                    channel=9, pitch=pitch, time=pos, duration=duration, volume=vol)
                # VERSE 3-4
                self.MyMIDI.addNote(
                    track=self.current_track_number,
                    channel=9, pitch=pitch, time=pos + self.verse_length * 16 + self.chorus_length * 16, duration=duration, volume=vol)
                pos += duration
        self.current_track_number += 1
        
    def chorus_create_perc_track(self):
        self.MyMIDI.addTrackName(
            track=self.current_track_number,
            time=0, trackName="perc")
        self.MyMIDI.addTempo(
            track=self.current_track_number,
            time=0, tempo=self.tempo)
        self.MyMIDI.addProgramChange(
            tracknum=self.current_track_number,
            channel=9, time=0, program=0)

        pos = self.verse_length * 16
        while pos < self.chorus_length * 16 + self.verse_length * 16:
            if pos != 0:
                # CHORUS 1-2
                self.MyMIDI.addNote(
                    track=self.current_track_number,
                    channel=9, pitch=49, time=pos, duration=0.5, volume=102)
                # CHORUS 3-4
                self.MyMIDI.addNote(
                    track=self.current_track_number,
                    channel=9, pitch=49, time=pos + self.verse_length * 16 + self.chorus_length * 16, duration=0.5, volume=102)
            for pitch, duration in self.chorus_seq_perc:
                relative_pos = pos - int(pos / 4) * 4
                if 0 <= relative_pos < 1:
                    vol = 102
                elif 2 <= relative_pos < 3:
                    vol = 96
                else:
                    vol = 92
                # CHORUS 1-2
                self.MyMIDI.addNote(
                    track=self.current_track_number,
                    channel=9, pitch=pitch, time=pos, duration=duration, volume=vol)
                # CHORUS 3-4
                self.MyMIDI.addNote(
                    track=self.current_track_number,
                    channel=9, pitch=pitch, time=pos + self.verse_length * 16 + self.chorus_length * 16, duration=duration, volume=vol)
                pos += duration
        self.current_track_number += 1

    def create_midi_file(self, filename, melody=False, chord=True, perc=True, bass=True):
        if melody:
            self.verse_create_melody_track()
            self.chorus_create_melody_track()
        if chord:
            self.verse_create_chord_track()
            self.chorus_create_chord_track()
        if perc:
            self.verse_create_perc_track()
            self.chorus_create_perc_track()
        if bass:
            self.verse_create_bass_track()
            self.chorus_create_bass_track()
        with open(filename, "wb") as midi_file:
            self.MyMIDI.writeFile(midi_file)
