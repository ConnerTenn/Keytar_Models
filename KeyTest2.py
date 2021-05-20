import cadquery as cq
from math import *

#Stop VS-Code undefined function error
if "show_object" not in globals():
    def func(*args, **kwargs):
        pass
    show_object = func

Small = 1e-5

class Key:
    Length = 100
    HiddenLength = 50
    TotalLength = Length + HiddenLength
    Width = 23.5
    Height = 10
    WallThickness = 4

    def __new__(self):
        self = super().__new__(self)

        key = cq.Workplane()
        return key


class Base:
    Length = Key.TotalLength
    Width = Key.Width+1
    Height = Key.Height
    WallThickness = Key.WallThickness

    def __new__(self):
        self = super().__new__(self)

        base = cq.Workplane()
        return base


key = Key()
base = Base()

show_object(key)
show_object(base)

cq.exporters.export(key, "KeyTest2.stl")
cq.exporters.export(base, "KeyBaseTest2.stl")

