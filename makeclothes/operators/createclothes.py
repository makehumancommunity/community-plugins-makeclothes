#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy, bmesh
from ..sanitychecks import *
from ..mhmesh import MHMesh

class MHC_OT_CreateClothesOperator(bpy.types.Operator):
    """Produce MHCLO file and MHMAT, copy textures"""
    bl_idname = "makeclothes.create_clothes"
    bl_label = "Create clothes"
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

        clothesObj = context.active_object

        if not checkHasAnyVGroups(clothesObj):
            self.report({'ERROR'}, "This object does not have any vertex group. It has to have at least one for MakeClothes to work.")
            return {'FINISHED'}

        if not checkAllVerticesBelongToAVGroup(clothesObj):
            self.report({'ERROR'}, "This object has vertices which do not belong to a vertex group.")
            return {'FINISHED'}

        if not checkAllVerticesBelongToAtMostOneVGroup(clothesObj):
            self.report({'ERROR'}, "This object has vertices which belong to multiple vertex groups")
            return {'FINISHED'}

        if not checkVertexGroupAssignmentsAreNotCorrupt(clothesObj):
            self.report({'ERROR'}, "This object has vertices which belong non-existing vertex groups, see console for more info")
            return {'FINISHED'}

        if not checkFacesHaveAtMostFourVertices(clothesObj):
            self.report({'ERROR'}, "This object has at least one face with more than four vertices. N-gons are not supported by MakeClothes.")
            return {'FINISHED'}

        if not checkFacesHaveTheSameNumberOfVertices(clothesObj):
            self.report({'ERROR'}, "This object has faces with different numbers of vertices. Tris *or* quads are supported, but not a mix of the two.")
            return {'FINISHED'}

        clothesmesh = MHMesh(clothesObj)

        self.report({'INFO'}, "Created clothes")
        return {'FINISHED'}
