#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Author: Joel Palmius

import bpy
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, CollectionProperty, FloatProperty

_extractGroup = []
_extractGroup.append(("BODY", "Body", "Create clothes from body",                      1))
_extractGroup.append(("SKIRT", "Skirt", "Create clothes from skirt",                   2))
_extractGroup.append(("TIGHTS", "Tights", "Create clothes from tights",                3))
_extractGroup.append(("EYES", "Eyes", "Create clothes from eyes",                      4))
_extractGroup.append(("HAIR", "Hair", "Create clothes from hair",                      5))
_extractGroup.append(("EYELASHES", "Eyelashes", "Create clothes from eyelashes",       6))
_extractGroup.append(("TEETH", "Teeth", "Create clothes from teeth",                   7))
_extractGroup.append(("TONGUE", "Tongue", "Create clothes from tongue",                8))
_extractGroup.append(("GENITALS", "Genitals", "Create clothes from genitals",          9))
_extractGroup.append(("HELPERS", "Helpers", "Entire helper geometry",                 10))
_extractGroupDescription = "You can create a new mesh based on a vertex group in an imported human. Note that this is only possible if you imported with \"detailed helpers\". Without that, the only group possible to extract will be \"body\" and \"helpers\"."

_licenses = []
_licenses.append(("CC0",   "CC0", "Creative Commons Zero",                                                  1))
_licenses.append(("CC-BY", "CC-BY", "Creative Commons Attribution",                                           2))
_licenses.append(("AGPL",  "AGPL", "Affero Gnu Public License (don't use unless absolutely necessary)",     3))
_licenseDescription = "Set an output license for the clothes. This will have no practical effect apart from being included in the written MHCLO file."

_nameDescription = "This is the base name of all files and directories written. A directory with the name will be created, and in it files with will be named with the name plus .mhclo, .mhmat and .obj."
_descDescription = "This is the description of the clothes. It has no function outside being included as a comment in the produced .mhclo file."

def extraProperties():
    #
    # properties used by all clothes are added to the scene
    #
    bpy.types.Scene.MhExtractClothes = bpy.props.EnumProperty(items=_extractGroup, name="extract_clothes", description=_extractGroupDescription, default="BODY")
    bpy.types.Scene.MhClothesLicense = bpy.props.EnumProperty(items=_licenses, name="clothes_license", description=_licenseDescription, default="CC0")
    bpy.types.Scene.MhClothesAuthor  = StringProperty(name="Author name", description="", default="unknown")

    # Object properties, normally set by MPFB
    if not hasattr(bpy.types.Object, "MhObjectType"):
        bpy.types.Object.MhObjectType = StringProperty(name="Object type", description="This is what type of MakeHuman object is (such as Clothes, Eyes...)", default="")
    if not hasattr(bpy.types.Object, "MhClothesName"):
        bpy.types.Object.MhClothesName = StringProperty(name="Cloth name", description="Name of the piece of cloth. Also used to create the filename", default="newcloth")
    if not hasattr(bpy.types.Object, "MhClothesDesc"):
        bpy.types.Object.MhClothesDesc = StringProperty(name="Description", description="", default="no description")
    if not hasattr(bpy.types.Object, "MhDeleteGroup"):
        bpy.types.Object.MhDeleteGroup = StringProperty(name="Delete Group",
                description="The group contains the vertices to be deleted on the human which are hidden by your piece of cloth", default="Delete")
    if not hasattr(bpy.types.Object, "MhZDepth"):
        bpy.types.Object.MhZDepth = IntProperty(name="Z-Depth", description="", default=50)
    if not hasattr(bpy.types.Object, "MhHuman"):
        bpy.types.Object.MhHuman = BoolProperty(name="Is MH Human", description="Old makeclothes property for deciding object type", default=False)

