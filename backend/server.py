from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import io
from werkzeug.utils import secure_filename

import whisper

import whisper

model = whisper.load_model('base')

app = Flask(__name__)
CORS(app) 

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'webm'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['audio']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # audio_file = io.BytesIO(file.read())
    
        result = model.transcribe(filepath)
        transcription = result['text']

        # transcription = "Dummy transcription"
        return jsonify({"text": transcription})

    return jsonify({"error": "Invalid file"}), 400

@app.route('/finish', methods=['POST'])
def finish():
    if 'audio' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['audio']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        transcription = "Last transcription"
        response_audio_url = f"/{UPLOAD_FOLDER}/{filename}"
        
        return jsonify({
            "text": transcription,
            "audioUrl": response_audio_url
        })

    return jsonify({"error": "Invalid file"}), 400

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host='0.0.0.0', port=5000, debug=True)
