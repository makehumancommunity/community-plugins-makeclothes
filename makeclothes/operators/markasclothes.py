#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy

class MHC_OT_MarkAsClothesOperator(bpy.types.Operator):
    """Extract one helper vertex group as clothes"""
    bl_idname = "makeclothes.mark_as_clothes"
    bl_label = "Mark selected object as clothes"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        return context.active_object is not None

    def execute(self, context):
        context.active_object.MhObjectType = "Clothes"
        self.report({'INFO'}, "Object marked as clothes")
        return {'FINISHED'}
