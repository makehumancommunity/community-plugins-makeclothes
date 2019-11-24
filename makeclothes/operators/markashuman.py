#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy, bmesh

class MHC_OT_MarkAsHumanOperator(bpy.types.Operator):
    """Extract one helper vertex group as clothes"""
    bl_idname = "makeclothes.mark_as_human"
    bl_label = "Mark selected object as human"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        return context.active_object is not None

    def getMeshType(self, humanObj):
        for group in humanObj.vertex_groups:
            if group.name.startswith('_mesh_'):
                return group.name[6:]
        return "hm08"

    def execute(self, context):
        context.active_object.MhObjectType = "Basemesh"
        context.active_object.MhMeshType = self.getMeshType(context.active_object)
        self.report({'INFO'}, "Object marked as human, mesh type is " + context.active_object.MhMeshType)
        return {'FINISHED'}
