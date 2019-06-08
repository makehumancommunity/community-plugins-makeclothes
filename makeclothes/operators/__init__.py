#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Author: Joel Palmius

from .extractclothes import MHC_OT_ExtractClothesOperator

OPERATOR_CLASSES = [
    MHC_OT_ExtractClothesOperator
]

__all__ = [
    "MHC_OT_ExtractClothesOperator",
    "OPERATOR_CLASSES"
]
