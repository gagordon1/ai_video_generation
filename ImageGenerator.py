from openai import OpenAI
from dotenv import load_dotenv
from constants import *


class ImageGenerator:

    def __init__(self, test = False):
        self.test = test

    def generate_image(self, prompt : str):
        """Given a text prompt returns the link to ai rendering of the text

        Args:
            prompt (str): text prompt to create an image from
        """
        raise NotImplementedError("Subclasses must implement this method")

class OpenAIImageGenerator(ImageGenerator):
    def __init__(self, test = False) -> None:
        super().__init__(test)

    def generate_image(self, prompt : str) -> str:

        if self.test:
            return TEST_IMAGE_URL
        load_dotenv()
        client = OpenAI()
        response = client.images.generate(
            model="dall-e-2",
            prompt=prompt,
            size="512x512",
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
