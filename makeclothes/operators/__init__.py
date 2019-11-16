#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Author: Joel Palmius

from .extractclothes import MHC_OT_ExtractClothesOperator
from .markasclothes import MHC_OT_MarkAsClothesOperator
from .markashuman import MHC_OT_MarkAsHumanOperator
from .importhuman import MHC_OT_ImportHumanOperator
from .checkclothes import MHC_OT_CheckClothesOperator
from .createclothes import MHC_OT_CreateClothesOperator
from .checkhuman import MHC_OT_CheckHumanOperator
from .tagselector import MHC_OT_TagSelector

OPERATOR_CLASSES = [
    MHC_OT_ExtractClothesOperator,
    MHC_OT_MarkAsClothesOperator,
    MHC_OT_MarkAsHumanOperator,
    MHC_OT_ImportHumanOperator,
    MHC_OT_CheckClothesOperator,
    MHC_OT_CreateClothesOperator,
    MHC_OT_CheckHumanOperator,
    MHC_OT_TagSelector
]

__all__ = [
    "MHC_OT_ExtractClothesOperator",
    "MHC_OT_MarkAsClothesOperator",
    "MHC_OT_MarkAsHumanOperator",
    "MHC_OT_ImportHumanOperator",
    "MHC_OT_CheckClothesOperator",
    "MHC_OT_CreateClothesOperator",
    "MHC_OT_CheckHumanOperator",
    "MHC_OT_TagSelector",
    "OPERATOR_CLASSES"
]
