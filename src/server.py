from flask import Flask, request, jsonify, Response, render_template
from flask_cors import CORS
import os
import io
import uuid

from speech2text import Speech2Text
from llm import LLM
from text2speech import Text2Speech

from dotenv import load_dotenv

load_dotenv()
llm_api_key = os.getenv('LLM_API_KEY')
llm_api_url = os.getenv('LLM_API_URL')
llm_model_name = os.getenv('LLM_MODEL_NAME')
ai_name = os.getenv('AI_NAME')
voice_path = os.getenv('WAV_VOICE_FILE_PATH')

speech_to_text = Speech2Text('base')
llm = LLM(ai_name, llm_api_key, llm_api_url, llm_model_name)
text_to_speech = Text2Speech(model_name="AstraMindAI/xttsv2", gpt_model_name='AstraMindAI/xtts2-gpt')

app = Flask(__name__)
CORS(app, supports_credentials=True) 

__transcriptions = {}
TEXT_KEY = 'text'
AUDIO_KEY = 'audio'
STREAM_KEY = 'stream_buffer'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'webm'}

def __allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.get('/')
def home():
    return render_template('index.html')

@app.get('/start')
def start():
    token = str(uuid.uuid4())
    __transcriptions[token] = {}
    return jsonify({"token": token}), 200

@app.post('/transcribe')
def transcribe():
    if 'audio' not in request.files:
        return jsonify({"error": "No file part"}), 400

    audio_file = request.files['audio']

    token = request.form['token']
    language = request.form['language']

    if token == '':
        return jsonify({"error": "Invalid token"}), 400

    if audio_file and __allowed_file(audio_file.filename):
        try:
            audio_buffer = audio_file.stream._file
            if type(audio_buffer) != io.BytesIO:
                raise Exception("Invalid data type")

            transcription = speech_to_text.transcribe(audio_buffer, language)         
            __transcriptions[token][TEXT_KEY] = transcription
            return jsonify({"text": transcription})
        except Exception as e:
            print("Error: ", e)
            return jsonify({"error": "Invalid chunk"}), 400

    return jsonify({"error": "Invalid file"}), 400

@app.post('/finish')
def finish():
    token = request.form['token']
    language = request.form['language']

    print(f"received token is: {token}")
    transcription = __transcriptions[token][TEXT_KEY]
    
    try:
        llm_answer = llm.call(transcription)
    except Exception as e:
        print(e)
        return jsonify({"error": "Cannot connect to llm"}), 400
    
    try:
        answer_audio = text_to_speech.speak_streaming(text=llm_answer, voice_clone_path=voice_path, language=language)
        __transcriptions[token][AUDIO_KEY] = answer_audio
    except Exception as e:
        print(e)
        return jsonify({"error": "Error syntethizing Audio"}), 400    

    return jsonify({
        "text": transcription,
        "answer": llm_answer
    })

@app.get("/stream/<token>")
def streamwav(token):
    try:
        chunk = next(__transcriptions[token][AUDIO_KEY])
    except StopIteration:
        return jsonify({'message': 'ended'}), 300
    return Response(chunk.to_bytes('wav'), mimetype="audio/x-wav", status=200)
