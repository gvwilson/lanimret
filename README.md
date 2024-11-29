# Terminal Replay

## Setup

1.  `brew install portaudio`
1.  `uv venv` and activate
1.  `uv pip install -r requirements.txt`

## Use

1.  `python recorder.py temp` will create `temp.json` (terminal recording) and `temp.wav` (audio recording).
    -   Note: when you are done recording, press Ctrl-D to exit asciinema and then Ctrl-C to exit the recorder.
2.  `python player.py temp` will replay the session.
