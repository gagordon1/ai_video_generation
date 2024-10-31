from openai import OpenAI
from dotenv import load_dotenv
from constants import *
import requests
import uuid
import os


class ImageGenerator:

    def __init__(self, test = False):
        self.test = test

    def generate_image(self, prompt : str):
        """Given a text prompt returns the link to ai rendering of the text

        Args:
            prompt (str): text prompt to create an image from
        """
        raise NotImplementedError("Subclasses must implement this method")
    
class StabilityImageGenerator(ImageGenerator):
    def __init__(self, test = False) -> None:
        super().__init__(test)

    def generate_image(self, prompt : str) -> str:
        load_dotenv()
        response = requests.post(
            f"https://api.stability.ai/v2beta/stable-image/generate/ultra",
            headers={
                "authorization": "Bearer {}".format(os.getenv("STABILITY_API_KEY")),
                "accept": "image/*"
            },
            files={"none": ''},
            data={
                "prompt": prompt,
                "output_format": "png",
            },
         )
        output_file = IMAGE_FILEPATH + str(uuid.uuid4()) + ".png"
        if response.status_code == 200:
            with open(output_file, 'wb') as file:
                file.write(response.content)
        else:
            raise Exception(str(response.json()))
        
        return output_file

class OpenAIImageGenerator(ImageGenerator):
    def __init__(self, test = False) -> None:
        super().__init__(test)

    def generate_image(self, prompt : str) -> str:

        if self.test:
            return TEST_IMAGE_URL
        load_dotenv()
        client = OpenAI()
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        if response.data[0].url:
            return response.data[0].url
        else:
            raise ValueError("Open AI failed to produce image for prompt {}".format(prompt))

if __name__ == "__main__":
    # generator = OpenAIImageGenerator()
    # generator.generate_image("playboi carti")
    pass
