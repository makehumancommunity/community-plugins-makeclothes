#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from ..sanitychecks import checkSanityClothes

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
        #
        # set mode to object, especially if you are still in edit mode
        # (otherwise last changes are not used
        bpy.ops.object.mode_set(mode='OBJECT')

        (b, info, error) = checkSanityClothes(context.active_object)
        bpy.ops.info.infobox('INVOKE_DEFAULT', title="Check Clothes", info=info, error=error)
        return {'FINISHED'}
