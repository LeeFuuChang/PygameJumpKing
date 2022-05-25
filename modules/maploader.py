from .constants import *
from .shapes import *
import json


class Level:
    def __init__(self, bg, lines):
        self.bg = bg
        self.lines = lines



class MapLoader:
    def __init__(self, path):
        self.path = path
        with open(path, "r") as f:
            self.data = json.load(f)

    def loadLevels(self):
        levels = []
        for idx in self.data:
            lines = []
            for lineData in self.data[idx]["lines"]:
                lines.append(Line(*lineData))
            levels.append(Level(
                bg = pygame.image.load(os.path.join(IMAGE_PATH, "bg", f"{idx}.png")),
                lines = lines
            ))
        return levels