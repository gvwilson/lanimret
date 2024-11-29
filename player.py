"""Replay terminal session with audio."""

from blessed import Terminal
import json
import os
import pyaudio
import sys
import threading
import time
import wave

from util import CHUNK, parse_args


PLAYER_DELAY = 0.01


class SyncPlayer:
    def __init__(self, session_filename, audio_filename):
        self.term = Terminal()
        self.load_session(session_filename)
        self.load_audio(audio_filename)
        self.current_time = 0
        self.playing = False

    def load_session(self, session_filename):
        with open(session_filename, "r") as reader:
            self.events = json.load(reader)
        self.event_index = 0

    def load_audio(self, audio_file):
        self.wf = wave.open(audio_file, "rb")
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.p.get_format_from_width(self.wf.getsampwidth()),
            channels=self.wf.getnchannels(),
            rate=self.wf.getframerate(),
            output=True
        )

    def play_audio(self):
        data = self.wf.readframes(CHUNK)
        while data and self.playing:
            self.stream.write(data)
            data = self.wf.readframes(CHUNK)

    def play_terminal(self):
        with self.term.fullscreen():
            print(self.term.clear + self.term.home, end="", flush=True)
            start_time = time.time()
            
            while self.event_index < len(self.events) and self.playing:
                current_time = time.time() - start_time
                event = self.events[self.event_index]
                timestamp = float(event[0])
                content = event[2]
                if current_time >= timestamp:
                    print(content, end="", flush=True)
                    self.event_index += 1
                else:
                    time.sleep(PLAYER_DELAY)

    def play(self):
        self.playing = True
        terminal_thread = threading.Thread(target=self.play_terminal)
        audio_thread = threading.Thread(target=self.play_audio)
        
        terminal_thread.start()
        audio_thread.start()
        
        try:
            while terminal_thread.is_alive() or audio_thread.is_alive():
                time.sleep(PLAYER_DELAY)
        except KeyboardInterrupt:
            self.playing = False
            terminal_thread.join()
            audio_thread.join()

    def cleanup(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        self.wf.close()


def main():
    session_filename, audio_filename = parse_args()
    player = SyncPlayer(session_filename, audio_filename)
    try:
        player.play()
    finally:
        player.cleanup()


if __name__ == "__main__":
    main()
