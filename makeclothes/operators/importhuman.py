#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from mathutils import Matrix
from bpy_extras.io_utils import axis_conversion, ImportHelper
from bpy.props import StringProperty
from io_scene_obj import import_obj

class MHC_OT_ImportHumanOperator(bpy.types.Operator, ImportHelper):
    """Import a basemesh used for human"""
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
        global_matrix = (Matrix.Scale(1.0, 4) @
                axis_conversion(from_forward='-Y',to_forward='-Z', from_up='Z', to_up='-Y',).to_4x4())
        return import_obj.load(context, self.properties.filepath, use_split_objects=False, use_groups_as_vgroups=True, global_matrix=global_matrix)
