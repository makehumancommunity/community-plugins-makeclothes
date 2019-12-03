#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy

def _deleteHelpers(obj):
    #
    # delete all vertices not in body group
    # this only works, because body is first part of the mesh
    #
    if not "body" in obj.vertex_groups:
        return (False, "Cannot delete helpers, no vertext-group 'body' available")

    groupIndex = obj.vertex_groups["body"].index
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    mesh = obj.data
    for vert in mesh.vertices:
        s = True
        for vgroup in vert.groups:
            if groupIndex == vgroup.group:
                s = False
        if s:
            vert.select = True
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.object.mode_set(mode = 'OBJECT')
    #
    # delete empty groups
    #
    for vg in obj.vertex_groups:
        mtvg = not any(vg.index in [g.group for g in v.groups] for v in mesh.vertices)
        if mtvg:
            obj.vertex_groups.remove(vg)
    return (True, "")


class MHC_OT_DeleteHelper(bpy.types.Operator):
    """Delete all vertices not belonging to a body vertex group to work on a mesh without helper"""
    bl_idname = "makeclothes.delete_helper"
    bl_label = "Delete all helpers on the basemesh"
    bl_options = {'REGISTER', 'UNDO'}

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
        print ("Pressed: delete helper")
        (b, error) = _deleteHelpers(context.active_object)
        if b:
            self.report({'INFO'}, "All vertices not belonging to vertex-group 'body' deleted.")
        else:
            self.report({'ERROR'}, error)
        return {'FINISHED'}
