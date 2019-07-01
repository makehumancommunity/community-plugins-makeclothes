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

    def execute(self, context):
        context.active_object.MhObjectType = "Basemesh"
        self.report({'INFO'}, "Object marked as human")
        return {'FINISHED'}
