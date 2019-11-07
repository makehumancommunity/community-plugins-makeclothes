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
        # set mode to object, especially if you are still in edit mode
        # (otherwise last changes are not used
        bpy.ops.object.mode_set(mode='OBJECT')

        (b, info, error) = checkSanityHuman(context)
        bpy.ops.info.infobox('INVOKE_DEFAULT', title="Check Human", info=info, error=error)
        return {'FINISHED'}
