#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy, bmesh, os
from ..sanitychecks import *
from ..core_makeclothes_functionality import MakeClothes
from ..utils import getClothesRoot

class MHC_OT_CreateClothesOperator(bpy.types.Operator):
    """Produce MHCLO file and MHMAT, copy textures"""
    bl_idname = "makeclothes.create_clothes"
    bl_label = "Create clothes"
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

        humanObj = None

        for obj in context.scene.objects:
            if hasattr(obj, "MhObjectType"):
                if obj.MhObjectType == "Basemesh":
                    if humanObj is None:
                        humanObj = obj
                    else:
                        self.report({'ERROR'}, "There are multiple human objects in this scene. To avoid errors, only use one.")
                        return {'FINISHED'}

        if humanObj is None:
            self.report({'ERROR'}, "Could not find any human object in this scene.")
            return {'FINISHED'}

        if not checkHasAnyVGroups(humanObj):
            self.report({'ERROR'}, "The human object does not have any vertex group. It has to have at least one for MakeClothes to work.")
            return {'FINISHED'}

        if not checkVertexGroupAssignmentsAreNotCorrupt(humanObj):
            self.report({'ERROR'}, "The human object has vertices which belong non-existing vertex groups, see console for more info")
            return {'FINISHED'}

        clothesObj = context.active_object

        if not checkHasAnyVGroups(clothesObj):
            self.report({'ERROR'}, "This object does not have any vertex group. It has to have at least one for MakeClothes to work.")
            return {'FINISHED'}

        if not checkAllVerticesBelongToAVGroup(clothesObj):
            self.report({'ERROR'}, "This object has vertices which do not belong to a vertex group.")
            return {'FINISHED'}

        if not checkAllVerticesBelongToAtMostOneVGroup(clothesObj):
            self.report({'ERROR'}, "This object has vertices which belong to multiple vertex groups")
            return {'FINISHED'}

        if not checkVertexGroupAssignmentsAreNotCorrupt(clothesObj):
            self.report({'ERROR'}, "This object has vertices which belong non-existing vertex groups, see console for more info")
            return {'FINISHED'}

        if not checkFacesHaveAtMostFourVertices(clothesObj):
            self.report({'ERROR'}, "This object has at least one face with more than four vertices. N-gons are not supported by MakeClothes.")
            return {'FINISHED'}

        if not checkFacesHaveTheSameNumberOfVertices(clothesObj):
            self.report({'ERROR'}, "This object has faces with different numbers of vertices. Tris *or* quads are supported, but not a mix of the two.")
            return {'FINISHED'}

        if not checkAllVGroupsInFirstExistsInSecond(clothesObj, humanObj):
            self.report({'ERROR'}, "There are vertex groups in the clothes object which do not exist in the human object. See console for more info.")
            return {'FINISHED'}

        #
        # apply all transformations on both objects, otherwise it is too hard
        # to determine problems.
        #
        context.view_layer.objects.active = humanObj
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        context.view_layer.objects.active = clothesObj
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        rootDir = getClothesRoot()
        name = clothesObj.MhClothesName
        desc = clothesObj.MhClothesDesc
        license = context.scene.MhClothesLicense
        author =  context.scene.MhClothesAuthor

        MakeClothes(clothesObj, humanObj, exportName=name, exportRoot=rootDir, license=license, author=author, description=desc)

        self.report({'INFO'}, "Clothes were written to " + os.path.join(rootDir,name))
        return {'FINISHED'}

