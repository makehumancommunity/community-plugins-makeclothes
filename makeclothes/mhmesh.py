#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy, pprint, mathutils

class MHMesh:

    def __init__(self, obj, context=None, allow_modifiers=False):
        """
        Parse the mesh into a set of numpy arrays, separated per vertex group.

        There are two dicts here, where each item is an array.

        vertexGroupVertices: The vertex coordinates for each vertex in the group

        vertexGroupNames: A mapping between each vertex groups's index and its name
        """

        self.obj = obj
        self.data = obj.data

        if context and allow_modifiers:
            dg = context.evaluated_depsgraph_get()
            obj2 = context.object.evaluated_get(dg)
            mesh = obj2.to_mesh(preserve_all_data_layers=True, depsgraph=dg)
            self.data = mesh

        self.vertexGroupVertices = dict()
        self.vertexGroupNames = dict()
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

        for vertex in self.data.vertices:
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
        for polygon in self.data.polygons:
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
            self.vertexGroupVertices[groupIndex] = self._seedGroups[groupIndex]

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
                tmp_varray = []
                groupIndex = group.index
                for vertex in self.data.vertices:
                        for vgroup in vertex.groups:
                            if groupIndex == vgroup.group:
                                tmp_varray.append(vertex)

                size = len(tmp_varray)

                #
                # in case of a rigid group
                #
                if size == 3:
                    return (size, tmp_varray)

                # in case we have elements create the kd-tree and balance it
                #
                if size > 0:
                    kd = mathutils.kdtree.KDTree(size)
                    for vertex in tmp_varray:
                        kd.insert(vertex.co, vertex.index)
                    kd.balance()
                    return (size, kd)

        return (0, None)

    # 
    # generates special indices to speed up searches and also used for UV-mapping
    # these indices are only needed for clothes and so it is not part of the init itself
    #
    def getAdditionalIndices(self):
        mesh = self.data

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
        mesh = self.data
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
                            break
                    if found is True:
                        break
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
        verts = self.data.vertices

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

