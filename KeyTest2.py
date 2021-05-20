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
        key -= self.SpringCut()

        angle=tan(self.Travel/(self.Length/2+self.PivotPos.x))*180/pi
        key = key.rotate((0,self.PivotPos.x,0), (1,self.PivotPos.x,0), angle)

        return key


    PivotPos = cq.Vector(40, 0) #offset from center

    def PivotCut(self):
        cut = cq.Workplane("YZ").move(self.PivotPos.x, self.PivotPos.y) \
            .line(10,-10).line(-20,0).close() \
            .extrude(self.Width/2, both=True)

        # show_object(cut)

        return cut

    SpringDiameter = 3
    SpringPos = Length/2-WallThickness-(SpringDiameter+1)/2-2

    def SpringCut(self):
        cut = cq.Workplane("XY") \
            .move((self.SpringDiameter+1), self.SpringPos).circle((self.SpringDiameter+1)/2).mirrorY() \
            .extrude(self.Height/2, both=True)

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
        base -= self.SpringCut()


        return base.translate((0,0,-Key.Height/2-self.Height/2-Key.Travel))

    
    def Pivot(self):
        pivot = cq.Workplane("YZ").move(Key.PivotPos.x, 0) \
            .move(5, self.Height/2) \
            .line(0, Key.Travel-self.Height/2+Key.PivotPos.y).line(-5,10).line(-5,-10).line(0,-(Key.Travel-self.Height/2+Key.PivotPos.y)).close() \
            .extrude(self.Width/2, both=True)

        return pivot

    def SpringCut(self):
        cut = cq.Workplane("XY") \
            .move((Key.SpringDiameter+1), Key.SpringPos).circle((Key.SpringDiameter+1)/2).mirrorY() \
            .extrude(self.Height/2, both=True)

        return cut


key = Key()
base = Base()

show_object(key)
show_object(base)

cq.exporters.export(key, "KeyTest2.stl")
cq.exporters.export(base, "KeyBaseTest2.stl")

