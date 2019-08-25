from .mhmesh import MHMesh
import math, re, os, uuid

class _VertexMatch():

    def __init__(self, clothesVertexIndex, clothesVertexX, clothesVertexY, clothesVertexZ):
        self.index = clothesVertexIndex
        self.exactMatch = None
        self.closestHumanVertexIndices = [-1, -1, -1]
        self.weights = [0.0, 0.0, 0.0]
        self.distance = [0.0, 0.0, 0.0]
        self.x = clothesVertexX
        self.y = clothesVertexY
        self.z = clothesVertexZ
        self.closestHumanVertexCoordinates = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]

    def markExact(self, humanVertexIndex):
        self.exactMatch = humanVertexIndex

    def setClosestIndices(self, v1, v2, v3, v1c = None, v2c = None, v3c = None ):
        self.closestHumanVertexIndices[0] = v1
        self.closestHumanVertexIndices[1] = v2
        self.closestHumanVertexIndices[2] = v3

        if v1c is None:
            v1c = [0.0, 0.0, 0.0]
        if v2c is None:
            v2c = [0.0, 0.0, 0.0]
        if v3c is None:
            v3c = [0.0, 0.0, 0.0]

        self.closestHumanVertexCoordinates = [v1c, v2c, v3c]

    def setWeights(self, w1, w2, w3):
        self.weights[0] = w1
        self.weights[1] = w2
        self.weights[2] = w3

    def __str__(self):
        if self.exactMatch is None:
            v1 = self.closestHumanVertexIndices[0]
            v2 = self.closestHumanVertexIndices[1]
            v3 = self.closestHumanVertexIndices[2]

            w1 = self.weights[0]
            w2 = self.weights[1]
            w3 = self.weights[2]

            dx = self.distance[0]
            dy = self.distance[1]
            dz = self.distance[2]

            # MakeHuman order is XZY
            return "{} {} {} {} {} {} {} {} {}".format(v1, v2, v3, w1, w2, w3, dx, dz, dy)
        else:
            return str(self.exactMatch)

class MakeClothes():

    def __init__(self, clothesObj, humanObj, exportName="clothes", exportRoot="/tmp"):
        self.clothesObj = clothesObj
        self.humanObj = humanObj
        self.clothesmesh = MHMesh(clothesObj)
        self.humanmesh = MHMesh(humanObj)
        self.vertexMatches = []
        self.exportName = exportName
        self.exportRoot = exportRoot

        self.findClosestVertices()
        self.findWeightsAndDistances()

        self.dirName = None
        self.cleanedName = None

        self.setupTargetDirectory()
        self.writeMhClo()

    def findClosestVertices(self):
        for vgroupIdx in self.clothesmesh.vertexGroupNames.keys():
            vgroupName = self.clothesmesh.vertexGroupNames[vgroupIdx]
            clothesVertices = self.clothesmesh.vertexGroupVertices[vgroupIdx]
            vertexIndexMap = self.clothesmesh.vertexGroupVertexIndexMap[vgroupIdx]

            i = 0
            for vertex in clothesVertices:
                vertexMatch = _VertexMatch(vertexIndexMap[i], vertex[0], vertex[1], vertex[2]) # idx x y z
                exact = self.humanmesh.getVertexAtExactLocation(vgroupName, vertex[0], vertex[1], vertex[2])
                if not exact is None:
                    vertexMatch.markExact(exact)
                else:
                    closest = self.humanmesh.findClosestThreeVertices(vgroupName, vertex[0], vertex[1], vertex[2])
                    vertexMatch.setClosestIndices(closest[0], closest[1], closest[2])
                    hCoord = []
                    hCoord.append(self.humanmesh.allVertexCoordinates[closest[0]])
                    hCoord.append(self.humanmesh.allVertexCoordinates[closest[1]])
                    hCoord.append(self.humanmesh.allVertexCoordinates[closest[2]])
                    vertexMatch.closestHumanVertexCoordinates = hCoord
                self.vertexMatches.append(vertexMatch)

    def findWeightsAndDistances(self):
        for vertexMatch in self.vertexMatches:
            if not vertexMatch.exactMatch:
                # TODO: Figure out what the weights actually mean
                vertexMatch.setWeights(0.333, 0.333, 0.334)

        for vertexMatch in self.vertexMatches:
            distance = [0,0,0]
            if not vertexMatch.exactMatch:
                v1 = self.humanmesh.allVertexCoordinates[vertexMatch.closestHumanVertexIndices[0]]
                v2 = self.humanmesh.allVertexCoordinates[vertexMatch.closestHumanVertexIndices[0]]
                v3 = self.humanmesh.allVertexCoordinates[vertexMatch.closestHumanVertexIndices[0]]

                w1 = vertexMatch.weights[0]
                w2 = vertexMatch.weights[1]
                w3 = vertexMatch.weights[2]

                medianPoint = [0.0, 0.0, 0.0]

                # X for median point is (vert1 x * vert1 weight) + (vert2 x * vert2 weight) (vert3 x * vert3 weight)
                medianPoint[0] = (v1[0] * w1) + (v2[0] * w2) + (v3[0] * w3)
                medianPoint[1] = (v1[1] * w1) + (v2[1] * w2) + (v3[1] * w3)
                medianPoint[2] = (v1[2] * w1) + (v2[2] * w2) + (v3[2] * w3)

                distance[0] = abs(vertexMatch.x - medianPoint[0])
                distance[1] = abs(vertexMatch.y - medianPoint[1])
                distance[2] = abs(vertexMatch.z - medianPoint[2])
            vertexMatch.distance = distance

    def setupTargetDirectory(self):
        cleanedName = re.sub(r'\s+',"_",self.exportName)
        self.cleanedName = re.sub(r'[./\\]+', "", cleanedName)
        self.dirName = os.path.join(self.exportRoot,cleanedName)
        if not os.path.exists(self.dirName):
            os.makedirs(self.dirName)

    def writeMhClo(self):
        outputFile = os.path.join(self.dirName,self.cleanedName + ".mhclo")
        with open(outputFile,"w") as f:
            f.write("# This is a clothes file for MakeHuman Community, exported by MakeClothes 2\n#\n")
            f.write("# author: Unkown\n")
            f.write("# license: CC0\n#\n")
            f.write("basemesh hm08\n\n")
            f.write("# Basic info:\n")
            f.write("name " + self.exportName + "\n")
            f.write("obj_file " + self.cleanedName + ".obj\n")
            f.write("material " + self.cleanedName + ".mhmat" + "\n\n")
            f.write("uuid " + str(uuid.uuid4()) + "\n")
            f.write("# Settings: (I have no idea what the scale is derived from atm)\n")
            f.write("x_scale 5399 11998 1.4800\n")
            f.write("z_scale 962 5320 1.9221\n")
            f.write("y_scale 791 881 2.3298\n")
            f.write("z_depth 50\n\n")
            f.write("# Vertex info:\n")
            f.write("verts 0\n")
            for vm in self.vertexMatches:
                f.write(str(vm) + "\n")


