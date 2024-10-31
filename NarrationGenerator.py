from google.cloud import texttospeech

class NarrationGenerator:

    def __init__(self, test = False) -> None:
        self.test = test
        print("Narration model initialized.")

    def generate_audio(self, input_text : str, output_filepath : str) -> str:
        """Given in input text and an output filepath, runs text to speech

        Args:
            input_text (str): input text to generate audio from
            output_filepath (str): destination filepath for the wav file

        Returns:
            str: Path to the completed text to speech file
        """
        raise NotImplementedError("Subclasses must implement this method.")
    

# class BarkNarrationGenerator(NarrationGenerator):
#     def __init__(self, test=False) -> None:
#         self.synthesizer = pipeline("text-to-speech", "suno/bark")
#         super().__init__(test)
        
    
#     def generate_audio(self, input_text: str, output_filepath : str) -> str:
#         speech = self.synthesizer(input_text, forward_params={"do_sample": True})
#         scipy.io.wavfile.write(output_filepath, rate=speech["sampling_rate"], data=speech["audio"]) #type: ignore
#         return output_filepath
    
class GoogleNarrationGenerator(NarrationGenerator):
    def __init__(self, test=False) -> None:
        super().__init__(test)
        
    
    def generate_audio(self, input_text: str, output_filepath : str) -> str:
        client = texttospeech.TextToSpeechClient()
        text_input = texttospeech.SynthesisInput(text=input_text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", ssml_gender="FEMALE"
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = client.synthesize_speech(
            input=text_input, voice=voice, audio_config=audio_config
        )

        with open(output_filepath, "wb") as out:
            out.write(response.audio_content)
        return output_filepath
    
if __name__ == "__main__":
    pass