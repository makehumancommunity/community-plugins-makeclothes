#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Authors: Joel Palmius
#           black-punkduck

from bpy.utils import register_class, unregister_class
from .extraproperties import extraProperties, bl_info
from .makeclothes2 import MHC_PT_MakeClothesPanel
from .infobox import MHC_OT_InfoBox,MHC_WarningBox
from .operators import *

# bl_info is placed in extra-properties to have access from everywhere and to avoid
# ending up with a circular dependency

MAKECLOTHES2_CLASSES = []
MAKECLOTHES2_CLASSES.extend(OPERATOR_CLASSES)
MAKECLOTHES2_CLASSES.append(MHC_PT_MakeClothesPanel)
MAKECLOTHES2_CLASSES.append(MHC_OT_InfoBox)
MAKECLOTHES2_CLASSES.append(MHC_WarningBox)

__all__ = [
    "MHC_PT_MakeClothesPanel",
    "MHC_OT_InfoBox",
    "MHC_WarningBox",
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

