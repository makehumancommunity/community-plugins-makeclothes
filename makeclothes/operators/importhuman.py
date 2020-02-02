#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from ..utils import loadObjFile
from .markashuman import markAsHuman

class MHC_OT_ImportHumanOperator(bpy.types.Operator, ImportHelper):
    """Import a basemesh used for human, make sure mesh is not rotated and face is pointing to front view"""
    bl_idname = "makeclothes.importhuman"
    bl_label = "Import a mesh as human"
    bl_options = {'REGISTER', 'UNDO'}
    filename_ext = ".obj"

    filter_glob: StringProperty(
        default="*.obj",
        options={'HIDDEN'},
    )

    @classmethod
    def poll(self, context):
        for obj in context.scene.objects:
            if hasattr(obj, "MhObjectType"):
                if obj.MhObjectType == "Basemesh":
                    return False
        return True

    def execute(self, context):
        obj = loadObjFile(context, self.properties.filepath)
        if obj is not None:
            text = markAsHuman(context)
            self.report({'INFO'}, text)
        return {'FINISHED'}
