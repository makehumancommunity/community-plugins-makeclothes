from .mhmesh import MHMesh
from .material import MHMaterial
import math, re, os, uuid
import mathutils
from mathutils import Vector


def _distance(co1, co2):
    xd = co1[0] - co2[0]
    yd = co1[1] - co2[1]
    zd = co1[2] - co2[2]
    x2 = xd * xd
    y2 = yd * yd
    z2 = zd * zd
    return math.sqrt(x2 + y2 + z2)

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

class _FaceMatch():

    def __init__(self, humanObj, humanFaceIdx, clothesVertCoords):
        self.faceIndex = humanFaceIdx
        poly = humanObj.data.polygons[humanFaceIdx]
        self.participatingVerts = []
        self.score = 1
        mx = 0.0
        my = 0.0
        mz = 0.0
        for vertIdx in poly.vertices:
            self.participatingVerts.append(vertIdx)
            vert = humanObj.data.vertices[vertIdx]
            mx = mx + vert.co[0]
            my = my + vert.co[1]
            mz = mz + vert.co[2]
        mx = mx / len(poly.vertices)
        my = my / len(poly.vertices)
        mz = mz / len(poly.vertices)
        self.medianPoint = [mx, my, mz]
        self.distance = _distance(self.medianPoint, clothesVertCoords)

    def containsVert(self, vertIdx):
        return vertIdx in self.participatingVerts

    def getMedianPoint(self):
        return self.medianPoint

    def getDistance(self):
        return self.distance


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
        self.deleteVerticesOutput = ""

        self.findClosestVertices()
        self.findBestFaces()
        self.findWeightsAndDistances()
        self.evaluateDeleteVertices()

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
                    vertexMatch = _VertexMatch(i, vertex[0], vertex[1], vertex[2])  # idx x y z
                    i = i + 1
                    hCoord = []
                    j = 0
                    exact = False
                    for (co, index, dist) in kdtree.find_n(vertex, 3):
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

    def findFacesForVert(self, vertIdx):
        # There must be a more efficient way to do this
        faces = []
        for poly in self.humanObj.data.polygons:
            if vertIdx in poly.vertices:
                faces.append(poly.index)
        return faces

    def findBestFaces(self):
        # In this method we will go through the vertexmatches and if needed switch which vertices are selected so that all
        # vertices belong to the same face.
        for vm in self.vertexMatches:
            if not vm.exactMatch:
                faceMatches = []
                maxScore = 1
                for i in [0, 1, 2]:
                    vertIdx = vm.closestHumanVertexIndices[i]
                    facesForVert = self.findFacesForVert(vertIdx)
                    for faceIdx in facesForVert:
                        alreadyAdded = False
                        for fm in faceMatches:
                            if fm.faceIndex == faceIdx:
                                alreadyAdded = True
                                fm.score = fm.score + 1  # a face that matches more than one of our verts is more important
                                if fm.score > maxScore:
                                    maxScore = fm.score
                                break
                        if not alreadyAdded:
                            fm = _FaceMatch(self.humanObj, faceIdx, [vm.x, vm.y, vm.z])
                            faceMatches.append(fm)
                bestFaceMatches = []
                if maxScore == 1:
                    bestFaceMatches = faceMatches
                else:
                    for fm in faceMatches:
                        if fm.score == maxScore:
                            bestFaceMatches.append(fm)
                bestFace = None
                for fm in bestFaceMatches:
                    if bestFace is None:
                        bestFace = fm
                    else:
                        if fm.distance < bestFace.distance:
                            bestFace = fm

                # Here "bestFace" should be the face whose median point is the shortest
                # distance away from the clothes vert

                # We should now ideally pick those verts in the face which are the
                # closest to the clothes vert. But for the sake of efficiency we
                # will instead pick the first three verts listed in the face

                bestVerts = bestFace.participatingVerts

                vIdxs = [0,0,0]
                vCos = [[0,0,0], [0,0,0], [0,0,0]]

                for i in [0, 1, 2]:
                    idx = bestVerts[i]
                    vIdxs[i] = idx
                    co = self.humanObj.data.vertices[idx].co
                    vCos[i] = [co[0], co[1], co[2]]

                vm.closestHumanVertexIndices = vIdxs
                vm.closestHumanVertexCoordinates = vCos

    def findWeightsAndDistances(self):
        for vertexMatch in self.vertexMatches:
            if not vertexMatch.exactMatch:
                # TODO: the algorithm has to be improved further, especially the barycentrics are not
                #       100% okay because of the projection, I guess

                # To make the algorithm understandable I change our 3 vertices to triangle ABC and use Blender
                # Vectors to be able to use internal functions like cross, dot, normal whatever you need
                # All vectors I use with only one capital letter, reading is simplified imho

                A = Vector(self.humanmesh.allVertexCoordinates[vertexMatch.closestHumanVertexIndices[0]])
                B = Vector(self.humanmesh.allVertexCoordinates[vertexMatch.closestHumanVertexIndices[1]])
                C = Vector(self.humanmesh.allVertexCoordinates[vertexMatch.closestHumanVertexIndices[2]])

                # We need the normal for this triangle. Normally it is calculated with cross-product using the
                # distance of e.g. B-A and C-A, but blender has a function implemented for that

                N= mathutils.geometry.normal (A, B, C)
                # print ("normal vector is " + str(N))

                # The vertex on the clothes is the Vector Q
                Q = Vector(( vertexMatch.x, vertexMatch.y, vertexMatch.z))

                # calculate the vector I (intersection) where the line given by two Vectors and plane intersect
                # (N is the direction of the normal-vector), Blender has a internal function for that
                #
                I = mathutils.geometry.intersect_line_plane(Q -20 * N, Q+20*N, A, N)
                # print ("intersection is " + str(I))


                # now calculate projection by simply neglecting the smallest dimension of the
                # normal vector
                NAbs = [abs(N[0]), abs(N[1]), abs(N[2])]

                sv = NAbs[0]
                px = 1
                py = 2
                if ( NAbs[1] < sv):
                    sv = NAbs[1]
                    px = 0
                    py = 2
                if ( NAbs[2] < sv):
                    px = 0
                    py = 1

                # print ("using plane " + str(px) + " " + str(py))

                # we need the barycentic coordinates of I
                # calculate barycentric values (weights) using our projection, triangle ABC
                # WeightA = ((By - Cy) (Ix-Cx) + (Cx-Bx)(Iy-Cy)) / ((By-Cy)(Ax-Cx) + (Cx-Bx)(Ay-Cy))
                # WeightB = ((By - Ay) (Ix-Cx) + (Ax-Bx)(Iy-Cy)) / ((By-Cy)(Ax-Cx) + (Cx-Bx)(Ay-Cy))
                # WeightC = 1 - WeightA - WeightB
                #
                # pre calculate everything we need more than one time

                abx = A[px]-B[px]
                acx = A[px]-C[px]
                acy = A[py]-C[py]
                bay = B[py]-A[py]
                bcy = B[py]-C[py]
                cbx = C[px]-B[px]
                icx = I[px]-C[px]
                icy = I[py]-C[py]

                # evaluate divisor (which is the same in both cases, it is also the determinant)
                dT = bcy * acx + cbx * acy

                # evaluate weights
                wa = (bcy * icx + cbx * icy) / dT
                wb = (bay * icx + abx * icy) / dT
                wc = 1 - wa - wb

                #if wa < 0 or wb < 0 or wc < 0:
                #   print ("outside")
                #print (wa, wb, wc)

                # calculate the distance with the weighted vectors and subtract that result from our point Q
                D = Q - (wa * A + wb * B + wc * C)

                # add the values
                vertexMatch.setWeights(wa, wb, wc)
                vertexMatch.distance = [D[0], D[1], D[2] ]
            else:
                # for all exact values
                vertexMatch.distance = [0,0,0]

    def setupTargetDirectory(self):
        cleanedName = re.sub(r'\s+',"_",self.exportName)
        self.cleanedName = re.sub(r'[./\\]+', "", cleanedName)
        self.dirName = os.path.join(self.exportRoot,cleanedName)
        if not os.path.exists(self.dirName):
            os.makedirs(self.dirName)

    def writeDebug(self):
        outputFile = os.path.join(self.dirName, self.cleanedName + ".debug.csv")
        with open(outputFile, "w") as f:
            f.write("clothesIdx,clVertX,clVertY,clVertZ,hIdx1,hVert1x,hVert1y,hVert1z,dist1,hIdx2,hVert2x,hVert2y,hVert2z,dist2,hIdx3,hVert3x,hVert3y,hVert3z,dist3,sumdist,dist1pct,dist2pct,dist3pct,medianX,medianY,medianZ,medDistX,medDistY,medDistZ\n")
            for vm in self.vertexMatches:

                if not vm.exactMatch: # No need to debug exact matches
                    f.write("%d,%.4f,%.4f,%.4f" % (vm.index, vm.x, vm.y, vm.z)) # clothes
                    sumdist = 0.0
                    dist = [0.0, 0.0, 0.0]
                    for i in [0,1,2]:
                        idx = vm.closestHumanVertexIndices[i]
                        co = vm.closestHumanVertexCoordinates[i]
                        dist[i] = _distance([vm.x,vm.y,vm.z],co)
                        sumdist = sumdist + dist[i]
                        f.write(",%d,%.4f,%.4f,%.4f,%.4f" % (idx,co[0],co[1],co[2],dist[i])) # human

                    f.write(",%.4f" % sumdist)

                    dpct = [0,0,0]
                    xMedian = 0
                    yMedian = 0
                    zMedian = 0
                    for i in [0, 1, 2]:
                        dpct[i] = dist[i] / sumdist
                        co = vm.closestHumanVertexCoordinates[i]
                        xMedian = xMedian + co[0] * dpct[i]
                        yMedian = yMedian + co[1] * dpct[i]
                        zMedian = zMedian + co[2] * dpct[i]
                        f.write(",%.4f" % dpct[i]) # vert distance as fraction of total distance, ie vertex weight

                    f.write(",%.4f,%.4f,%.4f" % (xMedian, yMedian, zMedian)) # median point of human vertices, shifted by weights

                    medDistX = vm.x - xMedian
                    medDistY = vm.y - yMedian
                    medDistZ = vm.z - zMedian

                    f.write(",%.4f,%.4f,%.4f\n" % (medDistX, medDistY, medDistZ)) # distance between median point and clothes vertex

    def selectHumanVertices(self):
        for vm in self.vertexMatches:
            if not vm.exactMatch:
                for i in [0, 1, 2]:
                    idx = vm.closestHumanVertexIndices[i]
                    self.humanObj.data.vertices[idx].select = True

    # for DeleteVertices test if the assigned delete-group is found on the human
    # and collect vertices belonging to this group

    def evaluateDeleteVertices(self):
        deletegroup = self.clothesObj.MhDeleteGroup
        lastindex = -2
        cnt = 0
        column = 0
        if deletegroup != "":
            vgrp = self.humanObj.vertex_groups

            # get group index and check on human
            #
            if vgrp is not None and deletegroup in vgrp:

                gindex = vgrp[deletegroup].index

                for v in self.humanObj.data.vertices:
                    for g in v.groups:

                        # if the index of the group fits to the current group
                        # print it as sequences when possible
                        #
                        if g.group == gindex:
                            if lastindex + 1 != v.index:
                                if cnt > 1:
                                    self.deleteVerticesOutput += " - " + str(lastindex)

                                # formating after 8 columns do a LF
                                #
                                column += 1
                                if column > 8:
                                    column = 0
                                    self.deleteVerticesOutput += "\n"

                                self.deleteVerticesOutput += " " + str(v.index)
                                cnt = 1
                            else:
                                if lastindex < 0:
                                    self.deleteVerticesOutput += str(v.index)
                                cnt += 1
                            lastindex = v.index
                if cnt > 1:
                    self.deleteVerticesOutput += " - " + str(lastindex)

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
            f.write("# Settings: head vertices and distances\n")
            f.write("x_scale 5399 11998 1.4800\n")
            f.write("z_scale 962 5320 1.9221\n")
            f.write("y_scale 791 881 2.3298\n")
            f.write("z_depth 50\n\n")
            f.write("# Vertex info:\n")
            f.write("verts 0\n")
            for vm in self.vertexMatches:
                f.write(str(vm) + "\n")

            # write the delete vertice numbers of the basemesh
            if self.deleteVerticesOutput != "":
                f.write ("\ndelete_verts\n" + self.deleteVerticesOutput + "\n")


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

