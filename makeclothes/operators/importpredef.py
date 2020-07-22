#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
import os
from .markashuman import markAsHuman

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
        # get all objects and figure out the new mesh
        #
        newObj = None
        for obj in context.scene.objects:
            if obj.name not in oldnames:
                newObj = obj
                break

        if newObj is not None:
            context.view_layer.objects.active = newObj
            text = markAsHuman(context)
            self.report({'INFO'}, text)
        return {'FINISHED'}

