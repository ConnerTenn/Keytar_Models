import cadquery as cq
import glm
import time

#Stop VS-Code undefined function error
if "show_object" not in globals():
    def func(*args, **kwargs):
        pass
    show_object = func


WallThickness = 4
Small = 1e-5


class Octave(object):
    Width = 24*7
    KeySpacing = 1.5

    def Show(self):
        self.Keys = [
            WhiteKey("C"),
            BlackKey("C#"),
            WhiteKey("D"),
            BlackKey("D#"),
            WhiteKey("E"),
            WhiteKey("F"),
            BlackKey("F#"),
            WhiteKey("G"),
            BlackKey("G#"),
            WhiteKey("A"),
            BlackKey("A#"),
            WhiteKey("B")
        ]

        for key in self.Keys:
            key.Show()


class KeyCommon(object):
    HiddenLength = 50
    Width = Octave.Width/12-Octave.KeySpacing
    Height = 10

    def __init__(self, mountlen, mountwidth):
        self.MountLength = mountlen
        self.Width = mountwidth
        self.TotalLength = self.MountLength+self.HiddenLength

    def Obj(self):
        common = cq.Workplane().box(self.Width, self.TotalLength, self.Height) \
            .translate((0,self.TotalLength/2-self.MountLength,0))

        common -= self.PivotCut()
        common -= self.SpringCut()

        return common#.translate((self.Width/2,0,0))


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


class WhiteKey(object):
    MountLength = 60
    ExtendedLength = 40
    Width = Octave.Width/7-Octave.KeySpacing

    def __init__(self, key):
        self.Key = key


    def Obj(self):
        key = self.Base() + self.Extension()

        return key

    def Base(self):
        key = KeyCommon(self.MountLength, Octave.BaseWidths[self.Key]).Obj()

        return key.translate((Octave.BaseOffsets[self.Key],0,0))

    def Extension(self):
        key = cq.Workplane().box(self.Width, self.ExtendedLength, KeyCommon.Height) \
            .translate((0, -(self.MountLength+self.ExtendedLength/2), 0))

        return key#.translate((self.Width/2,0,0))

    def GetPosition(self):
        return (self.Width/2+Octave.KeyOffsets[self.Key], 0, 0)

    def Show(self):
        show_object(self.Obj().translate(self.GetPosition()), options={"color":(255,255,255)})

class BlackKey(object):
    MountLength = 60-Octave.KeySpacing
    MountWidth = Octave.Width/12-Octave.KeySpacing

    def __init__(self, key):
        self.Key = key

    def Obj(self):
        key = KeyCommon(self.MountLength, self.MountWidth).Obj()
        return key

    def GetPosition(self):
        return (WhiteKey.Width/2+Octave.KeyOffsets[self.Key], 0, 0)

    def Show(self):
        show_object(self.Obj().translate(self.GetPosition()), options={"color":(20,20,20)})


Octave.KeyOffsets = {
    "C":Octave.KeySpacing/2 + 0*Octave.Width/7,
    "D":Octave.KeySpacing/2 + 1*Octave.Width/7,
    "E":Octave.KeySpacing/2 + 2*Octave.Width/7,
    "F":Octave.KeySpacing/2 + 3*Octave.Width/7,
    "G":Octave.KeySpacing/2 + 4*Octave.Width/7,
    "A":Octave.KeySpacing/2 + 5*Octave.Width/7,
    "B":Octave.KeySpacing/2 + 6*Octave.Width/7,
}

#Global position of the left side of each key
Octave.KeyLeft = {}
for key, offset in Octave.KeyOffsets.items():
    Octave.KeyLeft[key] = offset - WhiteKey.Width/2 + BlackKey.MountWidth/2

#Global position of the right side of each key
Octave.KeyRight = {}
for key, offset in Octave.KeyOffsets.items():
    Octave.KeyRight[key] = offset + WhiteKey.Width/2 - BlackKey.MountWidth/2

Octave.BaseWidths = {
    "C":Octave.Width/12-Octave.KeySpacing,
    "D":Octave.Width/12-Octave.KeySpacing,
    "E":Octave.Width/12-Octave.KeySpacing,
    "F":Octave.Width/12-Octave.KeySpacing,
    "G":Octave.Width/12-Octave.KeySpacing,
    "A":Octave.Width/12-Octave.KeySpacing,
    "B":Octave.Width/12-Octave.KeySpacing,
}

Octave.KeyOffsets["C#"] = Octave.KeyLeft["C"] + BlackKey.MountWidth + Octave.KeySpacing
Octave.KeyOffsets["D#"] = Octave.KeyRight["E"] - BlackKey.MountWidth - Octave.KeySpacing
Octave.KeyOffsets["F#"] = Octave.KeyLeft["F"] + BlackKey.MountWidth + Octave.KeySpacing
Octave.KeyOffsets["G#"] = Octave.KeyOffsets["G"] + WhiteKey.Width/2 + Octave.KeySpacing/2
Octave.KeyOffsets["A#"] = Octave.KeyRight["B"] - BlackKey.MountWidth - Octave.KeySpacing

Octave.BaseOffsets = {
    "C":-WhiteKey.Width/2 + Octave.BaseWidths["C"]/2,
    "D":0,
    "E":WhiteKey.Width/2 - Octave.BaseWidths["E"]/2,
    "F":-WhiteKey.Width/2 + Octave.BaseWidths["F"]/2,
    "G":-Octave.BaseWidths["G"]/4,
    "A":Octave.BaseWidths["A"]/4,
    "B":WhiteKey.Width/2 - Octave.BaseWidths["B"]/2,
}


class Base(object):
    Height = WallThickness
    def Obj(self):
        base = cq.Workplane().box(Octave.Width, KeyCommon.HiddenLength+WhiteKey.ExtendedLength, self.Height)

        return base.translate((Octave.Width/2,0,-KeyCommon.Height/2-self.Height/2-10))

    def Show(self):
        show_object(self.Obj(), options={"color":(127,127,127)})


Octave().Show()
Base().Show()

