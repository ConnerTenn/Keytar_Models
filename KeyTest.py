import cadquery as cq
from glm import *

#Stop VS-Code undefined function error
if "show_object" not in globals():
    def func(*args, **kwargs):
        pass
    show_object = func


class Key:
    Length = 150
    HiddenLength = 50
    TotalLength = Length + HiddenLength
    Width = 23.5
    Height = 10
    WallThickness = 2

    def __new__(self):
        key = cq.Workplane().box(self.Width, self.TotalLength, self.WallThickness)
        key = key.translate((0, self.TotalLength/2 - self.Length, 0))

        return key

key = Key()

show_object(key)
