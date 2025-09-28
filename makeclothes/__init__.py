#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Authors: Joel Palmius
#           black-punkduck (Maintainer)

#
# must be before(!) all imports
#
bl_info = {
    "name": "MakeClothes",
    "author": "black-punkduck, Joel Palmius",
    "version": (2,3,1),
    "blender": (4,0,0),
    "location": "View3D > Properties > MakeClothes2",
    "description": "Create MakeHuman Clothes",
    'wiki_url': "http://www.makehumancommunity.org/",
    "category": "MakeHuman"}

from bpy.utils import register_class, unregister_class
from .extraproperties import extraProperties
from .makeclothes2 import MHC_PT_MakeClothesPanel
from .infobox import MHC_OT_InfoBox,MHC_OT_WarningBox
from .operators import *

MAKECLOTHES2_CLASSES = []
MAKECLOTHES2_CLASSES.extend(OPERATOR_CLASSES)
MAKECLOTHES2_CLASSES.append(MHC_PT_MakeClothesPanel)
MAKECLOTHES2_CLASSES.append(MHC_OT_InfoBox)
MAKECLOTHES2_CLASSES.append(MHC_OT_WarningBox)

__all__ = [
    "MHC_PT_MakeClothesPanel",
    "MHC_OT_InfoBox",
    "MHC_OT_WarningBox",
    "MAKECLOTHES2_CLASSES"
]

def register():
    extraProperties()
    for cls in MAKECLOTHES2_CLASSES:
        register_class(cls)

def unregister():

    for cls in reversed(MAKECLOTHES2_CLASSES):
        unregister_class(cls)

if __name__ == "__main__":
    register()
    print("MakeClothes2 loaded")

