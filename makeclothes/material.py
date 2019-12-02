#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
import bpy.types
import os
from bpy.types import ShaderNodeBsdfPrincipled, ShaderNodeTexImage

class MHMaterial:

    def __init__(self, obj = None):
        self.diffuseColor = [0.5, 0.5, 0.5] # R, G, B
        self.specularColor = [0.5, 0.5, 0.5]  # R, G, B
        self.shininess = 0.5
        self.opacity = 1.0

        self.nodes = None

        self._blenderMaterial = None
        self._principledNode = None

        self.diffuseTexture = None

        if not obj is None:
            if len(obj.data.materials) > 0:
                # Only take first material into account
                self._blenderMaterial = obj.data.materials[0]

                if not hasattr(self._blenderMaterial, "node_tree") or not hasattr(self._blenderMaterial.node_tree, "nodes"):
                    # TODO: We have a old blender-internal material without nodes. Should write a separate routine for this.
                    pass
                else:
                    # We have a cycles/eevee material, or a blender-internal material with nodes
                    self._parseNodeTree(self._blenderMaterial.node_tree)

    def _parseNodeTree(self, nodes):
        self.nodes = nodes

        # Assume there is a principled node to which everything else
        # is connected. So find that first
        for node in nodes.nodes:
            if isinstance(node,ShaderNodeBsdfPrincipled):
                self._parsePrincipled(node)

        self._findDiffuseTexture()

    def _parsePrincipled(self, principled):
        self._principledNode = principled
        self.diffuseColor = principled.inputs["Base Color"].default_value
        self.shininess = 1.0 - principled.inputs["Roughness"].default_value

    def _findDiffuseTexture(self):
        if not self._principledNode:
            return
        for link in self.nodes.links:
            if link.to_node == self._principledNode:
                tsock = link.to_socket
                if tsock.name == "Base Color":
                    fnode = link.from_node
                    if isinstance(fnode, ShaderNodeTexImage):
                        if fnode.image:
                            if fnode.image.filepath or fnode.image.filepath_raw:
                                if fnode.image.filepath:
                                    self.diffuseTexture = fnode.image.filepath
                                else:
                                    self.diffuseTexture = fnode.image.filepath_raw
                            else:
                                print("Found image texture with an image property, but the image had an empty file path. Giving up on finding a diffuse texture.")
                                return
                        else:
                            print("Found an image texture, but its image property was empty. Giving up on finding a diffuse texture.")
                            return
                    else:
                        print("The principled node had a link to its Base Color input, but the source was not an image texture. Giving up on finding a diffuse texture.")
                        return
        if self.diffuseTexture:
            self.diffuseTexture = bpy.path.abspath(self.diffuseTexture)
            print("Found a diffuse texture: " + self.diffuseTexture)
        else:
            print("There was no diffuse texture to be found")
            
    def __str__(self):
        mat = ""
        mat = mat + "// Color shading attributes\n"
        mat = mat + "diffuseColor  %.4f %.4f %.4f\n" % (self.diffuseColor[0], self.diffuseColor[1], self.diffuseColor[2])
        s = self.shininess
        mat = mat + "specularColor  %.4f %.4f %.4f\n" % (s, s, s) # I don't know how to represent this in a principled node
        mat = mat + "shininess %.4f\n" % s
        mat = mat + "opacity 1\n\n"

        mat = mat + "// Textures\n\n"

        if self.diffuseTexture:
            bn = os.path.basename(self.diffuseTexture)
            mat = mat + "diffuseTexture " + bn + "\n"

        mat = mat + "// Settings\n\n"
        mat = mat + "transparent False\n"
        mat = mat + "alphaToCoverage True\n"
        mat = mat + "backfaceCull False\n"
        mat = mat + "depthless False\n"

        return mat

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