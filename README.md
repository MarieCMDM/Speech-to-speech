# Speech-to-speech
Python speech-to-speech webapp, uning openai compatible apis for llm

## Voice
Create a voice to sysntetize inm a wav file and puth the path of the file in the `.env` file

## Installation
You will need PortAudio (libportaudio.so.2) for auralis.
Install it with `sudo apt-get install libportaudio2`

## install pip requirements
`pip install -r requirements.txt`

## Start
`python3 run.py`

## .env file structure
```bash
LLM_API_KEY=
LLM_API_URL=
LLM_MODEL_NAME=
AI_NAME=
WAV_VOICE_FILE_PATH=
```

