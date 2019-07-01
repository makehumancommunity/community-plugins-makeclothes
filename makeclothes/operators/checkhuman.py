#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy, bmesh
from ..sanitychecks import *

class MHC_OT_CheckHumanOperator(bpy.types.Operator):
    """Extract one helper vertex group as clothes"""
    bl_idname = "makeclothes.check_human"
    bl_label = "Check human"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(self, context):
        return True

    def execute(self, context):

        humanObj = None

        for obj in context.scene.objects:
            if hasattr(obj, "MhObjectType"):
                if obj.MhObjectType == "Basemesh":
                    if humanObj is None:
                        humanObj = obj
                    else:
                        self.report({'ERROR'}, "There are multiple human objects in this scene. To avoid errors, only use one.")
                        return {'FINISHED'}

        if humanObj is None:
            self.report({'ERROR'}, "Could not find any human object in this scene.")
            return {'FINISHED'}

        if not checkHasAnyVGroups(humanObj):
            self.report({'ERROR'}, "The human object does not have any vertex group. It has to have at least one for MakeClothes to work.")
            return {'FINISHED'}

        if not checkVertexGroupAssignmentsAreNotCorrupt(humanObj):
            self.report({'ERROR'}, "The human object has vertices which belong non-existing vertex groups, see console for more info")
            return {'FINISHED'}

        # Todo: warn if there is no delete group

        self.report({'INFO'}, "Seems OK")
        return {'FINISHED'}
