from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import io
import uuid
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()
llm_api_key = os.getenv('LLM_API_KEY')
llm_api_url = os.getenv('LLM_API_URL')
llm_model_name = os.getenv('LLM_MODEL_NAME')
ai_name = os.getenv('AI_NAME')

from speech2text import Speech2Text
speech_to_text = Speech2Text('base')

from llm import LLM
llm = LLM(ai_name, llm_api_key, llm_api_url, llm_model_name)

from text2speech import Text2Speech
text_to_speech = Text2Speech(model_name="AstraMindAI/xttsv2", gpt_model_name='AstraMindAI/xtts2-gpt')

app = Flask(__name__)
CORS(app, supports_credentials=True) 

__transcriptions = {}

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'webm'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def call_speech_to_text(audio_file, language: str) -> str:
    audio_buffer = audio_file.stream._file
    if type(audio_buffer) != io.BytesIO:
        raise Exception("Invalid data type")

    try:
        transcription = speech_to_text.transcribe(audio_buffer, language)
        return transcription
    except Exception as e:
        raise e
    
@app.get('/s2s_bend/start',)
def start():
    token = str(uuid.uuid4())
    __transcriptions[token] = ''
    return jsonify({"token": token}), 200

@app.post('/s2s_bend/transcribe')
def transcribe():
    if 'audio' not in request.files:
        return jsonify({"error": "No file part"}), 400

    audio_file = request.files['audio']
    token = request.form['token']
    language = 'it'
    if audio_file and allowed_file(audio_file.filename):
        # filename = secure_filename(audio_file.filename)
        # filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        # audio_file.save(filepath)

        try:
            transcription = call_speech_to_text(audio_file, language)
            __transcriptions[token] = transcription
            return jsonify({"text": __transcriptions[token]})
        except Exception as e:
            print("Error: ", e)
            return jsonify({"error": "Invalid chunk"}), 400

    return jsonify({"error": "Invalid file"}), 400

@app.post('/s2s_bend/finish')
def finish():
    token = request.form['token']
    
    try:
        llm_answer = llm.call(__transcriptions[token])
    except Exception as e:
        print(e)
        return jsonify({"error": "Error from llm"}), 400
    
    
    try:
        answer_audio = text_to_speech.speak(text=llm_answer, voice_clone_path='./res/voice_to_sysntetize.wav', language='it', output_path=f'./uploads/{token}.wav')
    except Exception as e:
        print(e)
        return jsonify({"error": "Error syntethizing Audio"}), 400    

    return jsonify({
        "text": __transcriptions[token],
        "answer": llm_answer
    })


@app.get('/s2s_bend/stream_audio/<token>',)
def stream_audio(token):
    def generate(token):
        with open(f'./uploads/{token}.wav', 'rb') as f:
            while chunk := f.read(1024):
                yield chunk
    return Response(generate(token), content_type='audio/mp3')

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host='0.0.0.0', port=5100, debug=True)
