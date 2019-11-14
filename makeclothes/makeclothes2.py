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
        obj = context.active_object

        setupBox = layout.box()
        setupBox.label(text="Setup clothes mesh", icon="MESH_DATA")
        setupBox.operator("makeclothes.mark_as_clothes", text="Mark as clothes")

        setupBox.label(text="Vertex group as clothes:")
        setupBox.prop(scn, 'MhExtractClothes', text="")
        setupBox.operator("makeclothes.extract_clothes", text="Extract clothes")

        humanBox = layout.box()
        humanBox.label(text="Human", icon="MESH_DATA")
        humanBox.operator("makeclothes.mark_as_human", text="Mark as human")
        humanBox.operator("makeclothes.check_human", text="Check human")

        checkBox = layout.box()
        checkBox.label(text="Check clothes", icon="MESH_DATA")
        checkBox.operator("makeclothes.check_clothes", text="Check clothes")

        commonSettingsBox = layout.box()
        commonSettingsBox.label(text="Common settings", icon="PRESET")
        col = commonSettingsBox.column()
        row = col.row()
        row.label(text="License")
        row.prop(scn, 'MhClothesLicense', text="")
        row = col.row()
        row.label(text="Author")
        row.prop(scn, 'MhClothesAuthor', text="")

        produceBox = layout.box()
        produceBox.label(text="Produce clothes", icon="MESH_DATA")
        if obj is None or obj.type != "MESH":
            produceBox.label(text="- select a visible mesh object -")
        else:
            if obj.MhObjectType == "Basemesh":
                produceBox.label(text="Selected mesh is marked as human")
            else:
                produceBox.label(text="Name")
                produceBox.prop(obj, 'MhClothesName', text="")
                produceBox.label(text="Description")
                produceBox.prop(obj, 'MhClothesDesc', text="")
                produceBox.operator("makeclothes.tag_selector", text="Edit tags")
                col = produceBox.column()
                row = col.row()
                row.label(text="Z-Depth")
                row.prop(obj, 'MhZDepth', text="")
                produceBox.label(text="Delete-Group on Base-Mesh")
                produceBox.prop(obj, 'MhDeleteGroup', text="")
                produceBox.operator("makeclothes.create_clothes", text="Make clothes")
