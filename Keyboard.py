import cadquery as cq
import glm
import time

t1 = time.time()

#Stop VS-Code undefined function error
if "show_object" not in globals():
    def func(*args, **kwargs):
        pass
    show_object = func


WallThickness = 3
Small = 1e-5
ExportFolder = "Export/"

BitSize = 3

class Octave(object):
    Width = 24*7
    KeySpacing = 1.5

    KeyList = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]

    KeyOffsets = {}
    KeyLeft = {}
    KeyRight = {}
    KeyBaseWidths = {}
    KeyBaseOffsets = {}
    GlobalKeyMountPos ={}

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
    
    def Export(self):
        for key in self.Keys:
            cq.exporters.export(key.Obj, ExportFolder+key.Key+".stl")


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

        common = cq.Workplane().box(self.Width, self.TotalLength, self.Height) \
            .translate((0,self.TotalLength/2-self.KeyBaseLength,0))

        common = self.SpringCut(common)
        common = self.SpacerCut(common)
        common = self.PivotCut(common)

        self.Obj = common


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
    SpringHoleDiam = SpringDiameter+1
    SpringPos = HiddenLength-WallThickness-SpringHoleDiam/2-2

    def SpringCut(self, common):
        cut = common.faces(">Z").workplane() \
            .move(self.SpringHoleDiam/2+0.5, self.SpringPos).circle(self.SpringHoleDiam/2).mirrorY() \
            .cutThruAll()

        return cut


class WhiteKey(object):
    ExtendedLength = 40
    KeyBaseLength = KeyCommon.ExposedLength-ExtendedLength
    Width = Octave.Width/7-Octave.KeySpacing

    def __init__(self, key):
        self.Key = key

        keyobj = self.KeyBase() + self.Extension()

        keyobj = keyobj.faces("<Z").faces("<Y").shell(-WallThickness)

        self.Obj = keyobj

    def KeyBase(self):
        keybase = KeyCommon(self.KeyBaseLength, Octave.KeyBaseWidths[self.Key]).Obj

        return keybase.translate((Octave.KeyBaseOffsets[self.Key], 0, 0))

    def Extension(self):
        keyextend = cq.Workplane().box(self.Width, self.ExtendedLength, KeyCommon.Height)

        return keyextend.translate((0, -(self.KeyBaseLength+self.ExtendedLength/2), 0))

    def GetPosition(self):
        return cq.Vector(self.Width/2+Octave.KeyOffsets[self.Key], 0, 0)

    def Show(self):
        show_object(self.Obj.translate(self.GetPosition()), options={"color":(255,255,255), "alpha":0})

#Black key is positioned relative to the center of the white key
class BlackKey(object):
    KeyBaseLength = WhiteKey.KeyBaseLength-Octave.KeySpacing
    KeyBaseWidth = Octave.Width/12-Octave.KeySpacing

    def __init__(self, key):
        self.Key = key

        self.Common = KeyCommon(self.KeyBaseLength, self.KeyBaseWidth)
        self.TotalLength = self.Common.TotalLength
        
        keyobj = self.Common.Obj
        keyobj = self.Keytop(keyobj)

        keyobj = keyobj.faces("<Z").faces("<Y").shell(-WallThickness)

        self.Obj = keyobj

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
        show_object(self.Obj.translate(self.GetPosition()), options={"color":(20,20,20), "alpha":0})


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


#Global positions of the center of the mounts of each key
Octave.GlobalKeyMountPos ={
    "C":Octave.KeyOffsets["C"]+Octave.KeyBaseOffsets["C"]+ WhiteKey.Width/2,
    "C#":Octave.KeyOffsets["C#"] + WhiteKey.Width/2,
    "D":Octave.KeyOffsets["D"]+Octave.KeyBaseOffsets["D"]+ WhiteKey.Width/2,
    "D#":Octave.KeyOffsets["D#"] + WhiteKey.Width/2,
    "E":Octave.KeyOffsets["E"]+Octave.KeyBaseOffsets["E"]+ WhiteKey.Width/2,
    "F":Octave.KeyOffsets["F"]+Octave.KeyBaseOffsets["F"]+ WhiteKey.Width/2,
    "F#":Octave.KeyOffsets["F#"] + WhiteKey.Width/2,
    "G":Octave.KeyOffsets["G"]+Octave.KeyBaseOffsets["G"]+ WhiteKey.Width/2,
    "G#":Octave.KeyOffsets["G#"] + WhiteKey.Width/2,
    "A":Octave.KeyOffsets["A"]+Octave.KeyBaseOffsets["A"]+ WhiteKey.Width/2,
    "A#":Octave.KeyOffsets["A#"] + WhiteKey.Width/2,
    "B":Octave.KeyOffsets["B"]+Octave.KeyBaseOffsets["B"]+ WhiteKey.Width/2
}


class KeySpacer(object):

    WallSize = 7
    WallThick = 3
    Gap = 0.2

    def __init__(self):
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

        self.Obj = align

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
    Height = 4
    Width = Octave.Width+5

    def __init__(self):
        base = cq.Workplane().box(self.Width, KeyCommon.TotalLength, self.Height) \
            .translate((0, KeyCommon.HiddenLength-KeyCommon.TotalLength/2, 0))

        base = self.SpringCuts(base)
        base += self.Pivot()

        # Fillet along Pivot
        base = base.edges(cq.selectors.BoxSelector(
            (-self.Width-1, KeyCommon.PivotPos.x-5-1, 0),
            (self.Width+1, KeyCommon.PivotPos.x+5+1, self.Height),
            ()
        )).fillet(BitSize/2-Small)

        self.Obj = base

    def Pivot(self):
        spikeHeight = 7
        pivot = cq.Workplane("YZ").move(KeyCommon.PivotPos.x, 0) \
            .move(5, self.Height/2) \
            .line(0, KeyCommon.Travel+KeyCommon.Height/2+KeyCommon.PivotPos.y-spikeHeight) \
            .line(-5,spikeHeight).line(-5,-spikeHeight) \
            .line(0,-(KeyCommon.Travel+KeyCommon.Height/2+KeyCommon.PivotPos.y-spikeHeight)).close() \
            .extrude(self.Width/2, both=True)
        
        return pivot

    def SpringCuts(self, base):
        for key in Octave.KeyList:
            base = base.faces(">Z").workplane(centerOption="CenterOfBoundBox") \
                .center(Octave.GlobalKeyMountPos[key]-Octave.Width/2, KeyCommon.TotalLength/2-KeyCommon.HiddenLength) \
                .move(KeyCommon.SpringHoleDiam/2+0.5, KeyCommon.SpringPos).circle(KeyCommon.SpringHoleDiam/2).mirrorY() \
                .cutThruAll()

        return base


    def ShowKeySpacers(self):
        pos = self.GetPosition() + cq.Vector((-Octave.Width/2, 0, self.Height/2))

        spacer = KeySpacer().Obj

        show_object(spacer.translate(
            cq.Vector(Octave.GlobalKeyMountPos["C"]-Octave.KeyBaseWidths["C"]/2-Octave.KeySpacing/2, 0, 0) + pos
        ), options={"alpha":0.5})

        for key in Octave.KeyList:
            if not "#" in key:
                show_object(spacer.translate(
                    cq.Vector(Octave.GlobalKeyMountPos[key]+Octave.KeyBaseWidths[key]/2+Octave.KeySpacing/2, 0, 0) + pos
                ), options={"alpha":0.5})
            else:
                show_object(spacer.translate(
                    cq.Vector(Octave.GlobalKeyMountPos[key]+BlackKey.KeyBaseWidth/2+Octave.KeySpacing/2, 0, 0) + pos
                ), options={"alpha":0.5})


    def GetPosition(self):
        return cq.Vector(Octave.Width/2, 0, -KeyCommon.Height/2-self.Height/2-KeyCommon.Travel)

    def Show(self):
        show_object(self.Obj.translate(self.GetPosition()), options={"color":(0,127,127)})

        self.ShowKeySpacers()

    def Export(self):
        cq.exporters.export(self.Obj, ExportFolder+"KeyboardBase.stl")


print()
print("Runtime:")

t2 = time.time()
print(F"    Initialize: {t2-t1:.6f}s")

#= Octave =
octave = Octave()
octave.Show()

t3 = time.time()
print(F"    Octave:     {t3-t2:.6f}s")

#= Base =
base = Base()
base.Show()

t4 = time.time()
print(F"    Base:       {t4-t3:.6f}s")

#= Export =
octave.Export()
base.Export()

#= Results =
t5 = time.time()
print(F"    Export:     {t5-t4:.6f}s")

print(F"    :: Total :: {t5-t1:.6f}s")
print()

