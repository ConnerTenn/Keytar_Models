import cadquery as cq
from math import *

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
    WallThickness = 4

    def __new__(self):
        key = cq.Workplane().box(self.Width, self.TotalLength, self.WallThickness)
        key = key.translate((0, self.TotalLength/2 - self.Length, 0))

        pivot = self.Pivot(self)
        key = key.union(pivot)

        return key

    PivotPos = cq.Vector(0,-20)
    PivotSize = 10
    PivotGap = PivotSize-4

    def Pivot(self):
        sketch = cq.Workplane("YZ") \
            .move(self.PivotPos.x-self.PivotSize,0) \
            .line(0, self.PivotPos.y) \
            .tangentArcPoint((self.PivotSize*2,0)) \
            .line(0, -self.PivotPos.y) \
            .close()

        pivot = sketch.extrude(self.WallThickness).faces(">X").workplane() \
            .move(self.PivotPos.x, self.PivotPos.y).hole(self.PivotSize)
        cutline = pivot.faces(">X").workplane() \
            .center(self.PivotPos.x, self.PivotPos.y) \
            .lineTo(-sin(pi/2 * self.PivotGap/self.PivotSize)*self.PivotSize/2, -cos(pi/2 * self.PivotGap/self.PivotSize)*self.PivotSize/2) \
            .lineTo(-sin(pi/2 * self.PivotGap/self.PivotSize)*self.PivotSize, -cos(pi/2 * self.PivotGap/self.PivotSize)*self.PivotSize) \
            .lineTo(-sin(pi/2 * self.PivotGap/self.PivotSize)*self.PivotSize, -self.PivotSize) \
            .lineTo( sin(pi/2 * self.PivotGap/self.PivotSize)*self.PivotSize, -self.PivotSize) \
            .lineTo( sin(pi/2 * self.PivotGap/self.PivotSize)*self.PivotSize, -cos(pi/2 * self.PivotGap/self.PivotSize)*self.PivotSize) \
            .lineTo( sin(pi/2 * self.PivotGap/self.PivotSize)*self.PivotSize/2, -cos(pi/2 * self.PivotGap/self.PivotSize)*self.PivotSize/2) \
            .close()
        pivot = cutline.cutThruAll()

        # show_object(sketch)
        # show_object(cutline)
        # show_object(pivot)

        pivot = pivot.translate((-self.Width/2,0,0))
        pivot = pivot.union(pivot.mirror("YZ"))

        return pivot

key = Key()

show_object(key)
