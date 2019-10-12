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

            # Somewhat confusingly, order is here XYZ while normal MakeHuman order is XZY
            return "%d %d %d %.4f %.4f %.4f %.4f %.4f %.4f" % (v1, v2, v3, w1, w2, w3, dx, dy, dz)
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

        if True:
            self.writeDebug()
            self.selectHumanVertices()

    def findClosestVertices(self):
        for vgroupIdx in self.clothesmesh.vertexGroupNames.keys():
            vgroupName = self.clothesmesh.vertexGroupNames[vgroupIdx]
            clothesVertices = self.clothesmesh.vertexGroupVertices[vgroupIdx]
            vertexIndexMap = self.clothesmesh.vertexGroupVertexIndexMap[vgroupIdx]

            kdtree = self.humanmesh.vertexGroupKDTree(vgroupName)  # this function I defined in mhmesh.py
            i = 0
            if type(kdtree) is not bool:
                print(type(kdtree))  # well that's one method to only allow a tree, maybe not the best, error treatment should look different :P

                for vertex in clothesVertices:

                    # Find the closest 3 vertices, we consider 0.0001 as an exact match
                    vertexMatch = _VertexMatch(vertexIndexMap[i], vertex[0], vertex[1], vertex[2])  # idx x y z
                    hCoord = []
                    j = 0
                    exact = False
                    for (co, index, dist) in kdtree.find_n(vertex, 3):
                        # print("    ", co, index, dist)
                        if dist < 0.0001:
                            vertexMatch.markExact(index)
                            exact = True
                        elif exact is False:
                            vertexMatch.closestHumanVertexIndices[j] = index
                            vertexMatch.closestHumanVertexCoordinates[j] = co
                            hCoord.append(self.humanmesh.allVertexCoordinates[index])
                            j += 1
                    if exact is False:
                        vertexMatch.closestHumanVertexCoordinates = hCoord
                    self.vertexMatches.append(vertexMatch)

    # def findClosestVertices(self):
    #     for vgroupIdx in self.clothesmesh.vertexGroupNames.keys():
    #         vgroupName = self.clothesmesh.vertexGroupNames[vgroupIdx]
    #         clothesVertices = self.clothesmesh.vertexGroupVertices[vgroupIdx]
    #         vertexIndexMap = self.clothesmesh.vertexGroupVertexIndexMap[vgroupIdx]
    #
    #         i = 0
    #         for vertex in clothesVertices:
    #             vertexMatch = _VertexMatch(vertexIndexMap[i], vertex[0], vertex[1], vertex[2]) # idx x y z
    #             exact = self.humanmesh.getVertexAtExactLocation(vgroupName, vertex[0], vertex[1], vertex[2])
    #             if not exact is None:
    #                 vertexMatch.markExact(exact)
    #             else:
    #                 closest = self.humanmesh.findClosestThreeVertices(vgroupName, vertex[0], vertex[1], vertex[2])
    #                 vertexMatch.setClosestIndices(closest[0], closest[1], closest[2])
    #                 hCoord = []
    #                 hCoord.append(self.humanmesh.allVertexCoordinates[closest[0]])
    #                 hCoord.append(self.humanmesh.allVertexCoordinates[closest[1]])
    #                 hCoord.append(self.humanmesh.allVertexCoordinates[closest[2]])
    #                 vertexMatch.closestHumanVertexCoordinates = hCoord
    #             self.vertexMatches.append(vertexMatch)

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

                distance[0] = vertexMatch.x - medianPoint[0]
                distance[1] = vertexMatch.y - medianPoint[1]
                distance[2] = vertexMatch.z - medianPoint[2]
            vertexMatch.distance = distance

    def setupTargetDirectory(self):
        cleanedName = re.sub(r'\s+',"_",self.exportName)
        self.cleanedName = re.sub(r'[./\\]+', "", cleanedName)
        self.dirName = os.path.join(self.exportRoot,cleanedName)
        if not os.path.exists(self.dirName):
            os.makedirs(self.dirName)

    def _distance(self, co1, co2):
        xd = co1[0] - co2[0]
        yd = co1[1] - co2[1]
        zd = co1[2] - co2[2]
        x2 = xd * xd
        y2 = yd * yd
        z2 = zd * zd
        return math.sqrt(x2+y2+z2)

    def writeDebug(self):
        outputFile = os.path.join(self.dirName, self.cleanedName + ".debug.csv")
        with open(outputFile, "w") as f:
            f.write("clothesIdx,clVertX,clVertY,clVertZ,hIdx1,hVert1x,hVert1y,hVert1z,dist1,hIdx2,hVert2x,hVert2y,hVert2z,dist2,hIdx3,hVert3x,hVert3y,hVert3z,dist3,sumdist,dist1pct,dist2pct,dist3pct,medianX,medianY,medianZ,medianDist\n")
            for vm in self.vertexMatches:

                if not vm.exactMatch: # No need to debug exact matches
                    f.write("%d,%.4f,%.4f,%.4f" % (vm.index, vm.x, vm.y, vm.z)) # clothes
                    sumdist = 0.0
                    dist = [0.0, 0.0, 0.0]
                    mx = 0.0
                    my = 0.0
                    mz = 0.0
                    for i in [0,1,2]:
                        idx = vm.closestHumanVertexIndices[i]
                        co = vm.closestHumanVertexCoordinates[i]
                        dist[i] = self._distance([vm.x,vm.y,vm.z],co)
                        sumdist = sumdist + dist[i]
                        f.write(",%d,%.4f,%.4f,%.4f,%.4f" % (idx,co[0],co[1],co[2],dist[i])) # human
                        mx = mx + co[0]
                        my = my + co[1]
                        mz = mz + co[2]

                    f.write(",%.4f" % sumdist)

                    for i in [0, 1, 2]:
                        dpct = dist[i] / sumdist
                        f.write(",%.4f" % dpct) # vert distance as fraction of total distance, ie vertex weight

                    mx = mx * (dist[0] / sumdist)
                    my = my * (dist[1] / sumdist)
                    mz = mz * (dist[1] / sumdist)
                    f.write(",%.4f,%.4f,%.4f" % (mx, my, mz)) # median point of human vertices, shifted by weights

                    medianDistance = self._distance([mx,my,mz],[vm.x,vm.y,vm.z])
                    f.write(",%.4f\n" % medianDistance) # distance between median point and clothes vertex

    def selectHumanVertices(self):
        for vm in self.vertexMatches:
            if not vm.exactMatch:
                for i in [0, 1, 2]:
                    idx = vm.closestHumanVertexIndices[i]
                    self.humanObj.data.vertices[idx].select = True


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

