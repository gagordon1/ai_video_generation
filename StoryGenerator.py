from constants import *
from dotenv import load_dotenv
from Story import Story, Scene
from openai import OpenAI
import re

class StoryGenerator:

    def __init__(self, test = False):
        self.test = test

    def generate_story(self, story_prompt : str, duration : str) -> Story:
        raise NotImplementedError("Subclasses must implement this method")
    
    def build_prompt(self, story_prompt : str, duration : str)-> str:
        return STORY_GENERATION_PROMPT_TEMPLATE.format(duration=duration, story_prompt = story_prompt)
    
    def parse_response_content(self, input : str) -> Story:
        text_no_newlines = input.replace('\n', ' ')

        # Use regex to find all sections delimited by "%^"
        # Extract image descriptions using regex
        image_descriptions = re.findall(r'%\^(.*?)%\^', text_no_newlines)

        # Remove image descriptions from main text, leaving only main content
        main_text = re.sub(r'%\^.*?%\^', '', text_no_newlines).strip()

        # Split the main text into segments based on where the descriptions were removed
        # and remove extra spaces from each segment
        main_text_segments = [segment.strip() for segment in re.split(r'%\^.*?%\^', text_no_newlines) if segment.strip()]
        
        assert len(image_descriptions) == len(main_text_segments)

        scenes = []
        for i in range(len(image_descriptions)):
            scenes.append(Scene(
                scene_text=main_text_segments[i],
                scene_image=image_descriptions[i]
            ))
        return Story(scenes)


class OpenAIStoryGenerator(StoryGenerator):

    def __init__(self, test=False):
        super().__init__(test)

    def generate_story(self, story_prompt: str, duration : str) -> Story:
        prompt = self.build_prompt(story_prompt, duration)
        if self.test:
            response_content = TEST_RESPONSE_CONTENT
            return self.parse_response_content(response_content)
        load_dotenv()
        client = OpenAI()
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        response_content = completion.choices[0].message.content
        if response_content:
            return self.parse_response_content(response_content)
        else:
            raise ValueError("Open AI failed to produce a valid response for the prompt: \n{}".format(prompt))

if __name__ == "__main__":
    # oai_generator = OpenAIStoryGenerator(test=True)
    # story_prompt = "Playboi Carti and Lil Uzi Vert discovering the true value of friendship."
    # duration = "one minute"
    # prompt = STORY_GENERATION_PROMPT_TEMPLATE.format(duration = duration, story_prompt = story_prompt)
    
    # story = oai_generator.generate_story(prompt)
    # print(story)
    pass
