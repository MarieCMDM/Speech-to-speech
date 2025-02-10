import io
import whisper 
from subprocess import run, PIPE
import numpy as np

class Speech2Text:
    def __init__(self, model_name: str) -> None:
        self.model: whisper.Whisper = whisper.load_model(model_name)      
    
    def transcribe(self, input_audio: io.BytesIO, lang: str) -> str:
        try:
            # decode the audio bytes in what whisper needs
            cmd = [
                "ffmpeg",
                "-threads", "0",
                "-i", "pipe:0",
                "-f", "s16le",
                "-ac", "1",
                "-acodec", "pcm_s16le",
                "-ar", "16000",
                "pipe:1"
            ]


            audio_bytes_wav_format = run(cmd, stdout=PIPE, stderr=PIPE, input=input_audio.read())
            audio_array = np.frombuffer(audio_bytes_wav_format.stdout, np.int16).flatten().astype(np.float32) / 32768.0
        except Exception as e:
            raise Exception(f'Error converting audio to wav {e}')

        try:
            # whisper pads or trims to 30 secs chunks
            # it has a way to tell if it cut a world and a way to recover it
            audio_array = whisper.pad_or_trim(audio_array)
            mel = whisper.log_mel_spectrogram(audio_array, n_mels=self.model.dims.n_mels).to(self.model.device)
        except Exception as e:
            raise Exception(f'Error generating spectogram {e}')
        
        try:
            #* For Debug
            # _, probs = self.model.detect_language(mel)
            # print(f"Debugging: whisper detected language: {max(probs, key=probs.get)}")

            options = whisper.DecodingOptions(language=lang)
            transcription = whisper.decode(self.model, mel, options)

            return transcription.text
        except Exception as e:
            raise Exception(f'Error generating transcription {e}')