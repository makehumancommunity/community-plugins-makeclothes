#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Author: Joel Palmius

import bpy
import json
import os
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, CollectionProperty, FloatProperty

_licenses = []
_licenses.append(("CC0",   "CC0", "Creative Commons Zero",                                                  1))
_licenses.append(("CC-BY", "CC-BY", "Creative Commons Attribution",                                           2))
_licenses.append(("AGPL",  "AGPL", "Affero Gnu Public License (don't use unless absolutely necessary)",     3))
_licenseDescription = "Set an output license for the clothes. This will have no practical effect apart from being included in the written MHCLO file."

_tagsDescription = "Select Tags for MakeHuman"
_tagsDescriptionAdd = "Enter Tags for MakeHuman, separate by comma"

_nameDescription = "This is the base name of all files and directories written. A directory with the name will be created, and in it files with will be named with the name plus .mhclo, .mhmat and .obj."
_descDescription = "This is the description of the clothes. It has no function outside being included as a comment in the produced .mhclo file."

_destination = []
_destination.append(("clothes", "clothes", "Clothes subdir", 1))
_destination.append(("hair", "hair", "Hair subdir", 2))
_destination.append(("teeth", "teeth", "Teeth subdir", 3))
_destination.append(("eyebrows", "eyebrows", "Eyebrows subdir", 4))
_destination.append(("eyelashes", "eyelashes", "Eyelashes subdir", 5))
_destination.append(("tongue", "tongue", "Tongue subdir", 6))
# TODO: Maybe we should cover topologies too? Would need other file ext though
_destination_description = "This is the subdirectory (under data) where we should put the produced clothes"

mh_tags = {}

def extraProperties():
    #
    # properties used by all clothes are added to the scene
    #
    bpy.types.Scene.MhClothesLicense = bpy.props.EnumProperty(items=_licenses, name="clothes_license", description=_licenseDescription, default="CC0")
    bpy.types.Scene.MhClothesAuthor  = StringProperty(name="Author name", description="", default="unknown")

    # read the tag from a json file to keep things flexible
    #
    tagfile = os.path.join(os.path.dirname(__file__), "data", "tags.json")
    with open(tagfile, "r") as cfile: # the recommended way, in case something goes wrong
        tags = json.load(cfile)

    mh_sel = {}

    #tag groups can be loaded from the json file, for the sake of flexibility (see above...)

    for group, gr_values in tags.items():
        mh_tags[group] = []
        for cnt, (name, value) in enumerate(gr_values.items(), start=1):
            com = value.get('com', 'generic tag ' + name)             # preset for comment
            disp = value.get('text', name)
            if value.get('sel', False): # this one should be preselected
                mh_sel[group] = name
            mh_tags[group].append((name, disp, com, cnt)) # create entry
        setattr(bpy.types.Scene, 'MHTags_'+ group.lower(), EnumProperty(items=mh_tags[group], name=group.capitalize(),
                                                            description=_tagsDescription, default=mh_sel[group]))

    bpy.types.Scene.MHAdditionalTags = bpy.props.StringProperty(name="Additional tags", description=_tagsDescriptionAdd, default="")
    bpy.types.Scene.MHClothesDestination = bpy.props.EnumProperty(items=_destination, name="Clothes destination", description=_destination_description, default="clothes")

    bpy.types.Scene.MhMcMakeSkin = BoolProperty(name="Use makeskin", description="Use MakeSkin (if available) for writing material. This will be silently ignored if MakeSkin is not installed. For this to work you should have created the object's material using MakeSkin.", default=False)

    # Object properties, normally set by MPFB
    if not hasattr(bpy.types.Object, "MhObjectType"):
        bpy.types.Object.MhObjectType = StringProperty(name="Object type", description="This is what type of MakeHuman object is (such as Clothes, Eyes...)", default="")
    if not hasattr(bpy.types.Object, "MhClothesName"):
        bpy.types.Object.MhClothesName = StringProperty(name="Cloth name", description="Name of the piece of cloth. Also used to create the filename", default="newcloth")
    if not hasattr(bpy.types.Object, "MhClothesDesc"):
        bpy.types.Object.MhClothesDesc = StringProperty(name="Description", description="", default="no description")
    if not hasattr(bpy.types.Object, "MhClothesTags"):
        bpy.types.Object.MhClothesTags = StringProperty(name="Tags connected to the object", description="comma-separated list of tags", default = "")
    if not hasattr(bpy.types.Object, "MhOffsetScale"):
        bpy.types.Object.MhOffsetScale = StringProperty(name="OffSet Scale", description="Name of body part, where clothes are scaled to", default = "Torso")
    if not hasattr(bpy.types.Object, "MhDeleteGroup"):
        bpy.types.Object.MhDeleteGroup = StringProperty(name="Delete Group",
                description="The group contains the vertices to be deleted on the human which are hidden by your piece of cloth", default="Delete")
    if not hasattr(bpy.types.Object, "MhZDepth"):
        bpy.types.Object.MhZDepth = IntProperty(name="Z-Depth", description="", default=50)
    if not hasattr(bpy.types.Object, "MhMeshType"):
        bpy.types.Object.MhMeshType  = StringProperty(name="Mesh type", description="will contain future types, currently hm08", default="hm08")
    if not hasattr(bpy.types.Object, "MhHuman"):
        bpy.types.Object.MhHuman = BoolProperty(name="Is MH Human", description="Old makeclothes property for deciding object type", default=False)


