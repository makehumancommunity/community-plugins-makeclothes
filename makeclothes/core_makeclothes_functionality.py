from .mhmesh import MHMesh
from .material import MHMaterial
import json, math, re, os, uuid, shutil
import mathutils
from mathutils import Vector

_knownMeshes = {}                       # place to hold all jsons of meshes, used not to reload them again and again
                                        # normally there will be only a few meshes on disk

def _loadMeshJson(obj):
    meshtype = "hm08"                   # preset mesh  name
    if hasattr (obj, "MhMeshType"):
        meshtype = obj.MhMeshType

    if meshtype in _knownMeshes:        # check if we already have the mesh
        return (meshtype, _knownMeshes[meshtype])

    meshfilename =  meshtype + ".config"
    meshfile = os.path.join(os.path.dirname(__file__), "data", meshfilename)
    try:
        cfile = open (meshfile, "r")
    except IOError:
        return (meshtype, "")
    else:
        jlines = json.load(cfile)
        cfile.close()
        _knownMeshes[meshtype] = jlines     # we got a new mesh
        return (meshtype, jlines)

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
        self.rigidMatch = None
        self.closestHumanVertexIndices = [-1, -1, -1]
        self.weights = [0.0, 0.0, 0.0]
        self.distance = [0.0, 0.0, 0.0]
        self.x = clothesVertexX
        self.y = clothesVertexY
        self.z = clothesVertexZ
        self.closestHumanVertexCoordinates = [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]

    def markExact(self, humanVertexIndex):
        self.exactMatch = humanVertexIndex

    def markRigid(self, humanVertexIndex):
        self.rigidMatch = humanVertexIndex

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

            # write distances dx, dy, dz according to makehuman order
            return "%d %d %d %.4f %.4f %.4f %.4f %.4f %.4f" % (v1, v2, v3, w1, w2, w3, dx, dz, -dy)
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

    def __init__(self, clothesObj, humanObj, exportName="clothes", exportRoot="/tmp", license="CC0", author="unknown", description="No description", context=None):
        self.clothesObj = clothesObj
        self.humanObj = humanObj
        if context:
            self.clothesmesh = MHMesh(clothesObj, context=context, allow_modifiers=True)
        else:
            self.clothesmesh = MHMesh(clothesObj)
        self.humanmesh = MHMesh(humanObj)

        self.vertexMatches = []
        self.exportName = exportName
        self.exportRoot = exportRoot
        self.exportLicense = license
        self.exportAuthor = author
        self.exportDescription = description
        self.scales = [1.0, 1.0, 1.0]           # x_scale, y_scale, z_scale
        self.deleteVerticesOutput = ""
        self.clothesmesh.getAdditionalIndices() 
        self.clothesmesh.getUVforExport()       # method to assign UVs to mesh

    #
    # here the work is done. __init__ cannot provide proper return codes
    #
    def make(self):

        self.bodyPart = self.clothesObj.MhOffsetScale       # get the scalings
        if len(self.bodyPart) == 0:
            return (False, "No scaling defined")

        (self.baseMeshType, self.meshConfig) = _loadMeshJson(self.humanObj)    # load parameters for scales according to mesh
        if len(self.meshConfig) == 0:
            return (False, "Cannot open configuration file for " + self.baseMeshType)

        if self.bodyPart not in  self.meshConfig["dimensions"]:                 # check if we have the scalings
            return (False, "Cannot evaluate offsets for " + self.bodyPart)

        # also the groups have been tested we should avoid going on with an unknown group
        #
        (b, vgroupname) = self.findClosestVertices()
        if b is False:
            return (False, "Cannot create search tree for group " + vgroupname)

        self.findBestFaces()
        self.findWeightsAndDistances()
        self.evaluateDeleteVertices()

        self.dirName = None
        self.cleanedName = None

        self.setupTargetDirectory()

        # 
        # get dimensions of the selected BodyPart (values from json are blender values)
        #
        dims = self.meshConfig["dimensions"][self.bodyPart]
        self.minmax = {
            'xmin': dims['xmin'], 'xmax': dims['xmax'],
            'ymin': dims['ymin'], 'ymax': dims['ymax'],
            'zmin': dims['zmin'], 'zmax': dims['zmax']
        }
        self.scales[0] = self.humanmesh.getScale (dims['xmin'], dims['xmax'], 0)
        self.scales[2] = self.humanmesh.getScale (dims['ymin'], dims['ymax'], 1) # scales-index
        self.scales[1] = self.humanmesh.getScale (dims['zmin'], dims['zmax'], 2) # y and z are changed

        #
        # write the output files and check for errors
        #
        (b, hint) = self.writeMhClo()
        if b is False:
            return (False, hint)
        (b, hint) = self.writeObj()
        if b is False:
            return (False, hint)
        (b, hint) = self.writeMhMat()
        if b is False:
            return (False, hint)

        if True:
            self.writeDebug()
            self.selectHumanVertices()
        return (True, "")

    def findClosestVertices(self):
        for vgroupIdx in self.clothesmesh.vertexGroupNames.keys():
            vgroupName = self.clothesmesh.vertexGroupNames[vgroupIdx]
            clothesVertices = self.clothesmesh.vertexGroupVertices[vgroupIdx]
            vertexIndexMap = self.clothesmesh.vertexGroupVertexIndexMap[vgroupIdx]

            # determine kd tree, also delivers number of vertices per group
            # 3 means rigid group, then an array is given
            #
            (size, kdtree) = self.humanmesh.vertexGroupKDTree(vgroupName) 
            if size == 0:    # empty group
                return (False, vgroupName)

            i = 0

            #
            # special code for rigid group
            #
            if size == 3:
                for vertex in clothesVertices:
                    vertexMatch = _VertexMatch(i, vertex[0], vertex[1], vertex[2])  # idx x y z
                    i = i + 1
                    hCoord = []
                    j = 0
                    for vert in kdtree:     # an array in this case
                        vertexMatch.markRigid(vert.index)
                        vertexMatch.closestHumanVertexIndices[j] = vert.index
                        vertexMatch.closestHumanVertexCoordinates[j] = vert.co
                        hCoord.append(self.humanmesh.allVertexCoordinates[vert.index])
                        j += 1
                    self.vertexMatches.append(vertexMatch)
                continue

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

        return (True, "")

    def findBestFaces(self):
        # In this method we will go through the vertexmatches and if needed switch which vertices are selected so that all
        # vertices belong to the same face.
        for vm in self.vertexMatches:
            if not vm.exactMatch and not vm.rigidMatch:
                faceMatches = []
                maxScore = 1
                for i in [0, 1, 2]:
                    vertIdx = vm.closestHumanVertexIndices[i]
                    for polygon in self.humanmesh.vertPolygons[vertIdx]:
                        faceIdx = polygon.index
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
                # TODO: could be that further improvement like Thomas' mid vertex should be done

                # To make the algorithm understandable I change our 3 vertices to triangle ABC and use Blender
                # Vectors to be able to use internal functions like cross, dot, normal whatever you need
                # For all vectors I use only capital letters, reading is simplified imho

                A = Vector(self.humanmesh.allVertexCoordinates[vertexMatch.closestHumanVertexIndices[0]])
                B = Vector(self.humanmesh.allVertexCoordinates[vertexMatch.closestHumanVertexIndices[1]])
                C = Vector(self.humanmesh.allVertexCoordinates[vertexMatch.closestHumanVertexIndices[2]])

                # We need the normal for this triangle. Normally it is calculated with cross-product using the
                # distance of e.g. B-A and C-A, but blender has a function implemented for that

                N= mathutils.geometry.normal (A, B, C)
                # print ("normal vector is " + str(N))

                # The vertex on the clothes is the Vector Q
                Q = Vector(( vertexMatch.x, vertexMatch.y, vertexMatch.z))

                # transform normal vector to corner of triangle and recalculate length 
                # new vector is R (direction is the same)
                QA = Q - A
                R = Q - N * QA.dot(N)

                # now weight the triangle multiplied with the normal
                # 
                BA = B-A
                BA.normalize()
                NBA = N.cross(BA)
                NBA.normalize()

                AC = A-C
                BC = B-C
                RC = R-C

                # we are using barycentric coordinates to determine the weights. Normally you have
                # to do a projection. To get the values of all dimensions we can use the scalar or dot.product
                # of our vectors. This is also called projection product ...
                # the barycentric calculation now could be rewritten as
                #
                # WeightA = ( BC.NBA * RC.BA - BC.BA * RC.NBA) / (BA.AC * BC.NBA - BC.AC * AC.NBA)
                # WeightB = (-AC.NBA * RC.BA + AC.BA * RC.NBA) / (BA.AC * BC.NBA - BC.AC * AC.NBA)
                #
                # WeightC = 1 - WeightA - WeightB

                a00 = AC.dot(BA)
                a01 = BC.dot(BA)
                a10 = AC.dot(NBA)
                a11 = BC.dot(NBA)
                b0 = RC.dot(BA)
                b1 = RC.dot(NBA)

                det = a00*a11 - a01*a10

                wa = (a11*b0 - a01*b1)/det
                wb = (-a10*b0 + a00*b1)/det
                wc = 1 - wa - wb

                # calculate the distance with the weighted vectors and subtract that result from our point Q
                D = Q - (wa * A + wb * B + wc * C)

                # add the values
                vertexMatch.setWeights(wa, wb, wc)
                vertexMatch.distance = [D[0] * self.scales[0], D[1] * self.scales[1], D[2] * self.scales[2] ]
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
        try:
            with open(outputFile,"w") as f:
                f.write("# This is a clothes file for MakeHuman Community, exported by MakeClothes 2\n#\n")
                f.write("# author: "  + self.exportAuthor + "\n")
                f.write("# license: " + self.exportLicense + "\n#\n")
                f.write("# description: " + self.exportDescription + "\n#\n")
                f.write("basemesh " + self.baseMeshType + "\n\n")
                f.write("# Basic info:\n")
                f.write("name " + self.exportName + "\n")

                # add the tags
                #
                for tag in self.clothesObj.MhClothesTags.split(","):
                    if len(tag) > 0:
                        f.write("tag " + tag + "\n")

                f.write("obj_file " + self.cleanedName + ".obj\n")
                f.write("material " + self.cleanedName + ".mhmat" + "\n\n")
                f.write("uuid " + str(uuid.uuid4()) + "\n")
                f.write("x_scale " + str(self.minmax['xmin']) + " " + str(self.minmax['xmax']) + " " + str(round(self.scales[0], 4)) + "\n")
                f.write("y_scale " + str(self.minmax['zmin']) + " " + str(self.minmax['zmax']) + " " + str(round(self.scales[1], 4)) + "\n")
                f.write("z_scale " + str(self.minmax['ymin']) + " " + str(self.minmax['ymax']) + " " + str(round(self.scales[2], 4)) + "\n")
                f.write("z_depth " + str(self.clothesObj.MhZDepth) + "\n\n")
                f.write("# Vertex info:\n")
                f.write("verts 0\n")
                for vm in self.vertexMatches:
                    f.write(str(vm) + "\n")

                # write the delete vertice numbers of the basemesh
                if self.deleteVerticesOutput != "":
                    f.write ("\ndelete_verts\n" + self.deleteVerticesOutput + "\n")
                f.close()
                return (True, "")
        except EnvironmentError:
            return (False, "Cannot write " + outputFile)

    def writeObj(self):
        # Yes, I'm aware there is a wavefront exporter in the blender API already. However, we need to make
        # sure that we're using the proper origin and scale.

        obj = self.clothesObj
        mesh = self.clothesmesh.data

        outputFile = os.path.join(self.dirName, self.cleanedName + ".obj")
        #
        # scale, rotation and origin are not necessary because everything has be applied before
        #
        try:
            with open(outputFile,"w") as f:
                f.write("# This is a clothes file for MakeHuman Community, exported by MakeClothes 2\n#\n")
                f.write("# author: "  + self.exportAuthor + "\n")
                f.write("# license: " + self.exportLicense + "\n#\n")
                for v in mesh.vertices:
                    f.write("v %.4f %.4f %.4f\n" % (v.co[0], v.co[2], -v.co[1]))

                # check if we have a texture
                # in this case we create vt and f a/b lines per vertex
                # else create only f lines with one parameter per vertex
                #
                if self.clothesmesh.has_uv:
                    texVerts = self.clothesmesh.texVerts
                    nTexVerts = len(texVerts)
                    for vtn in range(nTexVerts):
                        uv = texVerts[vtn]
                        f.write("vt %.4f %.4f\n" % (uv[0], uv[1]))

                    uvFaceVerts = self.clothesmesh.uvFaceVerts
                    for polygon in mesh.polygons:
                        uvVerts = uvFaceVerts[polygon.index]
                        line = ["f"]
                        for n,v in enumerate(polygon.vertices):
                            (vt, uv) = uvVerts[n]
                            line.append("%d/%d" % (v+1, vt+1))
                        f.write(" ".join(line))
                        f.write("\n")

                else:
                    for p in mesh.polygons:
                        f.write("f")
                        for i in p.vertices:
                            f.write(" %d" % (i + 1))
                        f.write("\n")
                f.close()
                return (True, "")
        except EnvironmentError:
            return (False, "Cannot write " + outputFile)

    def writeMhMat(self):
        mhmat = MHMaterial(self.clothesObj)
        outputFile = os.path.join(self.dirName,self.cleanedName + ".mhmat")
        try:
            with open(outputFile,"w") as f:
                f.write("# This is a clothes file for MakeHuman Community, exported by MakeClothes 2\n#\n")
                f.write("# author: " + self.exportAuthor + "\n")
                f.write("# license: " + self.exportLicense + "\n#\n")
                f.write("name " + self.exportName + " material\n\n")

                f.write("// Color shading attributes\n")
                f.write("diffuseColor  %.4f %.4f %.4f\n" % (mhmat.diffuseColor[0], mhmat.diffuseColor[1], mhmat.diffuseColor[2]))
                f.write("specularColor  0.8 0.8 0.8\n")
                f.write("shininess %.4f\n" % mhmat.shininess)
                f.write("opacity 1\n\n")

                f.write("// Textures and properties\n\n")

                if mhmat.diffuseTexture:
                    bn = os.path.basename(mhmat.diffuseTexture)
                    dest = os.path.join(self.dirName, bn)
                    shutil.copyfile(mhmat.diffuseTexture, dest)
                    f.write("diffuseTexture " + bn)
                f.close()
                return (True, "")
        except EnvironmentError:
            return (False, "Cannot write " + outputFile)
