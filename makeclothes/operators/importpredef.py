#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
import os
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from .markashuman import markAsHuman
from ..extraproperties import copyNewBase

class MHC_OT_Predefined(bpy.types.Operator):
    """load predefined meshes from blend-file"""
    bl_idname = "makeclothes.importpredef"
    bl_label = "Import predefined human"
    bl_options = {'REGISTER'}
    @classmethod
    def poll(cls, context):
        return (context.scene.MH_predefinedMeshes != "---")

    def execute(self, context):
        oldnames = []
        for obj in context.scene.objects:
            oldnames.append (obj.name)
        (filepath, obj) = os.path.split(context.scene.MH_predefinedMeshes)
        print("append " + filepath + '/Object/' + obj)
        bpy.ops.wm.append(directory=filepath + '/Object/', link=False, autoselect=True, filename=obj)

        #
        # get all objects and figure out the new mesh, set this to human and set scale
        # to decimeter
        #
        newObj = None
        for obj in context.scene.objects:
            if obj.name not in oldnames:
                newObj = obj
                break

        if newObj is not None:
            context.view_layer.objects.active = newObj
            text = markAsHuman(context)
            if hasattr(bpy.context.scene, "MhScaleMode"):
                bpy.context.scene.MhScaleMode = "DECIMETER"
            self.report({'INFO'}, text)
        return {'FINISHED'}

class MHC_OT_NewBase(bpy.types.Operator, ImportHelper):
    """Import a new base"""
    bl_idname = "makeclothes.importnewbase"
    bl_label = "New base blend file"
    bl_options = {'REGISTER'}
    filename_ext = ".blend"

    filter_glob: StringProperty(
            default="*.blend",
            options={'HIDDEN'},
    )
    
    @classmethod
    def poll(self, context):
        return True

    
    def execute(self, context):
        # copy stuff
        okay, text = copyNewBase(self, context, self.filepath)
        if not okay:
            self.report({'ERROR'}, text)
        else:
            self.report({'INFO'}, text)
        return {'FINISHED'}
   
