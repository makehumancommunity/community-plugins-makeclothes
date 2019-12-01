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
            vgroup_names = {vgroup.index: vgroup.name for vgroup in obj.vertex_groups}
            hint = "Vertex with index " + str(vert.index) + " belongs to the following groups:\n"
            grps = ""
            for group in vert.groups:
                if len(grps) > 0:
                    grps += ", "
                grps += vgroup_names[group.group]
            return (False, hint + grps)
    return (True, "")

def checkVertexGroupAssignmentsAreNotCorrupt(obj):
    validIndices = []
    for vg in obj.vertex_groups:
        validIndices.append(vg.index)
    for vert in obj.data.vertices:
        for group in vert.groups.keys():
            if not int(group) in validIndices:
                hint = "Vertex with index " + str(vert.index) + " is assigned to a vertex group with index " + \
                    str(vert.groups[group]) + ",\nbut that group does not exist\n"
                return (False, hint)
    return (True, "")

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
    return (b, cnt, info)

def checkNumberOfPoles(obj, max_def):
    verts = obj.data.vertices
    edges = obj.data.edges
    vertEdges = [0 for d in range(len( obj.data.vertices))]
    maxpole = 0
    info = ""
    cnt = 0

    for edge in edges:
        for vertex in edge.vertices:
            vertEdges[vertex] += 1
            if vertEdges[vertex] > max_def:
                maxpole = vertEdges[vertex]             # highest number
                if vertEdges[vertex] == (max_def + 1):  # but only count them once
                    cnt += 1
                    if cnt < 10:
                        info += " " + str(vertex)
    print (maxpole)
    if info != "":
        info = "Max-Pole is " + str(maxpole) + ". Vertices:" + info
    return (maxpole <= max_def, cnt, info)
    

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

def checkSanityClothes(obj, humanobj=None):
    errortext = ""
    info  = ""
    max_def_poles = 8
    errorcnt = 0

    icon = "\001"
    (b, cnt, hint) = checkStrayVertices(obj)
    if not b:
        icon = "\002"
        errortext += "Object has " + str(cnt) + " stray vertices.\n" + hint
        errorcnt += 1
    info += icon + "No stray vertices.\n"

    icon = "\001"
    (b, cnt, hint) = checkNumberOfPoles(obj, max_def_poles)
    if not b:
        icon = "\003"
        errortext += "Object has " + str(cnt) + " vertices with more than " + str(max_def_poles) + " edges attached (poles).\n" + hint
    info += icon + "Number of poles <= " + str(max_def_poles) + ".\n"

    icon = "\001"
    suppress = 0
    if not checkFacesHaveAtMostFourVertices(obj):
        errortext += "This object has at least one face with more than four vertices.\nN-gons are not supported by MakeClothes.\n"
        errorcnt += 1
        icon = "\002"
        suppress = 1
    info += icon + "Faces do not have more than 4 vertices.\n"

    # in case that we have somewhere more than 4 vertices, second test will normally also fail
    #
    if suppress == 0:
        icon = "\001"
        if not checkFacesHaveTheSameNumberOfVertices(obj):
            errortext += "This object has faces with different numbers of vertices.\nTris *or* quads are supported, but not a mix of the two.\n"
            errorcnt += 1
            icon = "\002"
        info += icon + "Faces are either tris or quads.\n"

    icon = "\001"
    if not checkHasAnyVGroups(obj):
        errortext += "This object does not have any vertex group.\nIt has to have at least one for MakeClothes to work.\n"
        errorcnt += 1
        icon = "\002"
    info += icon + "At least one vertex group must exist.\n"

    icon = "\001"
    if not checkAllVerticesBelongToAVGroup(obj):
        errortext += "This object has vertices which do not belong to a vertex group.\n"
        errorcnt += 1
        icon = "\002"
    info += icon + "All vertices belong to a vertex group.\n"

    icon = "\001"
    (b, hint) = checkAllVerticesBelongToAtMostOneVGroup(obj)
    if not b:
        errortext += "This object has vertices which belong to multiple vertex groups.\n" + hint
        errorcnt += 1
        icon = "\002"
    info += icon + "No vertex belongs to multiple groups.\n"

    icon = "\001"
    (b, hint) = checkVertexGroupAssignmentsAreNotCorrupt(obj)
    if not b:
        errortext += "This object has vertices which belong non-existing vertex groups,\n" + hint
        icon = "\002"
    info += icon + "No vertex is assigned to a non existing group.\n"

    if humanobj is not None:
        icon = "\001"
        (b, hint) = checkAllVGroupsInFirstExistsInSecond(obj, humanobj)
        if not b:
            errorcnt += 1
            errortext += "This object has vertex groups which are missing on human,\nThese groups are:\n" + hint
            icon = "\002"
        info += icon + "All vertex groups exist on human.\n"

    icon = "\001"
    (b, cnt, hint) = checkNumberOfUVMaps(obj)
    if not b:
        icon = "\003"
        info += icon + "Object has " + str(cnt) + " UV-maps. " + hint +"\n"

    return (errorcnt > 0, info, errortext)
