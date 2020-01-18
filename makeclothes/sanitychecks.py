#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy

### --- VERTEX GROUP CHECKS --- ###

def checkHasAnyVGroups(obj):
    return len(obj.vertex_groups) > 0

# check if all vertices belong to a vertex group
# markmesh will select the vertices without groups

def checkAllVerticesBelongToAVGroup(obj, markmesh=False):
    b = True
    hint = ""

    for vert in obj.data.vertices:
        if len(vert.groups) < 1:
            b = False
            if markmesh is True:
                vert.select = True

    if b is False and markmesh is True:
            hint = "Change to edit mode and assign selected vertices to a vertex group\n"
    return (b, hint)

# check if vertices belong to more than one group
# markmesh will select the vertices with more then one group

def checkAllVerticesBelongToAtMostOneVGroup(obj, markmesh=False):
    b = True
    hint = ""

    for vert in obj.data.vertices:
        if len(vert.groups) > 1:
            b = False
            if markmesh is True:
                vert.select = True

    if b is False and markmesh is True:
            hint = "Change to edit mode and remove all groups from selected vertices,\nthen assign them to only one group\n"
    return (b, hint)

# check if group assignments are correct
# markmesh will select bad assigned vertices

def checkVertexGroupAssignmentsAreNotCorrupt(obj, markmesh=False):
    validIndices = []
    for vg in obj.vertex_groups:
        validIndices.append(vg.index)
    b = True
    hint = ""
    for vert in obj.data.vertices:
        for group in vert.groups.keys():
            if not int(group) in validIndices:
                b = False
                if markmesh is True:
                    vert.select = True

    if b is False and markmesh is True:
            hint = "Change to edit mode and re-assign selected vertices\n"
    return (b, hint)

def checkAllVGroupsInFirstExistsInSecond(firstObj, secondObj):
    firstObjVGroups = []
    secondObjVGroups = []

    for vg in firstObj.vertex_groups:
        firstObjVGroups.append(vg.name)

    for vg in secondObj.vertex_groups:
        secondObjVGroups.append(vg.name)

    hint = ""
    b = True
    for name in firstObjVGroups:
        if not name in secondObjVGroups:
            hint += name + "\n" # do all to create a list
            b = False

    return (b, hint)

### --- FACE CHECKS --- ###

# if vertices belong to no faces at all it will also not work
# markmesh will select stray vertices
#
def checkStrayVertices(obj, markmesh=False):
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
            if markmesh:
                v.select = True
            b = False
            cnt += 1
    if b is False and markmesh is True:
        info = "Change to edit mode and delete selected vertices.\n"
    return (b, cnt, info)

def checkNumberOfPoles(obj, max_def, markmesh=False):
    verts = obj.data.vertices
    edges = obj.data.edges
    vertEdges = [0] * len( obj.data.vertices)
    maxpole = 0
    info = ""
    cnt = 0

    for edge in edges:
        for vertex in edge.vertices:
            vertEdges[vertex] += 1
            if vertEdges[vertex] > max_def:
                maxpole = vertEdges[vertex]             # highest number
                if vertEdges[vertex] == (max_def + 1):  # but only count them once
                    if markmesh is True:
                        verts[vertex].select = True
                    cnt += 1
    if cnt > 1:
        info = "Max-Pole is " + str(maxpole) + ".\n"
        if markmesh is True:
            info += "To change this, switch to edit mode, these vertices are selected.\n"

    return (maxpole <= max_def, cnt, info)

# test if a face has more than 4 vertices
# markmesh will select the polygons

def checkFacesHaveAtMostFourVertices(obj, markmesh=False):
    b = True
    info = ""

    for polygon in obj.data.polygons:
        if len(polygon.vertices) > 4:
            b = False
            if markmesh is True:
                polygon.select = True

    if b is False and markmesh is True:
        info = "Change to edit mode and modify selected faces.\n"

    return (b, info)

# test if the faces have the same number of vertices, either 3 or 4
# markmesh will select the polygons which are less used in case of error

def checkTriOrQuad(obj, markmesh):
    cntarr = [0] *5

    for polygon in obj.data.polygons:
        l = len(polygon.vertices)
        if l < 5:
            cntarr[l] += 1

    if cntarr[3] == 0:
        return (True, "quad mesh")
    if cntarr[4] == 0:
        return (True, "triangle mesh")

    disp = 4
    mesh = "triangle"
    wrong= "quads"
    if cntarr[4] > cntarr[3]:
        disp = 3
        mesh = "quad"
        wrong = "triangles"

    info = "Mesh seems to be a " + mesh + " mesh. But some faces are " + wrong + ".\n"

    if markmesh is True:
        info += "Change to edit mode and modify selected faces.\n"
        for polygon in obj.data.polygons:
            if len(polygon.vertices) == disp:
                polygon.select = True

    return (False, info)

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

# checkSanityHuman
# do all tests on a human basemesh

def checkSanityHuman(context):
    errortext = ""
    info  = ""

    humanObj = None
    cnt = 0
    for obj in context.scene.objects:
        if hasattr(obj, "MhObjectType"):
            if obj.MhObjectType == "Basemesh":
                cnt += 1
                if humanObj is None:
                    humanObj = obj

    icon = "\001"
    if cnt == 0:
        errortext += "Could not find any human object in this scene.\n"
        icon = "\002"
    elif cnt > 1:
        icon = "\002"
        errortext += "There are multiple human objects in this scene.\nTo avoid errors, only use one.\n"
    info += icon + "Number of human objects is exactly 1 in the scene.\n"

    if cnt == 0:    # we have to return, without a human at all no further checks possible
        return (1, info, errortext)

    icon = "\001"   # now we try the test on the first object
    if not checkHasAnyVGroups(humanObj):
        errortext += "The human object does not have any vertex group.\nIt has to have at least one for MakeClothes to work.\n"
        icon = "\002"
    info += icon + "At least one vertex group is available.\n"

    icon = "\001"
    (b, hint) = checkVertexGroupAssignmentsAreNotCorrupt(humanObj)
    if not b:
        errortext += "The human object has vertices which belong non-existing\n" + hint
        icon = "\002"
    info += icon + "No vertex belongs to a non-existing group.\n"
    return (len(errortext) > 0, info, errortext)



# checkSanityClothes
# do all tests on a piece of cloth (called when creating the clothes, but also for a check)
#
# allowed to be called with second argument for checks between two objects
#
# if markmesh is True marking the mesh (selecting the vertices)
# will always be done only for the first occuring problem

def checkSanityClothes(obj, humanobj=None, markmesh=True):
    errortext = ""
    info  = ""
    max_def_poles = 8
    errorcnt = 0

    if markmesh is True:
        bpy.ops.object.mode_set (mode="EDIT")
        bpy.ops.mesh.select_all (action="DESELECT")
        bpy.ops.mesh.select_mode (type="VERT")
        bpy.ops.object.mode_set (mode="OBJECT")

    icon = "\001"
    (b, cnt, hint) = checkStrayVertices(obj, markmesh)
    if not b:
        icon = "\002"
        errortext += "Object has " + str(cnt) + " stray vertices.\n" + hint
        errorcnt += 1
        markmesh = False
    info += icon + "No stray vertices.\n"

    icon = "\001"
    suppress = 0
    (b, hint) = checkFacesHaveAtMostFourVertices(obj, markmesh)
    if not b:
        errortext += "This object has at least one face with more than four vertices.\nN-gons are not supported by MakeHuman.\n" + hint
        errorcnt += 1
        markmesh = False
        icon = "\002"
        suppress = 1
    info += icon + "Faces do not have more than 4 vertices.\n"

    # in case that we have somewhere more than 4 vertices, second test will normally also fail
    #
    if suppress == 0:
        icon = "\001"
        (b, hint) = checkTriOrQuad(obj, markmesh)
        if not b:
            errortext += "This object has faces with different numbers of vertices.\nTris *or* quads are supported, but not a mix of the two.\n" + hint
            errorcnt += 1
            markmesh = False
            icon = "\002"
        info += icon + "Object is a " + hint + ".\n"

    icon = "\001"
    if not checkHasAnyVGroups(obj):
        errortext += "This object does not have any vertex group.\nIt has to have at least one for MakeClothes to work.\n"
        errorcnt += 1
        icon = "\002"
    info += icon + "At least one vertex group must exist.\n"

    icon = "\001"
    (b, hint) = checkAllVerticesBelongToAVGroup(obj, markmesh)
    if not b:
        errortext += "This object has vertices which do not belong to a vertex group.\n" + hint
        errorcnt += 1
        markmesh = False
        icon = "\002"
    info += icon + "All vertices belong to a vertex group.\n"

    icon = "\001"
    (b, hint) = checkAllVerticesBelongToAtMostOneVGroup(obj, markmesh)
    if not b:
        errortext += "This object has vertices which belong to multiple vertex groups.\n" + hint
        errorcnt += 1
        markmesh = False
        icon = "\002"
    info += icon + "No vertex belongs to multiple groups.\n"

    icon = "\001"
    (b, hint) = checkVertexGroupAssignmentsAreNotCorrupt(obj, markmesh)
    if not b:
        errortext += "This object has vertices which belong non-existing vertex groups,\n" + hint
        errorcnt += 1
        icon = "\002"
        markmesh = False
    info += icon + "No vertex is assigned to a non existing group.\n"

    if humanobj is not None:
        icon = "\001"
        (b, hint) = checkAllVGroupsInFirstExistsInSecond(obj, humanobj)
        if not b:
            errorcnt += 1
            errortext += "This object has vertex groups which are missing on human,\nThese groups are:\n" + hint
            icon = "\002"
        info += icon + "All vertex groups exist on human.\n"

    # for the last two only issue a warning
    #
    icon = "\001"
    (b, cnt, hint) = checkNumberOfUVMaps(obj)
    if not b:
        icon = "\003"
        info += icon + "Object has " + str(cnt) + " UV-maps. " + hint +"\n"

    icon = "\001"
    (b, cnt, hint) = checkNumberOfPoles(obj, max_def_poles, markmesh)
    if not b:
        icon = "\003"
        errortext += "Object has " + str(cnt) + " vertices with more than " + str(max_def_poles) + " edges attached (poles).\n" + hint
        markmesh = False
    info += icon + "Number of poles <= " + str(max_def_poles) + ".\n"

    return (errorcnt > 0, info, errortext)
