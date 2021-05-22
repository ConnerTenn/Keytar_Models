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
            BKey()
        ]

        for i, key in enumerate(self.Keys):
            key.Show(i)


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

        return common.translate((self.Width/2,0,0))


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
    MountLength = 60-Octave.KeySpacing
    MountWidth = Octave.Width/12-Octave.KeySpacing

    def Obj(self):
        key = KeyCommon(self.MountLength, self.MountWidth).Obj()
        return key

    def Show(self, i):
        show_object(self.Obj().translate((i*Octave.Width/12,0,0)), options={"color":(20,20,20)})

class WhiteKey(object):
    MountLength = 60
    MountWidth = Octave.Width/12-Octave.KeySpacing
    ExtendedLength = 40
    Width = Octave.Width/7-Octave.KeySpacing

    def Obj(self): None

    def Base(self):
        key = KeyCommon(self.MountLength, self.MountWidth).Obj()

        return key

    def Extension(self):
        key = cq.Workplane().box(self.Width, self.ExtendedLength, KeyCommon.Height) \
            .translate((0, -(self.MountLength+self.ExtendedLength/2), 0))

        return key.translate((KeyCommon.Width/2,0,0))

    def Show(self, i):
        show_object(self.Obj().translate((i*Octave.Width/12,0,0)), options={"color":(255,255,255)})

class CKey(WhiteKey):
    def Obj(self):
        key = super().Base() + super().Extension().translate((self.Width/2-KeyCommon.Width/2, 0, 0))
        return key

class DKey(WhiteKey):
    def Obj(self):
        key = super().Base() + super().Extension()
        return key

class EKey(WhiteKey):
    def Obj(self):
        key = super().Base() + super().Extension().translate((-self.Width/2+KeyCommon.Width/2, 0, 0))
        return key

class FKey(WhiteKey):
    def Obj(self):
        key = super().Base() + super().Extension().translate((self.Width/2-KeyCommon.Width/2, 0, 0))
        return key

class GKey(WhiteKey):
    def Obj(self):
        key = super().Base() + super().Extension().translate((self.Width/2-KeyCommon.Width/2-KeyCommon.Width/4, 0, 0))
        return key

class AKey(WhiteKey):
    def Obj(self):
        key = super().Base() + super().Extension().translate((-self.Width/2+KeyCommon.Width/2+KeyCommon.Width/4, 0, 0))
        return key

class BKey(WhiteKey):
    def Obj(self):
        key = super().Base() + super().Extension().translate((-self.Width/2+KeyCommon.Width/2, 0, 0))
        return key


class Base(object):
    Height = WallThickness
    def Obj(self):
        base = cq.Workplane().box(Octave.Width, KeyCommon.HiddenLength+WhiteKey.ExtendedLength, self.Height)

        return base.translate((Octave.Width/2,0,-KeyCommon.Height/2-self.Height/2-10))

    def Show(self):
        show_object(self.Obj(), options={"color":(127,127,127)})


Octave().Show()
Base().Show()

