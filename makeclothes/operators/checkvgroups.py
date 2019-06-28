#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy, bmesh
from ..sanitychecks import *

class MHC_OT_CheckVGroupsOperator(bpy.types.Operator):
    """Extract one helper vertex group as clothes"""
    bl_idname = "makeclothes.check_vertex_groups"
    bl_label = "Check vertex groups"
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
        if not checkHasAnyVGroups(obj):
            self.report({'ERROR'}, "This object does not have any vertex group. It has to have at least one for MakeClothes to work.")
            return {'FINISHED'}

        if not checkAllVerticesBelongToAVGroup(obj):
            self.report({'ERROR'}, "This object has vertices which do not belong to a vertex group.")
            return {'FINISHED'}

        if not checkAllVerticesBelongToAtMostOneVGroup(obj):
            self.report({'ERROR'}, "This object has vertices which belong to multiple vertex groups")
            return {'FINISHED'}

        if not checkVertexGroupAssignmentsAreNotCorrupt(obj):
            self.report({'ERROR'}, "This object has vertices which belong non-existing vertex groups, see console for more info")
            return {'FINISHED'}

        self.report({'INFO'}, "Seems OK")
        return {'FINISHED'}
