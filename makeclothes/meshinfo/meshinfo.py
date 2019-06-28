#!/usr/bin/python
# -*- coding: utf-8 -*-

from .mhvgroup import MHVGroup
from .mhvertex import MHVertex

class MHMeshInfo:

    obj: None
    vgroups: None
    vertices: None

    def __init__(self, obj):
        self.obj = obj
        self.vgroups = dict()
        self.vertices = dict()

        for group in obj.vertex_groups:
            if not group.index in self.vgroups:
                vgroup = MHVGroup(group.name, group.index)
                self.vgroups[int(group.index)] = vgroup

        for vert in obj.data.vertices:
            mhvert = MHVertex(vert.index, vert.co[0], vert.co[1], vert.co[2])

            for group in vert.groups:
                gidx = group.group
                print(gidx)
                if not int(gidx) in self.vgroups:
                    print("Vertex says it has group with index " + str(gidx) + ", but that group does not exist")
                else:
                    mhvgroup = self.vgroups[int(gidx)]
                    mhvgroup.addVertex(mhvert)

            self.vertices[mhvert.index] = mhvert

    def findClosestFour(self, foreignVert):

        if foreignVert is None:
            raise ValueError("Cannot compare None vertex")

        if len(foreignVert.vgroups) != 1:
            print("Found foreign vertex with other than exactly one vgroup:")
            print("  index: " + str(foreignVert.index))
            print("  groups:")
            for grp in foreignVert.vgroups:
                print("    " + grp.name)
            raise ValueError("Foreign vertex needs exactly one vgroup, has " + str(len(foreignVert.vgroups)))

        groupName = foreignVert.vgroups[0].name

        mhvgroup = None

        for grp in self.vgroups:
            if grp.name == groupName:
                mhvgroup = grp

        if mhvgroup is None:
            raise ValueError("This mesh does not have the " + groupName + " vertex group")

        verts = mhvgroup.vertices

        vert0 = verts[0]
        firstDistance = vert0.distance(foreignVert)
        relevantVerts = [ [vert0, firstDistance], [vert0, firstDistance], [vert0, firstDistance], [vert0, firstDistance] ]

        for myVert in verts:
            distance = myVert.distance(foreignVert)
            i = 0
            while i < 4:
                if distance < relevantVerts[i][1]:
                    relevantVerts.insert(i, [myVert, distance])
                    relevantVerts.pop()
                    i = 4
                i = i + 1

        return relevantVerts
