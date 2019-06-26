#!/usr/bin/python
# -*- coding: utf-8 -*-

class MHVGroup:

    name: "VGroup"
    index: 0
    vertices: []

    def __init__(self, name, index):
        self.name = name
        self.index = index

    def addVertex(self, vertex, alsoAddGroupToVertex=True):
        if alsoAddGroupToVertex:
            vertex.addVGroup(self)
        if not vertex in self.vertices:
            self.vertices.append(vertex)

    def __str__(self):
        return "VGROUP(" + self.name + ":" + str(self.index) + ")"
