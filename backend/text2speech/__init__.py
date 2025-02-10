from auralis import TTS, TTSRequest

class Text2Speech:
    def __init__(self, model_name: str, gpt_model_name: str) -> None:
        self.model: TTS = TTS().from_pretrained(model_name, gpt_model=gpt_model_name)


    def speak(self, text:str, voice_clone_path: str, language: str, output_path: str) -> str:
        
        request = TTSRequest(
            text=text,
            speaker_files=[voice_clone_path],
            language=language,
            enhance_speech=True
        )
        output = self.model.generate_speech(request)
        
        output.save(output_path)

        #TODO: return a stream?
        return output.to_bytes()