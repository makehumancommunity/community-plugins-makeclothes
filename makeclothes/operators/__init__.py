#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Author: Joel Palmius

from .extractclothes import MHC_OT_ExtractClothesOperator
from .markasclothes import MHC_OT_MarkAsClothesOperator
from .checkvgroups import MHC_OT_CheckVGroupsOperator
from .checkfaces import MHC_OT_CheckFacesOperator

OPERATOR_CLASSES = [
    MHC_OT_ExtractClothesOperator,
    MHC_OT_MarkAsClothesOperator,
    MHC_OT_CheckVGroupsOperator,
    MHC_OT_CheckFacesOperator
]

__all__ = [
    "MHC_OT_ExtractClothesOperator",
    "MHC_OT_MarkAsClothesOperator",
    "MHC_OT_CheckVGroupsOperator",
    "MHC_OT_CheckFacesOperator",
    "OPERATOR_CLASSES"
]
