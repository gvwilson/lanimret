"""Record terminal session with audio."""

import json
import os
import pyaudio
import subprocess
import sys
import threading
import time
import wave

from util import CHUNK, parse_args


CHANNELS = 1
FORMAT = pyaudio.paInt16
RATE = 44100


class TerminalRecorder:
    def __init__(self, session_filename, audio_filename):
        self.session_filename = session_filename
        self.audio_filename = audio_filename
        self.recording = False

    def record_terminal(self):
        process = subprocess.Popen(
            ["asciinema", "rec", "-"], 
            stdout=subprocess.PIPE,
            universal_newlines=True
        )
        terminal_output = []
        while self.recording:
            line = process.stdout.readline()
            if line:
                terminal_output.append(json.loads(line))
        process.terminate()
        with open(self.session_filename, "w") as writer:
            json.dump(terminal_output[1:], writer)

    def record_audio(self):
        p = pyaudio.PyAudio()
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )

        frames = []
        while self.recording:
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(self.audio_filename, "wb")
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b"".join(frames))
        wf.close()

    def start_recording(self):
        self.recording = True
        self.terminal_thread = threading.Thread(target=self.record_terminal)
        self.audio_thread = threading.Thread(target=self.record_audio)
        self.terminal_thread.start()
        self.audio_thread.start()

    def stop_recording(self):
        self.recording = False
        self.terminal_thread.join()
        self.audio_thread.join()


def main():
    session_filename, audio_filename = parse_args()
    recorder = TerminalRecorder(session_filename, audio_filename)
    print("Recording started. Press <ctrl-c> after asciinema exits.")
    try:
        recorder.start_recording()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        recorder.stop_recording()
        print("Recording stopped.")


if __name__ == "__main__":
    main()
