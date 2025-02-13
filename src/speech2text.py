import io
import whisper 
from subprocess import run, PIPE
import numpy as np

class Speech2Text:
    def __init__(self, model_name: str) -> None:
        self.model: whisper.Whisper = whisper.load_model(model_name)      
    
    def transcribe(self, input_audio: io.BytesIO, language: str) -> str:
        try:
            audio_array = self.__audio_np_array_from_bytes(input_audio)
            mel = self.__get_mel_spectogram(audio_array)    
            transcription = self.__transcribe(mel, language)

            return transcription
        except Exception as e:
            raise e
        
    def __audio_np_array_from_bytes(self, input_audio: io.BytesIO) -> np.float32:
        try:
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
            return np.frombuffer(audio_bytes_wav_format.stdout, np.int16).flatten().astype(np.float32) / 32768.0
        except Exception as e:
            raise Exception(f'Error converting audio: {e}')
    
    def __get_mel_spectogram(self, audio_array: np.float32) -> Any:
        try:
            padded_array = whisper.pad_or_trim(audio_array)
            return whisper.log_mel_spectrogram(padded_array, n_mels=self.model.dims.n_mels).to(self.model.device)
        except Exception as e:
            raise Exception(f'Error generating spectogram: {e}')

    def __transcribe(self, mel, language) -> str:
        try:
            options = whisper.DecodingOptions(language=language)
            transcription = whisper.decode(self.model, mel, options)
            return transcription.text
        except Exception as e:
            raise Exception(f'Error generating transcription: {e}')