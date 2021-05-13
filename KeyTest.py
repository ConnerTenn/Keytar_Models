import cadquery as cq
from math import *

#Stop VS-Code undefined function error
if "show_object" not in globals():
    def func(*args, **kwargs):
        pass
    show_object = func

Small = 1e-5

class Key:
    Length = 150
    HiddenLength = 50
    TotalLength = Length + HiddenLength
    Width = 23.5
    Height = 10
    WallThickness = 4

    def __new__(self):
        self = super().__new__(self)

        key = cq.Workplane().box(self.Width, self.TotalLength, self.Height)
        key = key.faces("<Z").shell(-self.WallThickness)
        key = key.translate((0, self.TotalLength/2 - self.Length, 0))

        hook = self.SpringHook(key)
        key += hook

        pivot = self.Pivot()
        key += pivot

        self.ButtonPost(key)

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
        pivot += pivot.mirror("YZ")

        return pivot

    HookHeight = 20-Height/2

    def SpringHook(self, keyobj):
        post = keyobj.faces("<Z").edges(">Y").workplane(centerOption="CenterOfMass").center(0,self.WallThickness/2) \
            .rect(self.Width, self.WallThickness) \
            .workplane(offset=self.HookHeight) \
            .rect(self.WallThickness, self.WallThickness) \
            .loft(combine=False)
            # .extrude(self.HookHeight, combine=False)

        post = post.faces("<Z").workplane() \
            .circle(self.WallThickness/2) \
            .workplane(offset=3/2) \
            .circle(1.5/2).loft() \
            .faces("<Z").workplane() \
            .move(0,-(2-1.5)/2).circle(2/2).extrude(1)

        braceHeight = self.HookHeight+self.Height-self.WallThickness
        post += cq.Workplane("YZ").center(self.HiddenLength-self.WallThickness, self.Height/2-self.WallThickness) \
            .lineTo(-braceHeight, 0) \
            .lineTo(0, -braceHeight) \
            .close().extrude(self.WallThickness/2, both=True)
        # show_object(post)

        return post

    ButtonPostPos = Length-WallThickness - 40
    ButtonPostLength = 30
    ButtonPostWidth = WallThickness*2
    ButtonPostHeight = Height/2-WallThickness + 20

    def ButtonPost(self, keyobj):
        post = keyobj.faces(">Z[-2]").workplane() \
            .move(0, self.ButtonPostPos) \
            .slot2D(self.ButtonPostLength, self.ButtonPostWidth, 90) \
            .extrude(self.ButtonPostHeight, combine=False)

        show_object(post)

key = Key()

show_object(key)

