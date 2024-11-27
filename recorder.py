#!/usr/bin/env python3
import subprocess
import threading
import time
import json
import wave
import pyaudio
import os

class TerminalRecorder:
    def __init__(self):
        self.recording = False
        self.terminal_output = []
        self.start_time = None

    def record_terminal(self):
        process = subprocess.Popen(['asciinema', 'rec', '-'], 
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True)
        self.start_time = time.time()
        
        while self.recording:
            line = process.stdout.readline()
            if line:
                timestamp = time.time() - self.start_time
                self.terminal_output.append([timestamp, line])
        process.terminate()

    def record_audio(self, filename="audio.wav"):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100

        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       frames_per_buffer=CHUNK)

        frames = []
        while self.recording:
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

    def save_session(self, output_file="session.json"):
        session_data = {
            "version": 2,
            "width": 80,
            "height": 24,
            "timestamp": int(self.start_time),
            "events": self.terminal_output
        }
        with open(output_file, 'w') as f:
            json.dump(session_data, f)

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
        self.save_session()

def main():
    recorder = TerminalRecorder()
    print("Recording started. Press Ctrl+C to stop.")
    try:
        recorder.start_recording()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        recorder.stop_recording()
        print("Recording stopped. Session saved.")

if __name__ == "__main__":
    main()
