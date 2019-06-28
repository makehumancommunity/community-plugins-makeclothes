#!/usr/bin/python
# -*- coding: utf-8 -*-


### --- VERTEX GROUP CHECKS --- ###

def checkHasAnyVGroups(obj):
    return len(obj.vertex_groups) > 0

def checkAllVerticesBelongToAVGroup(obj):
    for vert in obj.data.vertices:
        if len(vert.groups) < 1:
            return False
    return True

def checkAllVerticesBelongToAtMostOneVGroup(obj):
    for vert in obj.data.vertices:
        if len(vert.groups) > 1:
            print("Vertex with index " + str(vert.index) + " belongs to the following groups:")
            for group in vert.groups:
                print(group)
            return False
    return True

def checkVertexGroupAssignmentsAreNotCorrupt(obj):
    validIndices = []
    for vg in obj.vertex_groups:
        validIndices.append(vg.index)
    for vert in obj.data.vertices:
        for group in vert.groups.keys():
            if not int(group) in validIndices:
                print("Vertex with index " + str(vert.index) + " is assigned to a vertex group with index " + str(vert.groups[group]) + ", but that group does not exist")
                return False
    return True

