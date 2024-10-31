from typing import List, Dict, Optional
from datetime import datetime
from moviepy.editor import ImageClip, concatenate_videoclips, TextClip, CompositeVideoClip, AudioFileClip
from ImageGenerator import ImageGenerator
from Story import Story
from StoryGenerator import OpenAIStoryGenerator, StoryGenerator
from ImageGenerator import OpenAIImageGenerator, ImageGenerator
from NarrationGenerator import NarrationGenerator, BarkNarrationGenerator
import json
from constants import *

# Import necessary modules for AI summarization, image generation, and TTS
# import openai

class ContentAutomationPipeline:

    def __init__(self, test = False, 
                 story_generation_model : str = "Open AI", 
                 image_generation_model : str = "Open AI",
                 narration_generation_model : str = "Bark"
                 ):
        
        if story_generation_model == "Open AI": 
            self.story_generation_model : StoryGenerator = OpenAIStoryGenerator(test=test)
        if image_generation_model == "Open AI":
            self.image_generation_model : ImageGenerator = OpenAIImageGenerator(test=test)
        if narration_generation_model == "Bark":
            self.narration_generation_model : NarrationGenerator = BarkNarrationGenerator(test = test)
    
    def generate_story(self, story_prompt : str, duration : str) -> Story:
        return self.story_generation_model.generate_story(story_prompt, duration)
    
    def generate_story_images(self, story : Story) -> Story:
        for scene in story.get_scenes():
            image_url = self.image_generation_model.generate_image(scene.scene_image)
            scene.add_image_url(image_url)
        return story
    
    def generate_story_narrations(self, story: Story) -> Story:
        scene_count = 0
        for scene in story.get_scenes():
            narration = scene.scene_text
            output_filepath = NARRATION_FILEPATH + story.id + str(scene_count)
            output_file = self.narration_generation_model.generate_audio(narration, output_filepath)
            scene.add_narration_path(output_file)
            scene_count += 1
        return story

    def save_story(self, story_filename : str, story : Story):
        with open(STORY_DATA_FILEPATH + story_filename, "w") as file:
            json.dump(story.to_json(), file, indent=4)

    def read_story(self, story_filename : str) -> Story:
        with open(STORY_DATA_FILEPATH +story_filename, "r") as file:
            scenes = json.load(file)
            return Story.from_json(scenes)

        

# Example usage
if __name__ == "__main__":

    pipeline = ContentAutomationPipeline(test=True)
    story_prompt = "Lil Uzi and Playboi Carti have a rizz competition"
    duration = "one minute"
    story = pipeline.generate_story(story_prompt, duration)
    story = pipeline.generate_story_images(story)
    story_filename = "Lil Uzi Vert and Playboi Carti Story Test 10.30.24.json"
    pipeline.save_story(story_filename, story)
    story = pipeline.read_story(story_filename)
    story = pipeline.generate_story_narrations(story)
    print(story)
