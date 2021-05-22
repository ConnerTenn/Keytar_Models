import cadquery as cq
import glm
import time

t1 = time.time()

#Stop VS-Code undefined function error
if "show_object" not in globals():
    def func(*args, **kwargs):
        pass
    show_object = func


WallThickness = 4
Small = 1e-5

BitSize = 3

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

        common = self.SpringCut(common)
        common = self.SpacerCut(common)
        common = self.PivotCut(common)

        return common


    PivotPos = cq.Vector(25, 0) #offset from center

    def PivotCut(self, common):
        cut = common.faces(">X").workplane().move(self.PivotPos.x, self.PivotPos.y-self.Height/2) \
            .line(10,-10).line(-20,0).close() \
            .cutThruAll()

        return cut

    def SpacerCut(self, common):
        width = (KeySpacer.WallThick-Octave.KeySpacing)/2+KeySpacer.Gap
        cut = common.faces(">Z").workplane().move(-self.Width/2+width/2, self.PivotPos.x) \
            .rect(width,KeySpacer.WallSize*2+5*2+5).mirrorY() \
            .cutThruAll()

        return cut


    SpringDiameter = 3
    SpringPos = HiddenLength-WallThickness-(SpringDiameter+1)/2-2

    def SpringCut(self, common):
        cut = common.faces(">Z").workplane() \
            .move(self.SpringDiameter, self.SpringPos).circle((self.SpringDiameter+1)/2).mirrorY() \
            .cutThruAll()

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
        show_object(self.Obj().translate(self.GetPosition()), options={"color":(255,255,255), "alpha":0})

#Black key is positioned relative to the center of the white key
class BlackKey(object):
    KeyBaseLength = WhiteKey.KeyBaseLength-Octave.KeySpacing
    KeyBaseWidth = Octave.Width/12-Octave.KeySpacing

    def __init__(self, key):
        self.Key = key
        self.Common = KeyCommon(self.KeyBaseLength, self.KeyBaseWidth)
        self.TotalLength = self.Common.TotalLength


    def Obj(self):
        key = self.Common.Obj()
        key = self.Keytop(key)

        return key

    TopWidth = KeyBaseWidth-3
    TopLength = KeyBaseLength-3
    TopHeight = 10

    def Keytop(self, key):
        top = key.faces(">Z").workplane(centerOption="CenterOfBoundBox") \
            .center(0,(self.KeyBaseLength+KeyCommon.HiddenLength)/2 - KeyCommon.HiddenLength - self.KeyBaseLength/2) \
            .rect(self.KeyBaseWidth, self.KeyBaseLength) \
            .workplane(offset=self.TopHeight) \
            .move(0,self.KeyBaseLength/2-self.TopLength/2).rect(self.TopWidth, self.TopLength) \
            .loft()
        #.center(0,(self.KeyBaseLength+KeyCommon.HiddenLength)/2-KeyCommon.HiddenLength)
        return top

    def GetPosition(self):
        return cq.Vector(WhiteKey.Width/2+Octave.KeyOffsets[self.Key], 0, 0)

    def Show(self):
        show_object(self.Obj().translate(self.GetPosition()), options={"color":(20,20,20), "alpha":0})


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


class KeySpacer(object):

    WallSize = 7
    WallThick = 3
    Gap = 0.2

    def Obj(self):
        align = cq.Workplane("YZ").move(KeyCommon.PivotPos.x, 0) \
        .move(self.WallSize+5, self.Gap) \
        .line(0, KeyCommon.Travel-self.Gap) \
        .tangentArcPoint((-self.WallSize*2-5*2,0)) \
        .line(0, -KeyCommon.Travel+self.Gap) \
        .close().extrude(self.WallThick/2, both=True)

        align -= self.PivotCut()

        # align = align.edges("<Z and |X and <Y[-1]").fillet(BitSize)
        align = align.edges(
            cq.selectors.SumSelector(
                cq.selectors.NearestToPointSelector((0,KeyCommon.PivotPos.x-1,0)),
                cq.selectors.NearestToPointSelector((0,KeyCommon.PivotPos.x+1,0))
            )).fillet(BitSize/2)

        return align

    def PivotCut(self):
        spikeHeight = 7
        pivot = cq.Workplane("YZ").move(KeyCommon.PivotPos.x, 0) \
            .move(5+self.Gap, 0) \
            .line(0, KeyCommon.Travel+KeyCommon.Height/2+KeyCommon.PivotPos.y-spikeHeight) \
            .line(-5-self.Gap,spikeHeight+self.Gap).line(-5-self.Gap,-spikeHeight-self.Gap) \
            .line(0,-(KeyCommon.Travel+KeyCommon.Height/2+KeyCommon.PivotPos.y-spikeHeight)).close() \
            .extrude(self.WallThick/2, both=True)
        
        return pivot


class Base(object):
    Height = WallThickness
    Width = Octave.Width+5
    def Obj(self):
        base = cq.Workplane().box(self.Width, KeyCommon.TotalLength, self.Height) \
            .translate((0, KeyCommon.HiddenLength-KeyCommon.TotalLength/2, 0))

        base += self.Pivot()

        # Fillet along Pivot
        base = base.edges(cq.selectors.BoxSelector(
            (-self.Width-1, KeyCommon.PivotPos.x-5-1, 0),
            (self.Width+1, KeyCommon.PivotPos.x+5+1, self.Height),
            ()
        )).fillet(BitSize/2-Small)

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


    def ShowKeySpacers(self):
        pos = self.GetPosition() + cq.Vector((-Octave.Width/2, 0, self.Height/2))

        spacer = KeySpacer().Obj()

        show_object(spacer.translate(
            cq.Vector(Octave.KeyOffsets["C"]-Octave.KeySpacing/2, 0, 0) + pos
        ))

        show_object(spacer.translate(
            cq.Vector(Octave.KeyOffsets["C"]+Octave.KeyBaseWidths["C"]+Octave.KeySpacing/2, 0, 0) + pos
        ))

        show_object(spacer.translate(
            cq.Vector(Octave.KeyOffsets["D"]+Octave.KeyBaseOffsets["D"]+WhiteKey.Width/2-Octave.KeyBaseWidths["D"]/2-Octave.KeySpacing/2, 0, 0) + pos
        ))

        show_object(spacer.translate(
            cq.Vector(Octave.KeyOffsets["D"]+Octave.KeyBaseOffsets["D"]+WhiteKey.Width/2+Octave.KeyBaseWidths["D"]/2+Octave.KeySpacing/2, 0, 0) + pos
        ))

        show_object(spacer.translate(
            cq.Vector(Octave.KeyOffsets["E"]+WhiteKey.Width-Octave.KeyBaseWidths["E"]-Octave.KeySpacing/2, 0, 0) + pos
        ))

        show_object(spacer.translate(
            cq.Vector(Octave.KeyOffsets["F"]-Octave.KeySpacing/2, 0, 0) + pos
        ))

        show_object(spacer.translate(
            cq.Vector(Octave.KeyOffsets["F"]+Octave.KeyBaseWidths["F"]+Octave.KeySpacing/2, 0, 0) + pos
        ))

        show_object(spacer.translate(
            cq.Vector(Octave.KeyOffsets["G"]+WhiteKey.Width/2+Octave.KeyBaseOffsets["G"]-Octave.KeyBaseWidths["G"]/2-Octave.KeySpacing/2, 0, 0) + pos
        ))

        show_object(spacer.translate(
            cq.Vector(Octave.KeyOffsets["G"]+WhiteKey.Width/2+Octave.KeyBaseOffsets["G"]+Octave.KeyBaseWidths["G"]/2+Octave.KeySpacing/2, 0, 0) + pos
        ))

        show_object(spacer.translate(
            cq.Vector(Octave.KeyOffsets["A"]+WhiteKey.Width/2+Octave.KeyBaseOffsets["A"]-Octave.KeyBaseWidths["A"]/2-Octave.KeySpacing/2, 0, 0) + pos
        ))

        show_object(spacer.translate(
            cq.Vector(Octave.KeyOffsets["A"]+WhiteKey.Width/2+Octave.KeyBaseOffsets["A"]+Octave.KeyBaseWidths["A"]/2+Octave.KeySpacing/2, 0, 0) + pos
        ))

        show_object(spacer.translate(
            cq.Vector(Octave.KeyOffsets["B"]+WhiteKey.Width-Octave.KeyBaseWidths["B"]-Octave.KeySpacing/2, 0, 0) + pos
        ))

        show_object(spacer.translate(
            cq.Vector(Octave.KeyOffsets["B"]+WhiteKey.Width+Octave.KeySpacing/2, 0, 0) + pos
        ))


    def GetPosition(self):
        return cq.Vector(Octave.Width/2, 0, -KeyCommon.Height/2-self.Height/2-KeyCommon.Travel)

    def Show(self):
        show_object(self.Obj().translate(self.GetPosition()), options={"color":(0,127,127)})

        self.ShowKeySpacers()

t2 = time.time()
Octave().Show()
t3 = time.time()
Base().Show()
t4 = time.time()

print()
print("Runtime:")
print(F"    Initialize: {t2-t1:.6f}s")
print(F"    Octave:     {t3-t2:.6f}s")
print(F"    Base:       {t4-t3:.6f}s")
print(F"    :: Total :: {t4-t1:.6f}s")
print()

