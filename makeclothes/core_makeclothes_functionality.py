from .mhmesh import MHMesh
import math

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

    def setClosestIndices(self, v1, v2, v3):
        self.closestHumanVertexIndices[0] = v1
        self.closestHumanVertexIndices[1] = v2
        self.closestHumanVertexIndices[2] = v3

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

            return "{} {} {} {} {} {}".format(v1, v2, v3, w1, w2, w3)
        else:
            return str(self.exactMatch)

class _MakeClothes():

    def __init__(self, clothesObj, humanObj):
        self.clothesObj = clothesObj
        self.humanObj = humanObj
        self.clothesmesh = MHMesh(clothesObj)
        self.humanmesh = MHMesh(humanObj)
        self.vertexMatches = []

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

    def findWeights(self):
        for vertexMatch in self.vertexMatches:
            if not vertexMatch.exactMatch:
                # TODO: Figure out what the weights actually mean
                vertexMatch.setWeights(0.3, 0.3, 0.3)


def MakeClothes(clothesObj, humanObj):
    mc = _MakeClothes(clothesObj, humanObj)
    mc.findClosestVertices()
    mc.findWeights()

    for vertexMatch in mc.vertexMatches:
        print(vertexMatch)
