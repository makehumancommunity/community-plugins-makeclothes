#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Author: Joel Palmius

from .extractclothes import MHC_OT_ExtractClothesOperator
from .importmhclo import MHC_OT_ImportClothesOperator
from .markasclothes import MHC_OT_MarkAsClothesOperator
from .markashuman import MHC_OT_MarkAsHumanOperator
from .importhuman import MHC_OT_ImportHumanOperator
from .checkclothes import MHC_OT_CheckClothesOperator
from .createclothes import MHC_OT_CreateClothesOperator
from .checkhuman import MHC_OT_CheckHumanOperator
from .apply_shapekeys import MHC_OT_ApplyShapeKeysOperator
from .deletehelper import MHC_OT_DeleteHelper
from .tagselector import MHC_OT_TagSelector
from .importpredef import MHC_OT_Predefined
from .offsetscaling import MHC_OT_GetOffsetScaling

OPERATOR_CLASSES = [
    MHC_OT_ExtractClothesOperator,
    MHC_OT_ImportClothesOperator,
    MHC_OT_MarkAsClothesOperator,
    MHC_OT_MarkAsHumanOperator,
    MHC_OT_ImportHumanOperator,
    MHC_OT_CheckClothesOperator,
    MHC_OT_CreateClothesOperator,
    MHC_OT_CheckHumanOperator,
    MHC_OT_ApplyShapeKeysOperator,
    MHC_OT_DeleteHelper,
    MHC_OT_TagSelector,
    MHC_OT_Predefined,
    MHC_OT_GetOffsetScaling
]

__all__ = [
    "MHC_OT_ExtractClothesOperator",
    "MHC_OT_ImportClothesOperator",
    "MHC_OT_MarkAsClothesOperator",
    "MHC_OT_MarkAsHumanOperator",
    "MHC_OT_ImportHumanOperator",
    "MHC_OT_CheckClothesOperator",
    "MHC_OT_CreateClothesOperator",
    "MHC_OT_CheckHumanOperator",
    "MHC_OT_ApplyShapeKeysOperator",
    "MHC_OT_DeleteHelper",
    "MHC_OT_TagSelector",
    "MHC_OT_Predefined",
    "MHC_OT_GetOffsetScaling",
    "OPERATOR_CLASSES"
]
