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

def checkAllVGroupsInFirstExistsInSecond(firstObj, secondObj):
    firstObjVGroups = []
    secondObjVGroups = []

    for vg in firstObj.vertex_groups:
        firstObjVGroups.append(vg.name)

    for vg in secondObj.vertex_groups:
        secondObjVGroups.append(vg.name)

    for name in firstObjVGroups:
        if not name in secondObjVGroups:
            print("The " + name + " group is missing")
            return False

    return True

### --- FACE CHECKS --- ###

# if vertices belong to no faces at all it will also not work
#
def checkStrayVertices(obj):
    verts = obj.data.vertices
    facesfound = {}
    for v in verts:
        facesfound[v.index] = False
    for faces in obj.data.polygons:
        for vn in faces.vertices:
            facesfound[vn] = True
    info = ""
    b = True
    cnt = 0
    for v in verts:
        if not facesfound[v.index]:
            b = False
            cnt += 1
            if cnt < 10:
                info += " " + str(v.index)
    if info != "":
        info = "Stray verts:" + info
    return (b, cnt, info);

def checkFacesHaveAtMostFourVertices(obj):
    for polygon in obj.data.polygons:
        verts_in_face = polygon.vertices[:]
        if len(verts_in_face) > 4:
            return False
    return True

def checkFacesHaveTheSameNumberOfVertices(obj):
    countToLookFor = None
    for polygon in obj.data.polygons:
        verts_in_face = polygon.vertices[:]
        if countToLookFor is None:
            countToLookFor = len(verts_in_face)
        else:
            if len(verts_in_face) != countToLookFor:
                return False
    return True

### --- UV MAP CHECKS --- ###

def checkNumberOfUVMaps(obj):
    uvlayers = obj.data.uv_layers
    cnt = 0
    if uvlayers:
        for (index,layer) in enumerate(uvlayers.keys()):
            cnt += 1
    if cnt == 0:
        return (False, cnt, "No texture possible.")
    elif cnt == 1:
        return (True, cnt, "")
    else:
        return (False, cnt, "Active map is: " + uvlayers.active.name)

