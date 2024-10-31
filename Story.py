import uuid

class Scene:

    def __init__(self, 
                 scene_text : str, 
                 scene_image : str, 
                 scene_image_url : str | None = None,
                 narration_path : str | None = None) -> None:
        self.scene_text = scene_text
        self.scene_image = scene_image
        self.scene_image_url = scene_image_url
        self.narration_path = narration_path

    def add_image_url(self, url : str):
        self.scene_image_url = url

    def add_narration_path(self, filepath : str):
        self.narration_path = filepath

    def __str__(self) -> str:
        out = "Scene Description: {}".format(self.scene_text)
        out += "\n\n"
        out += "Image Description: {}".format(self.scene_image)
        out += "\n\n"
        out += "Image Url: {}".format(self.scene_image_url)
        out += "\n\n"
        out += "Narration Path: {}".format(self.narration_path)
        return out
    
    def to_json(self):
        return {
            "scene_text" : self.scene_text,
            "scene_image" : self.scene_image,
            "scene_image_url" : self.scene_image_url,
            "narration_path" : self.narration_path
        }
    
    @classmethod
    def from_json(cls, data):
        return cls(
            data.get("scene_text"),
            data.get("scene_image"),
            data.get("scene_image_url"),
            data.get("narration_path")
        )


class Story:

    def __init__(self, scenes : list[Scene], id : str | None = None):
        if id:
            self.id = id
        else:
            self.id = str(uuid.uuid4())
        self.scenes = scenes

    def get_scenes(self):
        return self.scenes
    
    def __str__(self) -> str:
        out = ""
        for scene in self.scenes:
            out += str(scene)
            out += "\n"
            out += "---"*10
            out += "\n"
        return out
    
    def to_json(self):
        return {"scenes" : [scene.to_json() for scene in self.scenes], "id" : self.id}
    
    @classmethod
    def from_json(cls, data):
        return cls(scenes = [Scene.from_json(x) for x in data],id = data.get("id"))