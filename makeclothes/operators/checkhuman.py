#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from ..sanitychecks import checkSanityHuman

class MHC_OT_CheckHumanOperator(bpy.types.Operator):
    """Check human object if it is usable for makeclothes"""
    bl_idname = "makeclothes.check_human"
    bl_label = "Check human"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(self, context):
        if context.active_object is not None:
            if not hasattr(context.active_object, "MhObjectType"):
                return False
            if context.active_object.select_get():
                if context.active_object.MhObjectType == "Basemesh":
                    return True
        return False

    def execute(self, context):
        # set mode to object, especially if you are still in edit mode
        # (otherwise last changes are not used
        bpy.ops.object.mode_set(mode='OBJECT')

        (b, info, error) = checkSanityHuman(context)
        bpy.ops.info.infobox('INVOKE_DEFAULT', title="Check Human", info=info, error=error)
        return {'FINISHED'}
