"""Utilities."""

import argparse

CHUNK = 1024


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("stem", help="output filename stem")
    options = parser.parse_args()
    session_filename = f"{options.stem}.json"
    audio_filename = f"{options.stem}.wav"
    return session_filename, audio_filename
