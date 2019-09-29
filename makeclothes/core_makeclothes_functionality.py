from .mhmesh import MHMesh
from .material import MHMaterial
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
            return "%d %d %d %.4f %.4f %.4f %.4f %.4f %.4f" % (v1, v2, v3, w1, w2, w3, dx, dz, dy)
        else:
            return str(self.exactMatch)

class MakeClothes():

    def __init__(self, clothesObj, humanObj, exportName="clothes", exportRoot="/tmp", license="CC0", description="No description"):
        self.clothesObj = clothesObj
        self.humanObj = humanObj
        self.clothesmesh = MHMesh(clothesObj)
        self.humanmesh = MHMesh(humanObj)
        self.vertexMatches = []
        self.exportName = exportName
        self.exportRoot = exportRoot
        self.exportLicense = license
        self.exportDescription = description

        self.findClosestVertices()
        self.findWeightsAndDistances()

        self.dirName = None
        self.cleanedName = None

        self.setupTargetDirectory()
        self.writeMhClo()
        self.writeObj()
        self.writeMhMat()

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
                # TODO:    It would probably be more efficient to do all this by building a numpy array
                # TODO:    and applying all transformations on that

                # The following algorithm calculates the distances between a vertex point (on the clothes)
                # and the three vertices (on the human) that have previously been found to be closest.
                # It then calculates weights based on how large a percentage of the total distance each
                # distance encompass. 
                #
                # Unfortunately, the algorithm produces disappointing results. As of now, it is unclear
                # if the problem is the chosen vertices, or the approach for calculating the weights.

                v1 = self.humanmesh.allVertexCoordinates[vertexMatch.closestHumanVertexIndices[0]]
                v2 = self.humanmesh.allVertexCoordinates[vertexMatch.closestHumanVertexIndices[1]]
                v3 = self.humanmesh.allVertexCoordinates[vertexMatch.closestHumanVertexIndices[2]]
                
                x = vertexMatch.x
                y = vertexMatch.y
                z = vertexMatch.z
                
                # Squared distances for vertex 1
                x1d = (x - v1[0]) * (x - v1[0])
                y1d = (y - v1[1]) * (y - v1[1])
                z1d = (z - v1[2]) * (z - v1[2])

                # Squared distances for vertex 2
                x2d = (x - v2[0]) * (x - v2[0])
                y2d = (y - v2[1]) * (y - v2[1])
                z2d = (z - v2[2]) * (z - v2[2])

                # Squared distances for vertex 3
                x3d = (x - v3[0]) * (x - v3[0])
                y3d = (y - v3[1]) * (y - v3[1])
                z3d = (z - v3[2]) * (z - v3[2])

                # Euclidian distances
                d1 = math.sqrt(x1d + y1d + z1d)
                d2 = math.sqrt(x2d + y2d + z2d)
                d3 = math.sqrt(x3d + y3d + z3d)

                # Sum of distances
                ds = d1 + d2 + d3

                # Just a safeguard against division of zero
                if ds < 0.00001:
                    ds = 0.00001

                # Distances as fractions of total distance, aka weights
                w1 = d1 / ds
                w2 = d2 / ds
                w3 = d3 / ds

                vertexMatch.setWeights(w1, w2, w3)

        for vertexMatch in self.vertexMatches:
            distance = [0,0,0]
            if not vertexMatch.exactMatch:
                v1 = self.humanmesh.allVertexCoordinates[vertexMatch.closestHumanVertexIndices[0]]
                v2 = self.humanmesh.allVertexCoordinates[vertexMatch.closestHumanVertexIndices[1]]
                v3 = self.humanmesh.allVertexCoordinates[vertexMatch.closestHumanVertexIndices[2]]

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
            f.write("# license: " + self.exportLicense + "\n#\n")
            f.write("# description: " + self.exportDescription + "\n#\n")
            f.write("basemesh hm08\n\n")
            f.write("# Basic info:\n")
            f.write("name " + self.exportName + "\n")
            f.write("obj_file " + self.cleanedName + ".obj\n")
            f.write("material " + self.cleanedName + ".mhmat" + "\n\n")
            f.write("uuid " + str(uuid.uuid4()) + "\n")
            # TODO: Figure out what the scale values are for
            f.write("# Settings: (I have no idea what the scale is derived from atm)\n")
            f.write("x_scale 5399 11998 1.4800\n")
            f.write("z_scale 962 5320 1.9221\n")
            f.write("y_scale 791 881 2.3298\n")
            f.write("z_depth 50\n\n")
            f.write("# Vertex info:\n")
            f.write("verts 0\n")
            for vm in self.vertexMatches:
                f.write(str(vm) + "\n")

    def writeObj(self):
        # Yes, I'm aware there is a wavefront exporter in the blender API already. However, we need to make
        # sure that we're using the proper origin and scale.

        obj = self.clothesObj
        mesh = obj.data
        outputFile = os.path.join(self.dirName, self.cleanedName + ".obj")
        with open(outputFile,"w") as f:
            f.write("# This is a clothes file for MakeHuman Community, exported by MakeClothes 2\n#\n")
            f.write("# license: " + self.exportLicense + "\n#\n")
            texCo = []
            for v in mesh.vertices:
                # TODO: apply scale, origin
                f.write("v %.4f %.4f %.4f\n" % v.co[:])
                texCo.append([0.0, 0.0])
            for face in mesh.polygons:
                for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                    uv_coords = mesh.uv_layers.active.data[loop_idx].uv
                    #f.write("# face idx: %i, vert idx: %i, uvs: %f, %f\n" % (face.index, vert_idx, uv_coords.x, uv_coords.y))
                    texCo[vert_idx] = [uv_coords.x, uv_coords.y]
            for uv in texCo:
                f.write("vt " + str(uv[0]) + " " + str(uv[1]) + "\n")
            for p in mesh.polygons:
                f.write("f")
                for i in p.vertices:
                    f.write(" %d" % (i + 1))
                f.write("\n")

    def writeMhMat(self):
        mhmat = MHMaterial(self.clothesObj)
        outputFile = os.path.join(self.dirName,self.cleanedName + ".mhmat")
        with open(outputFile,"w") as f:
            f.write("# This is a clothes file for MakeHuman Community, exported by MakeClothes 2\n#\n")
            f.write("# author: Unkown\n")
            f.write("# license: " + self.exportLicense + "\n#\n")
            f.write("name " + self.exportName + " material\n\n")

            f.write("// Color shading attributes\n")
            f.write("diffuseColor  %.4f %.4f %.4f\n" % (mhmat.diffuseColor[0], mhmat.diffuseColor[1], mhmat.diffuseColor[2]))
            f.write("specularColor  0.8 0.8 0.8\n")
            f.write("shininess %.4f\n" % mhmat.shininess)
            f.write("opacity 1\n\n")

            f.write("// Textures and properties\n\n")

