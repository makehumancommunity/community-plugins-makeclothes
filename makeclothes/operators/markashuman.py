#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy

def getMeshType(humanObj):
    for group in humanObj.vertex_groups:
        if group.name.startswith('_mesh_'):
            return group.name[6:]
    if hasattr(humanObj, "MhMeshType") and humanObj.MhMeshType != "":
        return humanObj.MhMeshType
    return "hm08"

#
# we need this when we import a human mesh, it will be marked automatically
#
def markAsHuman(context):

    #
    # unmark existent mesh if not the same (it helps when you work with
    # a lot of assets and accidentally mark an object as a human
    #
    unmarked = ""
    for obj in context.scene.objects:
        if obj != context.active_object and hasattr(obj, "MhObjectType"):
            if obj.MhObjectType == "Basemesh":
                unmarked += obj.name + " "
                obj.MhObjectType = "Clothes"

    context.active_object.MhObjectType = "Basemesh"
    context.active_object.MhMeshType = getMeshType(context.active_object)
    if unmarked != "":
        text = "Marks change to clothes for: " + unmarked + ". Selected object marked as human, mesh type is " + context.active_object.MhMeshType
    else:
        text = "Selected object marked as human, mesh type is " + context.active_object.MhMeshType
    return (text)

class MHC_OT_MarkAsHumanOperator(bpy.types.Operator):
    """Mark this object to be used as human basemesh"""
    bl_idname = "makeclothes.mark_as_human"
    bl_label = "Mark selected object as human"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        return context.active_object is not None and context.active_object.type == 'MESH'

    def getMeshType(self, humanObj):
        for group in humanObj.vertex_groups:
            if group.name.startswith('_mesh_'):
                return group.name[6:]
        return "hm08"

    def execute(self, context):
        text = markAsHuman(context)
        self.report({'INFO'}, text)
        return {'FINISHED'}
