from auralis import TTS, TTSRequest
import logging

class Text2Speech:
    def __init__(self, model_name: str, gpt_model_name: str) -> None:
        self.model: TTS = TTS(vllm_logging_level=logging.ERROR).from_pretrained(model_name, gpt_model=gpt_model_name)
    
    def generate_streaming(self, text:str, voice_clone_path: str, language: str):

        request = TTSRequest(
            text=text,
            speaker_files=[voice_clone_path],
            language=language,
            enhance_speech=True,
            stream=True
        )
        
        output = self.model.generate_speech(request)
        
        return output
