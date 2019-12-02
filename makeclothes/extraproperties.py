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

    # read the tag froms a json file to keep then flexible
    #
    tagfile = os.path.join(os.path.dirname(__file__), "data", "tags.json")
    cfile = open (tagfile, "r")
    tags = json.load(cfile)
    cfile.close()

    mh_sel = {}
    tag_groups = ["gender", "dresscode", "activity", "period", "type"]
    for group in tag_groups:
        mh_tags[group] = []

        groupitems = tags[group]
        cnt = 1
        for item in groupitems:
            com = "generic tag " + item             # preset for comment
            if "com" in  groupitems[item]:          # normal comment is read from file
                com = groupitems[item]["com"]
            disp = item
            if "text" in  groupitems[item]:         # in case we use an alternative text to show the item
                disp =  groupitems[item]["text"]
            if "sel" in  groupitems[item]:          # this one should be preselected
                mh_sel[group] =  item
            mh_tags[group].append((item, disp, com, cnt))   # create entry
            cnt += 1

    bpy.types.Scene.MHTags_gender = bpy.props.EnumProperty(items=mh_tags["gender"], name="Gender", description=_tagsDescription, default=mh_sel["gender"])
    bpy.types.Scene.MHTags_dresscode = bpy.props.EnumProperty(items=mh_tags["dresscode"], name="Dress code", description=_tagsDescription, default=mh_sel["dresscode"])
    bpy.types.Scene.MHTags_activity = bpy.props.EnumProperty(items=mh_tags["activity"], name="Activity", description=_tagsDescription, default=mh_sel["activity"])
    bpy.types.Scene.MHTags_period = bpy.props.EnumProperty(items=mh_tags["period"], name="Period", description=_tagsDescription, default=mh_sel["period"])
    bpy.types.Scene.MHTags_type = bpy.props.EnumProperty(items=mh_tags["type"], name="Clothes type", description=_tagsDescription, default=mh_sel["type"])
    bpy.types.Scene.MHAdditionalTags = bpy.props.StringProperty(name="Additional tags", description=_tagsDescriptionAdd, default="")
    bpy.types.Scene.MHClothesDestination = bpy.props.EnumProperty(items=_destination, name="Clothes destination", description=_destination_description, default="clothes")

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


