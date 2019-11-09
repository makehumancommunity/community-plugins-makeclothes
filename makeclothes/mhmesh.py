#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy, pprint, mathutils

class MHMesh:

    def __init__(self, obj):
        """
        Parse the mesh into a set of numpy arrays, separated per vertex group.

        There are three dicts here, where each item is an array.

        vertexGroupVertices: The vertex coordinates for each vertex in the group

        vertexGroupVertexIndexMap: A mapping between the position in the vertexGroupVertices
        array and the vertices indexes in the mesh as a whole.

        vertexGroupNames: A mapping between each vertex groups's index and its name
        """

        self.obj = obj
        self.vertexGroupVertices = dict()
        self.vertexGroupNames = dict()
        self.vertexGroupVertexIndexMap = dict()
        self._seedGroups = dict()
        self._seedVertexCoordinates = []
        self.vertPolygons = {}  # will contain all polygons connected to a vertex, needed for efficiency (bestFace search)

        # additional helper indices, filled by getAdditionalIndices
        #
        self.vertEdges = {}     # will contain all edges connected to a vertex
        self.edgePolygons = {}  # will contain all polygons connected to an edge
        self.polygonEdges = {}  # will contain all edges a polygon is using
        self.polygonNeighbors = {} # will contain neighbor-polygons/faces
        self.uvFaceVerts = {}   # will contain UV-vertices for wavefront export 
        self.texVerts = {}      # will vertex number for UV

        self.has_uv = False


        if len(obj.vertex_groups) < 1:
            raise ValueError("This object has no vertex groups. Refusing to continue.")

        for group in obj.vertex_groups:
            if not group.name in self.vertexGroupNames:
                self.vertexGroupNames[int(group.index)] = group.name

        for vertex in obj.data.vertices:
            self.vertPolygons[vertex.index] = []    # supply an index to be filled, will contain all polygons connected to a vertex
            i = int(vertex.index)
            x = float(vertex.co[0])
            y = float(vertex.co[1])
            z = float(vertex.co[2])
            self._seedVertexCoordinates.append( [i, x, y, z] )
            for group in vertex.groups:
                groupIndex = int(group.group)
                if not int(groupIndex) in self.vertexGroupNames:
                    print("Vertex says it has group with index " + str(groupIndex) + ", but that group does not exist. Will ignore this vertex group assignment.")
                else:
                    if not groupIndex in self._seedGroups:
                        self._seedGroups[groupIndex] = []
                    seedGroup = self._seedGroups[groupIndex]
                    vertDef = [int(vertex.index), float(vertex.co[0]), float(vertex.co[1]), float(vertex.co[2])] # Index, x, y, z
                    seedGroup.append(vertDef)

        # supply an index of all polygons connected to a vertex
        #
        for polygon in obj.data.polygons:
            for vertex in polygon.vertices:
                self.vertPolygons[vertex].append(polygon)

        # This somewhat cumbersome routine is here to ensure that vertex.index equals index in the
        # resulting numpy array. It is theoretically possible that the index a vertex says it has
        # is not the same as its position in the object's array with vertices
        self.allVertexCoordinates = numpy.zeros((len(self._seedVertexCoordinates), 3))
        i = 0
        while i < len(self._seedVertexCoordinates):
            idx = self._seedVertexCoordinates[i][0]
            x = self._seedVertexCoordinates[i][1]
            y = self._seedVertexCoordinates[i][2]
            z = self._seedVertexCoordinates[i][3]
            self.allVertexCoordinates[idx][0] = x
            self.allVertexCoordinates[idx][1] = y
            self.allVertexCoordinates[idx][2] = z
            i = i + 1

        for groupIndex in self._seedGroups.keys():
            seed = self._seedGroups[groupIndex]
            vertexArray = numpy.zeros((len(seed), 3))
            indexArray = numpy.zeros(len(seed), dtype="i4")
            i = 0
            for vert in seed:
                vertexArray[i][0] = vert[1] # x
                vertexArray[i][1] = vert[2] # y
                vertexArray[i][2] = vert[3] # z

                # The vertex's index in the entire mesh. When there are several vertex groups, this will be
                # different from the index in the vertex group's array
                indexArray[i] = vert[0]

                i = i + 1

                # TODO:       All vertices should be stored with world space coordinates. Currently they
                # TODO:       are all as local coordinates. Theoretically, all vertices should be multiplied
                # TODO:       with the world matrix as per:
                # TODO:
                # TODO:       v_co_world = obj.matrix_world * obj.data.vertices[0].co
                # TODO:
                # TODO:       This pertains to a per-vertex operation. However, it would be hugely more
                # TODO:       efficient to make this matrix multiplication one the whole numpy vertex array.
                # TODO:       I'd just have to figure out how to do this

            self.vertexGroupVertexIndexMap[groupIndex] = indexArray
            self.vertexGroupVertices[groupIndex] = vertexArray

    def vertexGroupNameToIndex(self, vertexGroupName):
        for idx in self.vertexGroupNames.keys():
            if self.vertexGroupNames[idx] == vertexGroupName:
                return idx
        print("Could not find vertex group " + vertexGroupName + " in this mesh. Available names are:")
        print(self.vertexGroupNames)
        return None

    def vertexGroupKDTree(self, vertexGroupName):
        obj = self.obj

        #
        # first find the group
        for group in obj.vertex_groups:
            if group.name == vertexGroupName:
                #
                # now find all vertices belonging to the group, we first need size of the KDTree
                # we append all vertex numbers to a temporary array, so that we don't have to do the work twice
                #
                print ("Found group" + vertexGroupName)
                tmp_varray = []
                groupIndex = group.index
                for vertex in obj.data.vertices:
                        for vgroup in vertex.groups:
                            if groupIndex == vgroup.group:
                                tmp_varray.append(vertex)

                size = len(tmp_varray)

                # in case we have elements create the kd-tree and balance it
                #
                if size > 0:
                    kd = mathutils.kdtree.KDTree(size)
                    for vertex in tmp_varray:
                        kd.insert(vertex.co, vertex.index)
                    kd.balance()
                    return (kd)

        return False

    # 
    # generates special indices to speed up searches and also used for UV-mapping
    # these indices are only needed for clothes and so it is not part of the init itself
    #
    def getAdditionalIndices(self):
        mesh = self.obj.data

        # supply an index of all edges connected to a vertex
        #
        for vertex in mesh.vertices:
            self.vertEdges[vertex.index] = []

        for edge in mesh.edges:
            for vertex in edge.vertices:
                self.vertEdges[vertex].append(edge)

        # now make a connection between polygons and edges in both directions
        #
        for edge in mesh.edges:
            self.edgePolygons[edge.index] = []

        for polygon in mesh.polygons:
            self.polygonEdges[polygon.index] = []

        # create a polygon-entry for an edge and an edge entry for a polygon,
        # if both vertices of the edge belong to the polygon
        # avoid double entries

        for polygon in mesh.polygons:
            for vertex in polygon.vertices:
                for edge in self.vertEdges[vertex]:
                    v0 = edge.vertices[0]
                    v1 = edge.vertices[1]
                    if (v0 in polygon.vertices) and (v1 in polygon.vertices):
                        if polygon not in self.edgePolygons[edge.index]:
                            self.edgePolygons[edge.index].append(polygon)
                        if edge not in self.polygonEdges[polygon.index]:
                            self.polygonEdges[polygon.index].append(edge)


        # evaluate polygon neighbors (or faces neighbors)
        #
        # an entry containing edge number and polygon number is created

        for polygon in mesh.polygons:
            self.polygonNeighbors[polygon.index] = []

        for polygon in mesh.polygons:
            for edge in self.polygonEdges[polygon.index]:
                for neighbor in self.edgePolygons[edge.index]:
                    if neighbor != polygon:                 # do not add yourself :-)
                        self.polygonNeighbors[polygon.index].append((edge,neighbor))


    #
    # create a UV/Polygon table for a texture
    #
    def getUVforExport(self):
        mesh = self.obj.data
        uvlayer  = mesh.uv_layers.active

        # 
        # in case we have no texture
        #
        if uvlayer is None:
            return 

        #
        # add UV-verts to all polygons as an array
        #
        for polygon in mesh.polygons:
            self.uvFaceVerts[polygon.index] = []

        #
        # collect face vertices and append all to uvFaceVerts list
        # vtn counts numbers of new faces
        # if the distance to neighbor vertex on UV map is less than < 1e-8 an existing entry is used otherwise a new entry is created
        # uvFaceVerts will contain the entry
        #
        vtn = 0
        n = 0

        for polygon in mesh.polygons:
            for vn in polygon.vertices:
                uv = uvlayer.data[n].uv
                n += 1
                #
                # check if the entry is already existing
                #
                found = False
                for (edge,neighbor) in self.polygonNeighbors[polygon.index]:
                    for (vtn1,uv1) in self.uvFaceVerts[neighbor.index]:
                        vec = uv - uv1
                        if vec.length < 1e-8:
                            self.uvFaceVerts[polygon.index].append((vtn1,uv))
                            found = True
                #
                # so we got a new one
                #
                if found is False:
                    self.uvFaceVerts[polygon.index].append((vtn,uv))
                    self.texVerts[vtn] = uv
                    vtn +=1

        self.has_uv = True
        return

    #
    # used to determine x,y,z scale of object
    #
    def getScale(self, num1, num2, dimension):
        verts = self.obj.data.vertices

        # in case we don't have the vertex numbers
        # or distance is 0 return a value of 1
        #
        try:
            coord1 = verts[num1].co
        except:
            return 1
        try:
            coord2 = verts[num2].co
        except:
            return 1
        res = coord1 - coord2
        val = res[dimension]
        if val == 0:
            return 1
        else:
            return abs(val)

    def getDistanceArray(self, vertexGroupName, x, y, z):
        """
        Return an array with distances between the xyz coordinate given and each vertex listed in the vertexCoordinates array.
        The vertexCoordinates array is assumed to be a two-dimensional numpy array with the shape (n,3), i.e each row in the
        table is x, y, z and there is one row per vertex. This is what you'll find in the vertexGroupVertices property
        in this class.

        As a side note, this routine is pretty fast due to leveraging numpy matrix/array operations. The same procedure
        using native python would take quite a lot longer.

        Otherwise, the calculation is your usual pythagoras. For each row:

          xdelta = rowx - x
          ydelta = rowy - y
          zdelta = rowz - z

          distance = sqrt(xdelta*xdelta + ydelta*ydelta + zdelta*zdelta
        """
        idx = self.vertexGroupNameToIndex(vertexGroupName)
        vertexCoordinates = self.vertexGroupVertices[idx]

        vertex = numpy.zeros(3)
        vertex[0] = x
        vertex[1] = y
        vertex[2] = z

        # Return array with vertex subtracted from each row
        subtractedArray = vertexCoordinates - vertex

        # Return array with each cell multiplied by itself (ie squared)
        multipliedArray = numpy.multiply(subtractedArray,subtractedArray)

        # Return a one-dimensional array with values of each row summed
        summedArray = multipliedArray.sum(axis=1)

        # Return a one-dimensional array where each cell is the square root of the same cell in the given array
        sqrtArray = numpy.sqrt(summedArray)

        #print(sqrtArray)
        return sqrtArray

    def getVertexAtExactLocation(self, vertexGroupName, x, y, z, maxdelta = 0.0001):
        """
        Return index of a vertex matching these coordinates, if existing. Otherwise None.

        This looks for a match with a maximum of maxdelta fuzz, to account for float values
        """
        idx = self.vertexGroupNameToIndex(vertexGroupName)
        vertexCoordinates = self.vertexGroupVertices[idx]

        xmin = x - maxdelta
        xmax = x + maxdelta

        ymin = y - maxdelta
        ymax = y + maxdelta

        zmin = z - maxdelta
        zmax = z + maxdelta

        vidx = 0
        for vert in vertexCoordinates:
            xmatch = False
            ymatch = False
            zmatch = False
            if vert[0] > xmin and vert[0] < xmax:
                xmatch = True
            if vert[1] > ymin and vert[1] < ymax:
                ymatch = True
            if vert[2] > zmin and vert[2] < zmax:
                zmatch = True
            if xmatch and ymatch and zmatch:
                return self.vertexGroupVertexIndexMap[idx][vidx]
            vidx = vidx + 1
        return None

    def findClosestThreeVertices(self, vertexGroupName, x, y, z):
        """
        Return indexes of the three vertices which are the closest to the given coordinate.
        """

        vgidx = self.vertexGroupNameToIndex(vertexGroupName)

        distanceArray = self.getDistanceArray(vertexGroupName, x, y, z)

        # Indexes within vertex group
        localIndexes = [-1, -1, -1]

        # Indexes within mesh
        globalIndexes = [-1, -1, -1]

        # This syntax is exceptionally strange, but it's supposed to look like this.
        # Basically, "find all indexes of the minimum value in distanceArray"
        minidxs = numpy.where(distanceArray == numpy.amin(distanceArray))
        firstMin = minidxs[0][0]
        localIndexes[0] = firstMin

        # We then overwrite the found value so that the next time we repeat the
        # same thing, we'll find the next smallest
        distanceArray[firstMin] = 1000.0

        minidxs = numpy.where(distanceArray == numpy.amin(distanceArray))
        firstMin = minidxs[0][0]
        localIndexes[1] = firstMin
        distanceArray[firstMin] = 1000.0

        minidxs = numpy.where(distanceArray == numpy.amin(distanceArray))
        firstMin = minidxs[0][0]
        localIndexes[2] = firstMin
        distanceArray[firstMin] = 1000.0

        #print("The three smallest distances have the local indices: " + str(localIndexes))

        globalIndexes[0] = self.vertexGroupVertexIndexMap[vgidx][localIndexes[0]]
        globalIndexes[1] = self.vertexGroupVertexIndexMap[vgidx][localIndexes[1]]
        globalIndexes[2] = self.vertexGroupVertexIndexMap[vgidx][localIndexes[2]]

        #print("The three smallest distances have the global indices: " + str(globalIndexes))

        return globalIndexes

