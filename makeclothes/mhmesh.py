#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy

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

        if len(obj.vertex_groups) < 1:
            raise ValueError("This object has no vertex groups. Refusing to continue.")

        for group in obj.vertex_groups:
            if not group.name in self.vertexGroupNames:
                self.vertexGroupNames[int(group.index)] = group.name

        for vertex in obj.data.vertices:
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

        for groupIndex in self._seedGroups.keys():
            seed = self._seedGroups[groupIndex]
            vertexArray = numpy.zeros((len(seed), 3))
            indexArray = numpy.zeros(len(seed), dtype="i4")
            i = 0;
            for vert in seed:
                vertexArray[i][0] = vert[1] # x
                vertexArray[i][1] = vert[2] # y
                vertexArray[i][2] = vert[3] # z

                # The vertex's index in the entire mesh. When there are several vertex groups, this will be
                # different from the index in the vertex group's array
                indexArray[i] = vert[0]

                i = i + 1

            self.vertexGroupVertexIndexMap[groupIndex] = indexArray
            self.vertexGroupVertices[groupIndex] = vertexArray


    def getDistanceArray(self, vertexCoordinates, x, y, z):
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
