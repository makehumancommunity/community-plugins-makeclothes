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

        (b, info, error) = checkSanityHuman(context)
        if b:
            bpy.ops.info.infobox('INVOKE_DEFAULT', title="Check Human", info=info, error=error)
            return {'FINISHED'}

        # since we tested the existence of a human above there is exactly one
        #
        humanObj = None
        for obj in context.scene.objects:
            if hasattr(obj, "MhObjectType"):
                if obj.MhObjectType == "Basemesh":
                    humanObj = obj
                    break

        clothesObj = context.active_object

        (b, info, error) = checkSanityClothes(clothesObj)
        if b:
            bpy.ops.info.infobox('INVOKE_DEFAULT', title="Check Clothes", info=info, error=error)
            return {'FINISHED'}

        #
        # apply all transformations on both objects, otherwise it is too hard
        # to determine problems.
        #
        context.view_layer.objects.active = humanObj
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
        context.view_layer.objects.active = clothesObj
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        #
        # set mode to object, especially if you are still in edit mode
        # (otherwise last changes are not used
        bpy.ops.object.mode_set(mode='OBJECT')

        rootDir = getClothesRoot()
        name = clothesObj.MhClothesName
        desc = clothesObj.MhClothesDesc
        license = context.scene.MhClothesLicense
        author =  context.scene.MhClothesAuthor

        MakeClothes(clothesObj, humanObj, exportName=name, exportRoot=rootDir, license=license, author=author, description=desc, context=context)

        self.report({'INFO'}, "Clothes were written to " + os.path.join(rootDir,name))
        return {'FINISHED'}

