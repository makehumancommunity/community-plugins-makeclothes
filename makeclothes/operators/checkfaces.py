#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy, bmesh
from ..sanitychecks import *

class MHC_OT_CheckFacesOperator(bpy.types.Operator):
    """Extract one helper vertex group as clothes"""
    bl_idname = "makeclothes.check_faces"
    bl_label = "Check faces"
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

        if not checkFacesHaveAtMostFourVertices(obj):
            self.report({'ERROR'}, "This object has at least one face with more than four vertices. N-gons are not supported by MakeClothes.")
            return {'FINISHED'}

        if not checkFacesHaveTheSameNumberOfVertices(obj):
            self.report({'ERROR'}, "This object has faces with different numbers of vertices. Tris *or* quads are supported, but not a mix of the two.")
            return {'FINISHED'}

        self.report({'INFO'}, "Seems OK")
        return {'FINISHED'}
