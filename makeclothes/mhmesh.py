#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy

class MHMesh:

    def __init__(self, obj):

        self.obj = obj
        self.vertexGroupVertices = dict()
        self.vertexGroupNames = dict()

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
                    print("Appending to group " + str(groupIndex) + ": " + str(vertDef))
                    seedGroup.append(vertDef)

        for groupIndex in self._seedGroups.keys():
            seed = self._seedGroups[groupIndex]
            npa = numpy.zeros((len(seed), 3))
            for vert in seed:
                npa[vert[0]][0] = vert[1] # x
                npa[vert[0]][1] = vert[2] # y
                npa[vert[0]][2] = vert[3] # z
            self.vertexGroupVertices[groupIndex] = npa

