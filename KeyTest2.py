import cadquery as cq
from math import *

#Stop VS-Code undefined function error
if "show_object" not in globals():
    def func(*args, **kwargs):
        pass
    show_object = func

Small = 1e-5

class Key:
    Length = 120
    Width = 23.5
    Height = 10
    WallThickness = 4
    Travel = 10

    def __new__(self):
        self = super().__new__(self)

        key = cq.Workplane().box(self.Width, self.Length, self.Height) \
            .faces("<Z").shell(-self.WallThickness)

        key -= self.PivotCut()

        return key


    PivotPos = cq.Vector(30, 0) #offset from center

    def PivotCut(self):
        cut = cq.Workplane("YZ").move(self.PivotPos.x, self.PivotPos.y) \
            .line(10,-10).line(-20,0).close() \
            .extrude(self.Width/2, both=True)

        # show_object(cut)

        return cut


class Base:
    Length = Key.Length
    Width = Key.Width+1
    Height = Key.Height
    WallThickness = Key.WallThickness

    def __new__(self):
        self = super().__new__(self)

        base = cq.Workplane().box(self.Width, self.Length, self.Height) \
            .faces("<Z").shell(-self.WallThickness)

        base += self.Pivot()


        return base.translate((0,0,-Key.Height/2-self.Height/2-Key.Travel))

    
    def Pivot(self):
        pivot = cq.Workplane("YZ").move(Key.PivotPos.x, 0) \
            .move(5, self.Height/2) \
            .line(0, Key.Travel-self.Height/2+Key.PivotPos.y).line(-5,10).line(-5,-10).line(0,-(Key.Travel/2+self.Height/2+Key.PivotPos.y)).close() \
            .extrude(self.Width/2, both=True)
        
        return pivot


key = Key()
base = Base()

show_object(key)
show_object(base)

cq.exporters.export(key, "KeyTest2.stl")
cq.exporters.export(base, "KeyBaseTest2.stl")

