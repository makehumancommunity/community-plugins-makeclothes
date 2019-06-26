#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy, bmesh

class MHC_OT_MarkAsClothesOperator(bpy.types.Operator):
    """Extract one helper vertex group as clothes"""
    bl_idname = "makeclothes.mark_as_clothes"
    bl_label = "Mark selected object as clothes"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        if context.active_object is not None:
            if not hasattr(context.active_object, "MhObjectType"):
                return False
            if context.active_object.select_get():
                if context.active_object.MhObjectType != "Clothes":
                    return True
        return False

    def execute(self, context):
        self.report({'INFO'}, "Object marked as clothes")
        return {'FINISHED'}
