#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Author: Joel Palmius

from .extractclothes import MHC_OT_ExtractClothesOperator
from .markasclothes import MHC_OT_MarkAsClothesOperator
from .markashuman import MHC_OT_MarkAsHumanOperator
from .checkclothes import MHC_OT_CheckClothesOperator
from .createclothes import MHC_OT_CreateClothesOperator
from .checkhuman import MHC_OT_CheckHumanOperator

OPERATOR_CLASSES = [
    MHC_OT_ExtractClothesOperator,
    MHC_OT_MarkAsClothesOperator,
    MHC_OT_MarkAsHumanOperator,
    MHC_OT_CheckClothesOperator,
    MHC_OT_CreateClothesOperator,
    MHC_OT_CheckHumanOperator
]

__all__ = [
    "MHC_OT_ExtractClothesOperator",
    "MHC_OT_MarkAsClothesOperator",
    "MHC_OT_MarkAsHumanOperator",
    "MHC_OT_CheckClothesOperator",
    "MHC_OT_CreateClothesOperator",
    "MHC_OT_CheckHumanOperator",
    "OPERATOR_CLASSES"
]
