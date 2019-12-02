#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
import os
from ..sanitychecks import checkSanityHuman, checkSanityClothes
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

        #
        # set mode to object, especially if you are still in edit mode
        # (otherwise last changes are not used, even assigned groups will not work)
        # since blender could be in multi-editmode we have to do that on both
        # objects, before we do transformation, otherwise transformation is
        # in wrong context
        #
        # apply all transformations on both objects, otherwise it is too hard
        # to determine problems.
        #
        bpy.ops.object.select_all(action='DESELECT')

        if(humanObj.select_get() is False):
            humanObj.select_set(True)

        context.view_layer.objects.active = humanObj
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


        bpy.ops.object.select_all(action='DESELECT')
        if(clothesObj.select_get() is False):
            clothesObj.select_set(True)

        context.view_layer.objects.active = clothesObj
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        (b, info, error) = checkSanityClothes(clothesObj, humanObj)
        if b:
            bpy.ops.info.infobox('INVOKE_DEFAULT', title="Check Clothes", info=info, error=error)
            return {'FINISHED'}

        subdir = context.scene.MHClothesDestination
        rootDir = getClothesRoot(subdir)
        name = clothesObj.MhClothesName
        desc = clothesObj.MhClothesDesc
        license = context.scene.MhClothesLicense
        author =  context.scene.MhClothesAuthor

        mc = MakeClothes(clothesObj, humanObj, exportName=name, exportRoot=rootDir, license=license, author=author, description=desc, context=context)
        (b, hint) = mc.make()
        if b is False:
            self.report({'ERROR'}, hint)
        else:
            self.report({'INFO'}, "Clothes were written to " + os.path.join(rootDir,name))
        return {'FINISHED'}

