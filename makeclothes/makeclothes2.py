#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Author: Joel Palmius

import bpy

class MHC_PT_MakeClothesPanel(bpy.types.Panel):
    bl_label = "MakeClothes2"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MakeClothes2"

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        extractBox = layout.box()
        extractBox.label(text="Extract clothes", icon="MESH_DATA")

        extractBox.label(text="Vertex group:")
        extractBox.prop(scn, 'MhExtractClothes', text="")
        extractBox.operator("makeclothes.extract_clothes", text="Extract clothes")
        #createBox.operator("mh_community.load_primary_target", text="Load target")

