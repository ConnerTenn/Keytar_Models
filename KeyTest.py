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

    Padding = 0.3

    def __new__(self):
        self = super().__new__(self)

        key = cq.Workplane().box(self.Width, self.TotalLength, self.Height)
        key = key.faces("<Z").shell(-self.WallThickness)
        key = key.translate((0, self.TotalLength/2 - self.Length, 0))

        hook = self.SpringHook(key)
        key += hook

        pivot = self.Pivot()
        key += pivot

        key += self.ButtonPost(key)

        return key

    PivotPos = cq.Vector(0,-10)
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
            .move(self.PivotPos.x, self.PivotPos.y).hole(self.PivotSize+self.Padding*2)
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

    ButtonPostPos = Length-WallThickness - 20
    ButtonPostLength = 20
    ButtonPostWidth = WallThickness*1.5
    ButtonPostHeight = Height/2-WallThickness + 10

    def ButtonPost(self, keyobj):
        post = keyobj.faces(">Z[-2]").workplane() \
            .move(0, self.ButtonPostPos) \
            .slot2D(self.ButtonPostLength, self.ButtonPostWidth, 90) \
            .extrude(self.ButtonPostHeight, combine=False)

        # show_object(post)
        return post

class Base:
    Length = Key.TotalLength
    Width = Key.Width+1
    Height = Key.Height
    WallThickness = Key.WallThickness

    def __new__(self):
        self = super().__new__(self)

        base = cq.Workplane().box(self.Width, self.Length, self.Height) \
            .faces("<Z").shell(-self.WallThickness) \
            .translate((0, Key.TotalLength/2 - Key.Length, 0))

        combined = base
        combined += self.SpringHooks(base)
        combined += self.KeyStopper(base)
        combined += self.Pivot(base)

        return combined.translate((0, 0, -self.PivotHeight+Key.PivotPos.y))


    PivotHeight = 20
    
    def Pivot(self, base):
        pivot = base.faces("<X").workplane() \
            .move(0, (self.PivotHeight/2+Key.PivotSize/2 + self.Height/2)/2) \
            .rect(Key.PivotSize, self.PivotHeight+self.Height).extrude(self.WallThickness, combine=False) \
            .edges(">Z and |X").fillet(Key.PivotSize/(2+Small))

        pivot += pivot.mirror("YZ")

        pivot += cq.Workplane("YZ").move(0, self.PivotHeight) \
            .circle(Key.PivotSize/2).extrude(self.Width/2, both=True)

        # show_object(pivot)

        return pivot


    HookStartPos = 20
    HookCount = 9

    def SpringHooks(self, base):
        hook = base.faces(">Z").workplane() \
            .circle(self.WallThickness/2) \
            .workplane(offset=3/2) \
            .circle(1.5/2).loft(combine=False) \
            .faces(">Z").workplane() \
            .move(0,-(2-1.5)/2).circle(2/2).extrude(1)

        hooks = cq.Workplane()
        for i in range(self.HookCount):
            hooks += hook.translate((0,self.HookStartPos-i*10,0))

        return hooks

    def KeyStopper(self, base):
        stopper = base.faces(">Z").workplane() \
            .move(-Key.Width/2+self.WallThickness/2, Key.HiddenLength*0.6) \
            .rect(self.WallThickness,3*self.WallThickness).mirrorY() \
            .extrude(abs(Key.PivotPos.y) + self.PivotHeight - (self.Height+Key.Height)/2 - Key.Padding, combine=False)

        return stopper


key = Key()
base = Base()

show_object(key)
show_object(base)

cq.exporters.export(key, "KeyTest.stl")
cq.exporters.export(base, "KeyBaseTest.stl")
