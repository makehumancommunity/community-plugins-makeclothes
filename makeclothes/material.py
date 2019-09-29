#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy, bmesh, os
import bpy.types
from bpy.types import ShaderNodeBsdfPrincipled

class MHMaterial:

    def __init__(self, obj = None):
        self.diffuseColor = [0.5, 0.5, 0.5] # R, G, B
        self.specularColor = [0.5, 0.5, 0.5]  # R, G, B
        self.shininess = 0.5
        self.opacity = 1.0

        self._blenderMaterial = None
        self._principledNode = None

        if not obj is None:
            if len(obj.data.materials) > 0:
                # Only take first material into account
                self._blenderMaterial = obj.data.materials[0]
                self._parseNodeTree(self._blenderMaterial.node_tree)

    def _parseNodeTree(self, nodes):
        # Assume there is a principled node to which everything else
        # is connected. So find that first
        for node in nodes.nodes:
            if isinstance(node,ShaderNodeBsdfPrincipled):
                self._parsePrincipled(node)

    def _parsePrincipled(self, principled):
        self._principledNode = principled
        self.diffuseColor = principled.inputs["Base Color"].default_value
        self.shininess = 1.0 - principled.inputs["Roughness"].default_value

# TODO: Manage linked textures etc

"""
<bpy_struct, ShaderNodeBsdfPrincipled("Principled BSDF")>
<bpy_struct, NodeSocketColor("Base Color")>
<bpy_struct, NodeSocketFloatFactor("Subsurface")>
<bpy_struct, NodeSocketVector("Subsurface Radius")>
<bpy_struct, NodeSocketColor("Subsurface Color")>
<bpy_struct, NodeSocketFloatFactor("Metallic")>
<bpy_struct, NodeSocketFloatFactor("Specular")>
<bpy_struct, NodeSocketFloatFactor("Specular Tint")>
<bpy_struct, NodeSocketFloatFactor("Roughness")>
<bpy_struct, NodeSocketFloatFactor("Anisotropic")>
<bpy_struct, NodeSocketFloatFactor("Anisotropic Rotation")>
<bpy_struct, NodeSocketFloatFactor("Sheen")>
<bpy_struct, NodeSocketFloatFactor("Sheen Tint")>
<bpy_struct, NodeSocketFloatFactor("Clearcoat")>
<bpy_struct, NodeSocketFloatFactor("Clearcoat Roughness")>
<bpy_struct, NodeSocketFloat("IOR")>
<bpy_struct, NodeSocketFloatFactor("Transmission")>
<bpy_struct, NodeSocketFloatFactor("Transmission Roughness")>
<bpy_struct, NodeSocketColor("Emission")>
<bpy_struct, NodeSocketFloatFactor("Alpha")>
<bpy_struct, NodeSocketVector("Normal")>
<bpy_struct, NodeSocketVector("Clearcoat Normal")>
<bpy_struct, NodeSocketVector("Tangent")>
"""