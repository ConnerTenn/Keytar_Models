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

    def __init__(self):
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

    def Show(self):
        for key in self.Keys:
            key.Show()


class KeyCommon(object):
    HiddenLength = 50
    TotalLength = 150
    ExposedLength = TotalLength-HiddenLength
    Height = 10

    Travel = 10

    def __init__(self, keybaseLength, keybaseWidth):
        self.KeyBaseLength = keybaseLength
        self.Width = keybaseWidth
        self.TotalLength = self.KeyBaseLength+self.HiddenLength

    def Obj(self):
        common = cq.Workplane().box(self.Width, self.TotalLength, self.Height) \
            .translate((0,self.TotalLength/2-self.KeyBaseLength,0))

        common -= self.PivotCut()
        common -= self.SpringCut()

        return common


    PivotPos = cq.Vector(25, 0) #offset from center

    def PivotCut(self):
        cut = cq.Workplane("YZ").move(self.PivotPos.x, self.PivotPos.y) \
            .line(10,-10).line(-20,0).close() \
            .extrude(self.Width/2, both=True)

        return cut


    SpringDiameter = 3
    SpringPos = HiddenLength-WallThickness-(SpringDiameter+1)/2-2

    def SpringCut(self):
        cut = cq.Workplane("XY") \
            .move(self.SpringDiameter, self.SpringPos).circle((self.SpringDiameter+1)/2).mirrorY() \
            .extrude(self.Height/2, both=True)

        return cut


class WhiteKey(object):
    ExtendedLength = 40
    KeyBaseLength = KeyCommon.ExposedLength-ExtendedLength
    Width = Octave.Width/7-Octave.KeySpacing

    def __init__(self, key):
        self.Key = key


    def Obj(self):
        key = self.KeyBase() + self.Extension()

        return key

    def KeyBase(self):
        keybase = KeyCommon(self.KeyBaseLength, Octave.KeyBaseWidths[self.Key]).Obj()

        return keybase.translate((Octave.KeyBaseOffsets[self.Key], 0, 0))

    def Extension(self):
        keyextend = cq.Workplane().box(self.Width, self.ExtendedLength, KeyCommon.Height)

        return keyextend.translate((0, -(self.KeyBaseLength+self.ExtendedLength/2), 0))

    def GetPosition(self):
        return cq.Vector(self.Width/2+Octave.KeyOffsets[self.Key], 0, 0)

    def Show(self):
        show_object(self.Obj().translate(self.GetPosition()), options={"color":(255,255,255)})

#Black key is positioned relative to the center of the white key
class BlackKey(object):
    KeyBaseLength = WhiteKey.KeyBaseLength-Octave.KeySpacing
    KeyBaseWidth = Octave.Width/12-Octave.KeySpacing

    def __init__(self, key):
        self.Key = key

    def Obj(self):
        key = KeyCommon(self.KeyBaseLength, self.KeyBaseWidth).Obj()
        return key

    def GetPosition(self):
        return cq.Vector(WhiteKey.Width/2+Octave.KeyOffsets[self.Key], 0, 0)

    def Show(self):
        show_object(self.Obj().translate(self.GetPosition()), options={"color":(20,20,20)})


#Initialize the positioning of all the white keys
Octave.KeyOffsets = {
    "C":Octave.KeySpacing/2 + 0*Octave.Width/7,
    "D":Octave.KeySpacing/2 + 1*Octave.Width/7,
    "E":Octave.KeySpacing/2 + 2*Octave.Width/7,
    "F":Octave.KeySpacing/2 + 3*Octave.Width/7,
    "G":Octave.KeySpacing/2 + 4*Octave.Width/7,
    "A":Octave.KeySpacing/2 + 5*Octave.Width/7,
    "B":Octave.KeySpacing/2 + 6*Octave.Width/7,
}

#Calculate the global position of the left side of each key
Octave.KeyLeft = {}
for key, offset in Octave.KeyOffsets.items():
    Octave.KeyLeft[key] = offset - WhiteKey.Width/2 + BlackKey.KeyBaseWidth/2

#Calculate the global position of the right side of each key
Octave.KeyRight = {}
for key, offset in Octave.KeyOffsets.items():
    Octave.KeyRight[key] = offset + WhiteKey.Width/2 - BlackKey.KeyBaseWidth/2

#Default sizing of the mounts
Octave.KeyBaseWidths = {
    "C":Octave.Width/12-Octave.KeySpacing,
    # "D":Octave.Width/12-Octave.KeySpacing,
    "E":Octave.Width/12-Octave.KeySpacing,
    "F":Octave.Width/12-Octave.KeySpacing,
    # "G":Octave.Width/12-Octave.KeySpacing,
    # "A":Octave.Width/12-Octave.KeySpacing,
    "B":Octave.Width/12-Octave.KeySpacing,
}

#Offsets of the black keys calculated relative to the white keys
Octave.KeyOffsets["C#"] = Octave.KeyLeft["C"] + BlackKey.KeyBaseWidth + Octave.KeySpacing
Octave.KeyOffsets["D#"] = Octave.KeyRight["E"] - BlackKey.KeyBaseWidth - Octave.KeySpacing
Octave.KeyOffsets["F#"] = Octave.KeyLeft["F"] + BlackKey.KeyBaseWidth + Octave.KeySpacing
Octave.KeyOffsets["G#"] = Octave.KeyOffsets["G"] + WhiteKey.Width/2 + Octave.KeySpacing/2
Octave.KeyOffsets["A#"] = Octave.KeyRight["B"] - BlackKey.KeyBaseWidth - Octave.KeySpacing

#Offsets from the key extension to place the base. (white keys only)
# #Calculation is relative to rectangle centers 
Octave.KeyBaseOffsets = {
    "C":-WhiteKey.Width/2 + Octave.KeyBaseWidths["C"]/2,
    "D":0,
    "E":WhiteKey.Width/2 - Octave.KeyBaseWidths["E"]/2,
    "F":-WhiteKey.Width/2 + Octave.KeyBaseWidths["F"]/2,
    "G":(Octave.KeyOffsets["F#"]+Octave.KeyOffsets["G#"])/2 - Octave.KeyOffsets["G"],
    "A":(Octave.KeyOffsets["G#"]+Octave.KeyOffsets["A#"])/2 - Octave.KeyOffsets["A"],
    "B":WhiteKey.Width/2 - Octave.KeyBaseWidths["B"]/2,
}

#Adjust widths based on the black key positioning
#The size is the distance between the two keys, minus the 2x the spacing
Octave.KeyBaseWidths["D"] = Octave.KeyOffsets["D#"]-Octave.KeyOffsets["C#"] - BlackKey.KeyBaseWidth - Octave.KeySpacing*2
Octave.KeyBaseWidths["G"] = Octave.KeyOffsets["G#"]-Octave.KeyOffsets["F#"] - BlackKey.KeyBaseWidth - Octave.KeySpacing*2
Octave.KeyBaseWidths["A"] = Octave.KeyOffsets["A#"]-Octave.KeyOffsets["G#"] - BlackKey.KeyBaseWidth - Octave.KeySpacing*2


class Base(object):
    Height = WallThickness
    Width = Octave.Width+5
    def Obj(self):
        base = cq.Workplane().box(self.Width, KeyCommon.TotalLength, self.Height) \
            .translate((0, KeyCommon.HiddenLength-KeyCommon.TotalLength/2, 0))

        base += self.Pivot()

        return base

    def Pivot(self):
        spikeHeight = 7
        pivot = cq.Workplane("YZ").move(KeyCommon.PivotPos.x, 0) \
            .move(5, self.Height/2) \
            .line(0, KeyCommon.Travel+KeyCommon.Height/2+KeyCommon.PivotPos.y-spikeHeight) \
            .line(-5,spikeHeight).line(-5,-spikeHeight) \
            .line(0,-(KeyCommon.Travel+KeyCommon.Height/2+KeyCommon.PivotPos.y-spikeHeight)).close() \
            .extrude(self.Width/2, both=True)
        
        return pivot

    def GetPosition(self):
        return cq.Vector(Octave.Width/2, 0, -KeyCommon.Height/2-self.Height/2-KeyCommon.Travel)

    def Show(self):
        show_object(self.Obj().translate(self.GetPosition()), options={"color":(0,127,127)})


Octave().Show()
Base().Show()

