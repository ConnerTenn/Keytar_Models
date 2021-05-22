import cadquery as cq
import glm
import time

#Stop VS-Code undefined function error
if "show_object" not in globals():
    def func(*args, **kwargs):
        pass
    show_object = func


class Octave(object):
    Width = 24*7
    KeySpacing = 1.5

    def __new__(self):
        self = super().__new__(self)

        self.Keys = [
            CKey(),
            BlackKey(),
            DKey(),
            BlackKey(),
            EKey(),
            FKey(),
            BlackKey(),
            GKey(),
            BlackKey(),
            AKey(),
            BlackKey(),
            BKey(),
            BlackKey()
        ]

        for i, key in enumerate(self.Keys):
            self.Keys[i] = key.translate((i*self.Width/12,0,0))

        return self


    def Show(self):
        for key in self.Keys:
            show_object(key)



class KeyCommon(object):
    MountLength = 40
    HiddenLength = 50
    Width = Octave.Width/12-Octave.KeySpacing
    Height = 10
    WallThickness = 4

    TotalLength = MountLength+HiddenLength

    def __new__(self):
        self = super().__new__(self)

        common = cq.Workplane().box(self.Width, self.TotalLength, self.Height) \
            .translate((0,self.TotalLength/2-self.MountLength,0))

        common -= self.PivotCut()
        common -= self.SpringCut()

        return common


    PivotPos = cq.Vector(25, 0) #offset from center

    def PivotCut(self):
        cut = cq.Workplane("YZ").move(self.PivotPos.x, self.PivotPos.y) \
            .line(10,-10).line(-20,0).close() \
            .extrude(self.Width/2, both=True)

        # show_object(cut)

        return cut


    SpringDiameter = 3
    SpringPos = HiddenLength-WallThickness-(SpringDiameter+1)/2-2

    def SpringCut(self):
        cut = cq.Workplane("XY") \
            .move(self.SpringDiameter, self.SpringPos).circle((self.SpringDiameter+1)/2).mirrorY() \
            .extrude(self.Height/2, both=True)

        return cut


class BlackKey(object):
    def __new__(self):
        self = super().__new__(self)

        key = KeyCommon()
        return key

class CKey(object):
    def __new__(self):
        self = super().__new__(self)

        key = KeyCommon()
        return key

class DKey(object):
    def __new__(self):
        self = super().__new__(self)

        key = KeyCommon()
        return key

class EKey(object):
    def __new__(self):
        self = super().__new__(self)

        key = KeyCommon()
        return key

class FKey(object):
    def __new__(self):
        self = super().__new__(self)

        key = KeyCommon()
        return key

class GKey(object):
    def __new__(self):
        self = super().__new__(self)

        key = KeyCommon()
        return key

class AKey(object):
    def __new__(self):
        self = super().__new__(self)

        key = KeyCommon()
        return key

class BKey(object):
    def __new__(self):
        self = super().__new__(self)

        key = KeyCommon()
        return key


common = KeyCommon()
show_object(common)

octave = Octave()
octave.Show()

