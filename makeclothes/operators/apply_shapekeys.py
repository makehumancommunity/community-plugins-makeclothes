#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
import os

class MHC_OT_ApplyShapeKeysOperator(bpy.types.Operator):
    """Apply shapekeys"""
    bl_idname = "makeclothes.apply_shapekeys"
    bl_label = "Apply targets"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(self, context):
        if context.active_object is not None:
            if not hasattr(context.active_object, "MhObjectType"):
                return False
            if context.active_object.select_get():
                if context.active_object.MhObjectType == "Basemesh":
                    if context.active_object.data.shape_keys is not None:
                        return True
        return False

    def execute(self, context):

        humanObj = context.active_object

        humanObj.shape_key_add(name=str(humanObj.active_shape_key.name)+"_applied", from_mix=True)
        n = len (humanObj.data.shape_keys.key_blocks)
        humanObj.active_shape_key_index = 0
        for i in range(0, n):
            bpy.ops.object.shape_key_remove(all=False)

        return {'FINISHED'}

