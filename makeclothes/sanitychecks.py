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

# checkSanityHuman
# do all tests on a human basemesh

def checkSanityHuman(context):
    error = ""
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
        error += "Could not find any human object in this scene.\n"
        icon = "\002"
    elif cnt > 1:
        icon = "\002"
        error += "There are multiple human objects in this scene.\nTo avoid errors, only use one.\n"
    info += icon + "Number of human objects is exactly 1 in the scene.\n"

    if cnt == 0:    # we have to return, without a human at all no further checks possible
        return (1, info, error)

    icon = "\001"   # now we try the test on the first object
    if not checkHasAnyVGroups(humanObj):
        error += "The human object does not have any vertex group.\nIt has to have at least one for MakeClothes to work.\n"
        icon = "\002"
    info += icon + "At least one vertex group is available.\n"

    icon = "\001"
    if not checkVertexGroupAssignmentsAreNotCorrupt(humanObj):
        error += "The human object has vertices which belong non-existing\nvertex groups, see console for more info.\n"
        icon = "\002"
    info += icon + "No vertex belongs to a non-existing group.\n"
    return (len(error) > 0, info, error)



# checkSanityClothes
# do all tests on a piece of cloth (called when creating the clothes, but also for a check)

def checkSanityClothes(obj):
    error = ""
    info  = ""

    icon = "\001"
    (b, cnt, hint) = checkStrayVertices(obj)
    if not b:
        icon = "\002"
        error += "Object has " + str(cnt) + " stray vertices.\n" + hint
    info += icon + "No stray vertices.\n"

    icon = "\001"
    suppress = 0
    if not checkFacesHaveAtMostFourVertices(obj):
        error += "This object has at least one face with more than four vertices.\nN-gons are not supported by MakeClothes.\n"
        icon = "\002"
        suppress = 1
    info += icon + "Faces do not have more than 4 vertices.\n"

    # in case that we have somewhere more than 4 vertices, second test will normally also fail
    #
    if suppress == 0:
        icon = "\001"
        if not checkFacesHaveTheSameNumberOfVertices(obj):
            error += "This object has faces with different numbers of vertices.\nTris *or* quads are supported, but not a mix of the two.\n"
            icon = "\002"
        info += icon + "Faces are either tris or quads.\n"

    icon = "\001"
    if not checkHasAnyVGroups(obj):
        error += "This object does not have any vertex group.\nIt has to have at least one for MakeClothes to work.\n"
        icon = "\002"
    info += icon + "At least one vertex group must exist.\n"

    icon = "\001"
    if not checkAllVerticesBelongToAVGroup(obj):
        error += "This object has vertices which do not belong to a vertex group.\n"
        icon = "\002"
    info += icon + "All vertices belong to a vertex group.\n"

    icon = "\001"
    if not checkAllVerticesBelongToAtMostOneVGroup(obj):
        error += "This object has vertices which belong to multiple vertex groups.\n"
        icon = "\002"
    info += icon + "No vertex belongs to multiple groups.\n"

    icon = "\001"
    if not checkVertexGroupAssignmentsAreNotCorrupt(obj):
        error += "This object has vertices which belong non-existing vertex groups,\nsee console for more info\n"
        icon = "\002"
    info += icon + "No vertex is assigned to a non existing group.\n"

    icon = "\001"
    (b, cnt, hint) = checkNumberOfUVMaps(obj)
    if not b:
        icon = "\003"
        info += icon + "Object has " + str(cnt) + " UV-maps. " + hint +"\n"

    return (len(error) > 0, info, error)
