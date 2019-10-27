#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy, bmesh
from ..sanitychecks import *

class MHC_OT_CheckClothesOperator(bpy.types.Operator):
    """Do all checks we need for clothes"""
    bl_idname = "makeclothes.check_clothes"
    bl_label = "Check clothes"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(self, context):
        if context.active_object is not None:
            if not hasattr(context.active_object, "MhObjectType"):
                return False
            if context.active_object.select_get():
                if context.active_object.MhObjectType == "Clothes":
                    return True
        return False

    def execute(self, context):

        obj = context.active_object
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
        info += icon + "At least one vertex groups are exists.\n"

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
            error += "This object has vertices which belong non-existing vertex groups,\n see console for more info\n"
            icon = "\002"
        info += icon + "No vertex is assigned to a non existing group.\n"

        icon = "\001"
        (b, cnt, hint) = checkNumberOfUVMaps(obj)
        if not b:
            icon = "\003"
        info += icon + "Object has " + str(cnt) + " UV-maps. " + hint +"\n"

        bpy.ops.info.infobox('INVOKE_DEFAULT', title="Check Clothes", info=info, error=error)
        return {'FINISHED'}
