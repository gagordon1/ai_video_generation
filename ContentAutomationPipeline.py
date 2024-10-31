from ImageGenerator import ImageGenerator
from Story import Story
from StoryGenerator import OpenAIStoryGenerator, StoryGenerator
from ImageGenerator import OpenAIImageGenerator, ImageGenerator, StabilityImageGenerator
from NarrationGenerator import NarrationGenerator, GoogleNarrationGenerator
import json
from constants import *
from moviepy.editor import ImageClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
import requests
import os

# Import necessary modules for AI summarization, image generation, and TTS
# import openai


def download_image(url, filename):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filename, 'wb') as out_file:
            out_file.write(response.content)
        return filename
    else:
        raise Exception(f"Failed to download image: {url}")

class ContentAutomationPipeline:

    def __init__(self, test = False, 
                 story_generation_model : str = "Open AI", 
                 image_generation_model : str = "Open AI",
                 narration_generation_model : str = "Google"
                 ):
        
        if story_generation_model == "Open AI": 
            self.story_generation_model : StoryGenerator = OpenAIStoryGenerator(test=test)
        if image_generation_model == "Open AI":
            self.image_generation_model : ImageGenerator = OpenAIImageGenerator(test=test)
        elif image_generation_model == "Stability":
            self.image_generation_model : ImageGenerator = StabilityImageGenerator(test = test)
        if narration_generation_model == "Google":
            self.narration_generation_model : NarrationGenerator = GoogleNarrationGenerator(test = test)
    
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
            output_filepath = NARRATION_FILEPATH + story.id + str(scene_count) + ".mp3"
            output_file = self.narration_generation_model.generate_audio(narration, output_filepath)
            scene.add_narration_path(output_file)
            scene_count += 1
        return story
    
    def create_video(self, story: Story, output_path : str) -> str:
        """Given a story, creates a video combining each scene and returns the output filepath to thevide

        Args:
            story (Story): completed story object
            output_path (str): path to write video file to

        Returns:
            str: filepath to finished video file
        """
        scene_clips = []

        # Create a temporary directory for images
        temp_dir = "temp_images"
        os.makedirs(temp_dir, exist_ok=True)

        try:
            for i, scene in enumerate(story.get_scenes()):
                # Download image locally
                if scene.scene_image_url == None:
                    raise ValueError("Scene image url is none.")
                if scene.scene_image_url[0:4] == "http":
                    image_path = os.path.join(temp_dir, f"scene_{i}.png")
                    download_image(scene.scene_image_url, image_path)
                else:
                    image_path = scene.scene_image_url

                # Load image
                image_clip = ImageClip(image_path).set_duration(10)  # Set default duration to 10s or match audio length
                image_clip = image_clip.set_position("center").resize(height=720)  # Resize to fit 720p video

                # Load audio
                audio_clip = AudioFileClip(scene.narration_path)
                image_clip = image_clip.set_audio(audio_clip)  # Add audio to the image clip
                image_clip = image_clip.set_duration(audio_clip.duration)  # Match image duration to audio duration

                # Add scene text as a subtitle overlay
                text_clip = TextClip(scene.scene_text, fontsize=24, color='white', size=(image_clip.w - 100, None), method='caption')
                text_clip = text_clip.set_position(('center', 'bottom')).set_duration(audio_clip.duration)

                # Combine image and text clip
                scene_clip = CompositeVideoClip([image_clip, text_clip])
                scene_clips.append(scene_clip)

            # Concatenate all scene clips
            final_video = concatenate_videoclips(scene_clips, method="compose")
            final_video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

        finally:
            # Clean up the temporary directory
            for file in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file))
            os.rmdir(temp_dir)

        return output_path

    def save_story(self, story_filename : str, story : Story):
        with open(STORY_DATA_FILEPATH + story_filename, "w") as file:
            json.dump(story.to_json(), file, indent=4)

    def read_story(self, story_filename : str) -> Story:
        with open(STORY_DATA_FILEPATH +story_filename, "r") as file:
            data = json.load(file)
            return Story.from_json(data)

        

# Example usage
if __name__ == "__main__":

    pipeline = ContentAutomationPipeline(test=False, image_generation_model="Stability")
    story_prompt = "Captain Crunch has his girl stolen then grinds in the gym"
    duration = "one minute"
    story_filename = "Trump and Kamala 2.json"
    story = pipeline.generate_story(story_prompt, duration)
    pipeline.save_story(story_filename, story)
    story = pipeline.read_story(story_filename)
    story = pipeline.generate_story_images(story)
    pipeline.save_story(story_filename, story)
    story = pipeline.generate_story_narrations(story)
    pipeline.save_story(story_filename, story)
    outuput_video_file = "completed_videos/3.mp4"
    pipeline.create_video(story, outuput_video_file)




