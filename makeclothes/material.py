#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
import bpy.types
import os
import shutil
from math import log
from bpy.props import StringProperty
from bpy.types import ShaderNodeBsdfPrincipled
from bpy_extras.io_utils import ImportHelper, ExportHelper
from .keytypes import *
from .extraproperties import _litspheres, _shaders
from .utils import getClothesRoot


def hasMaterial(obj):
    if not obj.material_slots:
        return False
    return len(obj.material_slots) > 0

class MHMat:
    def __init__(self):

        self.MHMAT_KEY_GROUPS = ["Metadata", "Color", "Texture", "Intensity", "Various"]

        self.MHMAT_KEYS = [
            ### METADATA ###
            MHMATStringKey("tag", None, 'Metadata'),
            MHMATStringKey("name", None, 'Metadata'),
            MHMATStringKey("description", None, 'Metadata'),
            MHMATStringKey("license", 'CC0', 'Metadata'),
            MHMATStringKey("author", None, 'Metadata'),
            MHMATStringShaderKey("shaderParam", None, 'Metadata'),

            ### COLORS ###
            MHMATColorKey("diffuseColor", [0.5, 0.5, 0.5], 'Color'),
            MHMATColorKey("emissiveColor", [0.0, 0.0, 0.0], 'Color'),
            MHMATColorKey("ambientColor", None, 'Color'),

            ### TEXTURES ###
            MHMATFileKey("diffuseTexture", None, 'Texture'),
            MHMATFileKey("normalmapTexture", None, 'Texture'),
            MHMATFileKey("metallicRoughnessTexture", None, 'Texture'),
            MHMATFileKey("aomapTexture", None, 'Texture'),
            MHMATFileKey("emissiveTexture", None, 'Texture'),

            ### INTENSITIES ###
            MHMATFloatKey("normalmapIntensity", 1.0, 'Intensity'),
            MHMATFloatKey("metallicFactor", 0.0, 'Intensity'),
            MHMATFloatKey("roughnessFactor", 0.5, 'Intensity'),
            MHMATFloatKey("aomapIntensity", 1.0, 'Intensity'),
            MHMATFloatKey("emissiveFactor", 0.0, 'Intensity'),

            ### VARIOUS ###
            MHMATFileKey("litsphereTexture", "lit_leather", 'Various'),
            MHMATStringKey("shader", "PBR", 'Various'),
            MHMATBooleanKey("transparent", False, 'Various'),
            MHMATBooleanKey("alphaToCoverage", True, 'Various'),
            MHMATBooleanKey("backfaceCull", True, 'Various')
        ]

        self.MHMAT_NAME_TO_KEY = {}
        for keyObj in self.MHMAT_KEYS:
            keyname = keyObj.keyNameLower
            self.MHMAT_NAME_TO_KEY[keyname] = keyObj

        self.MHMAT_SHADER_KEYS = [
            MHMATStringShaderKey("shaderParam litsphereTexture", None, 'Shaders'),
        ]

        self.settings = dict()
        for keyObj in self.MHMAT_KEYS:
            self.settings[keyObj.keyName] = keyObj.defaultValue

    def prepare(self, obj, scn):
        self.diffuse = None
        self.nodes = None
        self.blendmat = None
        self.node_principled = None
        self.litSphere = None

        if obj is not None:
            if isinstance(obj, str):
                self.parseFile(obj)
                scn.MhClothesLicense = self.settings["license"]
            else:
                if len(obj.data.materials) == 0:
                    self.createEmptyMaterial(obj, "genericMaterial")
                    print ("Use a generic empty material")

                # Only take first material into account
                self.blendmat = obj.data.materials[0]

                if not hasattr(self.blendmat, "node_tree") or not hasattr(self.blendmat.node_tree, "nodes"):
                    raise ValueError("Only cycles/eevee materials are supported")
                else:
                    self.nodes = self.blendmat.node_tree.nodes
                    self.links = self.blendmat.node_tree.links

                    for node in self.nodes:
                        if isinstance(node, ShaderNodeBsdfPrincipled):
                            self.node_principled = node

                    if self.node_principled is None:
                        raise ValueError("no principled found")
                    self.parseNodeMaterial()

    def addNode(self, ntype, x, y, name):
        node = self.nodes.new(ntype)
        node.name = name
        node.label = name
        node.location = x,y
        return node

    def createEmptyMaterial(self, obj, name):
        self.blendmat = bpy.data.materials.new(name)
        self.blendmat.use_nodes = True
        self.blendmat.blend_method = 'HASHED'
        obj.data.materials.append(self.blendmat)
        self.nodes = self.blendmat.node_tree.nodes
        self.nodes.clear()
        self.links = self.blendmat.node_tree.links

        # Add the Principled and Output
        self.node_principled = self.addNode('ShaderNodeBsdfPrincipled', -200, 0, "Principled-MainShader")
        self.node_output = self.addNode('ShaderNodeOutputMaterial', 300, -200, "Output")

        # will be overwritten
        self.links.new(self.node_principled.outputs["BSDF"], self.node_output.inputs["Surface"])

    def addTextureNode(self, path, x, y, noncolor, name):
        node = self.nodes.new('ShaderNodeTexImage')
        if path:
            node.image = bpy.data.images.load(path)
            if noncolor:
                node.image.colorspace_settings.name = 'Non-Color'
        node.name = name
        node.label = name
        node.location = x,y
        return node

    def createDiffuseTextureNode(self, imagePathAbsolute=None):
        self.diffuse = self.addTextureNode(imagePathAbsolute, -800, 300, False, "diffuseTexture")
        self.links.new(self.diffuse.outputs["Color"], self.node_principled.inputs['Base Color'])
        self.links.new(self.diffuse.outputs["Alpha"], self.node_principled.inputs["Alpha"])

    def createAOTextureNode(self, imagePathAbsolute=None, newAO=False, ambientcolor=[1.0, 1.0, 1.0], intensity=1.0):

        # a second eevee output node is needed, otherwise cycles will show weird colors,
        # set other node to cycles
        #
        self.node_output_eevee = self.addNode('ShaderNodeOutputMaterial', 300, 0, "OutputEevee")
        self.node_output_eevee.target = "EEVEE"
        self.node_output.target = "CYCLES"

        if ambientcolor is None:
            ambientcolor = [1.0, 1.0, 1.0]

        self.aom = None
        if imagePathAbsolute is not None or newAO is True:
            self.aom = self.addTextureNode(imagePathAbsolute, -800, -600, True, "aomapTexture")
        nsep = self.addNode("ShaderNodeSeparateColor", -400, -600, "AO Separator")
        if len(ambientcolor) < 4:
            ambientcolor.append(1.0)
        nsep.inputs[0].default_value =  ambientcolor

        mixcol = self.addNode("ShaderNodeMixRGB", -200, -600, "AO Mixer")
        mixcol.inputs[0].default_value = intensity

        amboc = self.addNode("ShaderNodeAmbientOcclusion", 0, -600, "AmbientOcclusion")
        mixshader = self.addNode("ShaderNodeMixShader", 100, 0, "MixAO")

        if self.aom is not None:
            self.links.new(self.aom.outputs["Color"], nsep.inputs["Color"])
        self.links.new(nsep.outputs[0], mixcol.inputs[2])
        self.links.new(mixcol.outputs[0], amboc.inputs["Color"])
        self.links.new(amboc.outputs["Color"], mixshader.inputs[0])
        self.links.new(self.node_principled.outputs["BSDF"], mixshader.inputs[2])
        self.links.new(mixshader.outputs[0], self.node_output_eevee.inputs["Surface"])
        self.links.new(self.node_principled.outputs["BSDF"], self.node_output.inputs["Surface"])

    def createEmissiveTextureNode(self, imagePathAbsolute=None, intensity=1.0):
        self.emimission = self.addTextureNode(imagePathAbsolute, -800, -900, True, "emissiveTexture")
        self.links.new(self.emimission.outputs["Color"], self.node_principled.inputs["Emission Color"])
        self.node_principled.inputs["Emission Strength"].default_value = intensity

    def createNormal(self, imagePathAbsolute=None, intensity=1.0):
        self.normal = self.addTextureNode(imagePathAbsolute, -800, -300, True, "normalmapTexture")
        nnode= self.addNode("ShaderNodeNormalMap", -400, -300, "Normalmap")
        nnode.inputs[0].default_value = intensity
        self.links.new(nnode.outputs["Normal"], self.node_principled.inputs["Normal"])
        self.links.new(self.normal.outputs["Color"], nnode.inputs["Color"])

    def createRoughnessTextureNode(self, imagePathAbsolute=None):
        self.metalRoughness = self.addTextureNode(imagePathAbsolute, -800, 0, True, "metallicRoughnessTexture")
        nsep= self.addNode("ShaderNodeSeparateColor", -400, 0, "color Separator")
        self.node_principled.inputs["Metallic"].default_value = 1.0
        self.node_principled.inputs["Roughness"].default_value = 1.0
        self.links.new(self.metalRoughness.outputs["Color"], nsep.inputs['Color'])
        self.links.new(nsep.outputs[2], self.node_principled.inputs["Metallic"])
        self.links.new(nsep.outputs[1], self.node_principled.inputs["Roughness"])

    # create MakeHuman Nodeframe
    def createMHNodeFrame(self, name):
        frame_node = self.nodes.new("NodeFrame")
        frame_node.label = name
        frame_node.name = name
        return frame_node

    # create unlinked value nodes
    #
    def createDummyNode(self, x, y, name, value, parent):
        node = None
        if type(value) is bool:
            node = self.addNode("ShaderNodeValue", x, y, name)
            node.outputs["Value"].default_value = float(value)
            node.parent = parent

        if type(value) is str:
            node = self.addNode("ShaderNodeAttribute", x, y, name)
            node.attribute_name = value
            node.parent = parent

        return node

    def findNodeSocketDefaultValue(self, nodeName, socketName):
        fnode = None
        for node in self.nodes:
            if node.name == nodeName:
                fnode = node
                break
        if not fnode:
            return None
        if not fnode.inputs:
            print("Node of type " + str(type(node)) + " didn't have any inputs!?")
            return None
        if not socketName in fnode.inputs:
            print("Node of type " + str(type(node)) + " didn't have any input called " + socketName)
            return None
        return fnode.inputs[socketName].default_value

    def setPrincipledSocketDefaultValue(self, socketName, socketValue):
        self.node_principled.inputs[socketName].default_value = socketValue

    def getPrincipledSocketDefaultValue(self, socketName):
        return self.node_principled.inputs[socketName].default_value

    # test if a textureNode is well-defined, in case of error, return reason
    #
    def extractImageFilePath(self, nodeName):
        textureNode = None
        for node in self.nodes:
            if node.name == nodeName:
                textureNode = node
                break

        if textureNode is None:
            return (None, None)

        if textureNode.image:
            if textureNode.image.filepath or textureNode.image.filepath_raw:
                if textureNode.image.filepath:
                    path = bpy.path.abspath(textureNode.image.filepath)
                    if os.path.isfile(path):
                        return (path, None)
                    return (None, path + " is not a file")
                else:
                    return (bpy.path.abspath(textureNode.image.filepath_raw), None) #  file test?!
            else:
                return (None, "Found image texture with an image property, but the image had an empty file path.")
        else:
            return (None, "Found an image texture, but its image property is empty.")


    # test for all texture nodes and add an error text to be displayed on blender
    #
    def checkAllTexturesAreSaved(self):
        for ttype, tname in [("Diffuse image", "diffuseTexture"), ("Normal map", "normalmapTexture"),
                ("Metallic-Roughness map", "metallicRoughnessTexture"),
                ("Ambient Occlusion map", "aomapTexture"), ("Emission map", "emissiveTexture")]:
            (name, err) = self.extractImageFilePath(tname)
            if (err):
                return ttype + ": " + err

        return ""

    def parseNodeMaterial(self):

        # Everything else should be from nodes
        sett = self.settings

        for texture in ["diffuseTexture", "metallicRoughnessTexture", "normalmapTexture", "aomapTexture", "emissiveTexture"]:
            sett[texture] = None
            (dtp, err) = self.extractImageFilePath(texture)
            if dtp and str(dtp).strip():
                sett[texture] = str(dtp).strip()

        if sett["normalmapTexture"] is not None:
            sett["normalmapIntensity"] = self.findNodeSocketDefaultValue("Normalmap", "Strength")

        diffuseColor = self.getPrincipledSocketDefaultValue('Base Color')
        sett["diffuseColor"] = [diffuseColor[0], diffuseColor[1], diffuseColor[2]]

        ambientColor = self.findNodeSocketDefaultValue('AO Separator', 'Color')
        if ambientColor:
            sett["ambientColor"] = [ambientColor[0], ambientColor[1], ambientColor[2]]
        else:
            sett["ambientColor"] = [1.0, 1.0, 1.0]


        sett["emissiveColor"] = None
        col = self.getPrincipledSocketDefaultValue("Emission Color")
        if col:
            if col[0] < 0.01 and col[1] < 0.01 and col[2] < 0.01:
                pass # emission is black
            else:
                sett["emissiveColor"] = [col[0], col[1], col[2]]

        if sett["emissiveTexture"] is not None or sett["emissiveColor"] is not None:
            emscale = self.getPrincipledSocketDefaultValue("Emission Strength")
            sett["emissiveFactor"] =  log(emscale + 1, 2) / 8

        sett["roughnessFactor"] = self.getPrincipledSocketDefaultValue('Roughness')
        sett["metallicFactor"] = self.getPrincipledSocketDefaultValue('Metallic')
        if sett["aomapTexture"] is not None:
            sett["aomapIntensity"] = self.findNodeSocketDefaultValue('AO Mixer', 'Fac') * 2.0


    def copyTextures(self, mhmatFilenameAbsolute, normalize=True, adjustSettings=True):
        matBaseName = os.path.basename(mhmatFilenameAbsolute)
        matLoc = os.path.dirname(mhmatFilenameAbsolute)
        (matBase, matExt) = os.path.splitext(matBaseName)

        for keyObj in self.MHMAT_KEYS:
            if isinstance(keyObj, MHMATFileKey) and keyObj.keyName in self.settings and keyObj.keyName != "litsphereTexture":
                key = keyObj.keyName
                origLoc = self.settings[key]
                if origLoc:
                    (dummy, texExt) = os.path.splitext(origLoc)
                    if not normalize:
                        baseName = os.path.basename(origLoc)
                    else:
                        suffix = re.sub(r'Texture','',key)
                        suffix = re.sub(r'map','',suffix)
                        baseName = matBase + '_' + suffix + texExt
                    destLoc = os.path.join(matLoc, baseName)
                    origLoc = os.path.abspath(origLoc)
                    destLoc = os.path.abspath(destLoc)
                    if origLoc != destLoc:
                        print ("copy from " + origLoc  + " to " + destLoc)
                        shutil.copyfile(origLoc, destLoc)
                    else:
                        print("Source and destination is same file, skipping texture copy for this entry")
                    if adjustSettings:
                        self.settings[key] = baseName

    # create a node-setup for a new or loaded material
    # take information from scene and objects
    #
    def assignAsNodesMaterialForObj(self, scn, obj, mode_load=False):
        if obj is None or scn is None:
            return

        sett = self.settings
        diffusePH=False
        normalPH=False
        roughmetalPH=False
        aoPH = False
        emissionPH = False
        name = None

        if mode_load is False:
            diffusePH = scn.MhMsCreateDiffuse
            normalPH = scn.MhMsCreateNormal
            roughmetalPH = scn.MhMsCreateRoughMetal
            aoPH = scn.MhMsCreateAOMap
            emissionPH = scn.MhMsCreateEmission
            name = obj.name
            sett["litsphereTexture"] = obj.MhMsLitsphere
            sett["transparent"] = obj.MhMsTransparent
            sett["alphaToCoverage"] = obj.MhMsAlphaToCoverage
            sett["backfaceCull"] = obj.MhMsBackfaceCull
            sett["shader"] = obj.MhMsShader
        else:
            name = sett["name"]
            obj.MhMsTransparent = sett["transparent"]
            obj.MhMsAlphaToCoverage = sett["alphaToCoverage"]
            obj.MhMsBackfaceCull = sett["backfaceCull"]
            for elem in _litspheres:
                if sett["litsphereTexture"] == elem[0]:
                    obj.MhMsLitsphere = sett["litsphereTexture"]
                    break
            for elem in _shaders:
                if sett["shader"] == elem[0]:
                    obj.MhMsShader = sett["shader"]
                    break

        if not name:   # for the case that MHMAT file did not specify a name
            name = "genericMaterial"

        self.createEmptyMaterial(obj,name)

        # --- set the values in the menu (needed after import)
        #
        obj.MhMsName = self.blendmat.name # using mat.name instead of mat will take the real name like asset.001

        if sett["description"]:
            obj.MhMsDescription = sett["description"]
        if sett["tag"]:
            obj.MhMsTag = sett["tag"]
        if sett["author"]:
            obj.MhClothesAuthor = sett["author"]

        # --- visualization of MakeHuman internals in node-setup
        # create node-frame for MakeHuman additional nodes
        #
        frame = self.createMHNodeFrame ("MakeHuman Internal")

        # now add all internal values to this frame
        #
        y = 50
        for nodename, down in [ ("transparent", 100), ("alphaToCoverage", 100), ("backfaceCull", 100), ("litsphereTexture", 200), ("shader", 200) ]:
            self.createDummyNode(500, y, nodename, sett[nodename], frame)
            y -= down

        if sett["diffuseTexture"] or diffusePH:
            self.createDiffuseTextureNode(sett["diffuseTexture"])

        if sett["roughnessFactor"]:
            self.setPrincipledSocketDefaultValue("Roughness", sett["roughnessFactor"])

        if sett["metallicFactor"]:
            self.setPrincipledSocketDefaultValue("Metallic", sett["metallicFactor"])

        if sett["metallicRoughnessTexture"] or roughmetalPH:
            self.createRoughnessTextureNode(sett["metallicRoughnessTexture"])

        if sett["normalmapTexture"] or normalPH:
            self.createNormal(imagePathAbsolute=sett["normalmapTexture"], intensity=sett["normalmapIntensity"])

        if sett["aomapTexture"] or aoPH or sett["ambientColor"]:
            self.createAOTextureNode(imagePathAbsolute=sett["aomapTexture"], newAO=aoPH, ambientcolor=sett["ambientColor"], intensity=sett["aomapIntensity"] / 2)
        else:
            self.links.new(self.node_principled.outputs["BSDF"], self.node_output.inputs["Surface"])

        if sett["emissiveTexture"] or emissionPH:
            emscale = pow(2, sett["emissiveFactor"] * 8) -1
            self.createEmissiveTextureNode(imagePathAbsolute=sett["emissiveTexture"], intensity=emscale)

        if sett["diffuseColor"] is not None:
            col = sett["diffuseColor"]

            # TODO weird hack to be changed later, but otherwise col grows to infinity when 2nd material is added
            if len(col) < 4:
                col.append(1.0)

            self.setPrincipledSocketDefaultValue("Base Color", col)

        if sett["emissiveColor"] is not None:
            col = sett["emissiveColor"]
            if len(col) < 4:
                col.append(1.0)
            self.setPrincipledSocketDefaultValue("Emission Color", col)

        return self.blendmat


    def writeMHmat(self, scn, obj, fnAbsolute):

        errtext = None

        if obj.MhMsName:
            self.settings['name'] = obj.MhMsName

        if obj.MhMsTag:
            self.settings['tag'] = obj.MhMsTag

        if obj.MhMsDescription:
            self.settings['description'] = obj.MhMsDescription

        if scn.MhClothesAuthor and scn.MhClothesAuthor != "unknown":
            self.settings['author'] = scn.MhClothesAuthor

        self.settings['license'] = scn.MhClothesLicense
        self.settings['shader'] = obj.MhMsShader
        self.settings['backfaceCull'] = obj.MhMsBackfaceCull
        self.settings['alphaToCoverage'] = obj.MhMsAlphaToCoverage
        self.settings['transparent'] = obj.MhMsTransparent
        handling = "COPY"
        if obj.MhMsTextures:
            handling = obj.MhMsTextures
        if handling == "NORMALIZE":
            self.copyTextures(fnAbsolute)
        if handling == "COPY":
            self.copyTextures(fnAbsolute,normalize=False)
        # If handling is KEEP, then paths are already correct

        if obj.MhMsUseLit and obj.MhMsLitsphere:
            self.litSphere = obj.MhMsLitsphere
        with open(fnAbsolute,'w') as f:
            f.write(str(self))

        return (errtext)

    def parseFile(self, fileName):

        full = os.path.abspath(fileName)
        location = os.path.dirname(full)
        with open(fileName, 'r', errors='ignore') as f:
            line = f.readline()
            while line:
                parsedLine = line.strip()
                key = None
                if parsedLine and not parsedLine.startswith("#") and not parsedLine.startswith("/"):
                    match = re.search(r'^([a-zA-Z]+)\s+(.*)$', parsedLine)
                    if match:
                        key = match.group(1)
                        keyLower = key.lower()
                        value = None

                        if keyLower in self.MHMAT_NAME_TO_KEY:
                            keyObj = self.MHMAT_NAME_TO_KEY[keyLower]
                            keyCorrectCase = keyObj.keyName
                            if key != keyCorrectCase:
                                print("Autofixing case: " + key + " -> " + keyCorrectCase)
                                key = keyCorrectCase
                            if isinstance(keyObj, MHMATFileKey):
                                (usedKey, value) = keyObj.parseFile(parsedLine, location)
                            else:
                                (usedKey, value) = keyObj.parse(parsedLine)
                        else:
                            # print("skipped: " + key)
                            key = None

                if key:
                    # handle multiple occurences of tag (create a comma-separated entry)
                    #
                    if key == 'tag':
                        if self.settings[key]:
                            self.settings[key] += ", " + value
                        else:
                            self.settings[key] = value
                    elif key == 'shaderParam':
                        if value[0] == "litsphereTexture":
                            li = value[1][11:] if value[1].startswith("litspheres/") else value[1]
                            match = re.search(r'(.*)\.png$', value[1])
                            if match:
                                self.settings["litsphereTexture"] = match.group(1)
                    else:
                        # print ("set", key)
                        self.settings[key] = value

                line = f.readline()

    def __str__(self):
        mat = "# This is a material file for MakeHuman 2, produced by MakeClothes2\n"

        for keyGroup in self.MHMAT_KEY_GROUPS:
            mat = mat + "\n// " + keyGroup + "\n\n"
            for keyNameLower in self.MHMAT_NAME_TO_KEY.keys():
                keyObj = self.MHMAT_NAME_TO_KEY[keyNameLower]
                keyName = keyObj.keyName
                if keyObj.keyGroup == keyGroup and not self.settings[keyName] is None:
                    if keyName == "tag":
                        for elem in self.settings["tag"].split(","):
                            mat = mat + "tag " + elem.strip() + "\n"
                    elif keyName != "litsphereTexture":
                        mat = mat + keyName + " " + keyObj.asString(self.settings[keyName]) + "\n"

        if self.litSphere:
            mat = mat + "\nshaderParam litsphereTexture " + str(self.litSphere) + ".png\n"

        mat = mat + "\n"

        return mat

class MHC_OT_ImportMaterialOperator(bpy.types.Operator, ImportHelper):
    """Import MHMAT"""
    bl_idname = "makeclothes.import_material"
    bl_label = "Import material"
    bl_options = {'REGISTER','UNDO'}

    filter_glob: StringProperty(default='*.mhmat', options={'HIDDEN'})

    @classmethod
    def poll(self, context):
        if context.active_object is not None:
            if not hasattr(context.active_object, "MhObjectType"):
                return False
            return True
        return False

    def execute(self, context):
        obj = context.active_object
        scn = context.scene

        if hasMaterial(obj):
            if not scn.MhMsOverwrite:
                self.report({'ERROR'}, "A material for this object already exists, change 'replace' option in common settings to overwrite material")
                return {'FINISHED'}
            else:
                while len(obj.data.materials) > 0:
                    obj.data.materials.pop(index=0)

        mhmat = MHMat()
        mhmat.prepare(self.filepath, scn)
        mhmat.assignAsNodesMaterialForObj(scn, obj, True)

        self.report({'INFO'}, "Material imported")
        return {'FINISHED'}

class MHC_OT_CreateMaterialOperator(bpy.types.Operator):
    """Create template material"""
    bl_idname = "makeclothes.create_material"
    bl_label = "Create material"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(self, context):
        if context.active_object is not None:
            if not hasattr(context.active_object, "MhObjectType"):
                return False
            return True
        return False

    def execute(self, context):

        obj = context.active_object
        scn = context.scene

        if hasMaterial(obj):
            if not scn.MhMsOverwrite:
                self.report({'ERROR'}, "A material for this object already exists, change 'replace' option in common settings to overwrite material")
                return {'FINISHED'}
            else:
                while len(obj.data.materials) > 0:
                    obj.data.materials.pop(index=0)

        mhmat = MHMat()
        mhmat.prepare(None, scn)

        # use object name as a first guess, if it already exists, a .001 is automatically appended by new function for material
        #
        mhmat.assignAsNodesMaterialForObj(scn, obj)

        self.report({'INFO'}, "A template material was created")
        return {'FINISHED'}

class MHC_OT_WriteMaterialOperator(bpy.types.Operator, ExportHelper):
    """Write material to MHMAT file"""
    bl_idname = "makeclothes.write_material"
    bl_label = "Write material"
    bl_options = {'REGISTER'}

    filename_ext = '.mhmat'

    filter_glob: StringProperty(default='*.mhmat', options={'HIDDEN'})
    filepath: StringProperty(
            name="File Path",
            description="Filepath used for exporting the file",
            maxlen=1024,
            subtype='FILE_PATH',
            )

    def getHuman(self, context):
        humanObj = None
        for obj in context.scene.objects:
            if hasattr(obj, "MhObjectType"):
                if obj.MhObjectType == "Basemesh":
                    humanObj = obj
                    break
        return humanObj

    @classmethod
    def poll(self, context):
        if context.active_object is not None:
            if not hasattr(context.active_object, "MhObjectType"):
                return False
            return True
        return False

    def invoke(self, context, event):
        #
        # try to find a correct folder
        #
        if not self.filepath:
            blend_filepath = context.active_object.MhMsName;
            if not blend_filepath:
                blend_filepath = "untitled"
            self.filepath = blend_filepath + self.filename_ext

        humanObj = self.getHuman(context)
        subdir = context.scene.MHClothesDestination
        if context.scene.MHAltPath != "":
            rootDir = context.scene.MHAltPath
        else:
            if humanObj is None:
                meshtype = "hm08"
            else:
                meshtype = humanObj.MhMeshType
            rootDir = getClothesRoot(context.scene.MHVersion, meshtype, subdir)

        self.filepath = os.path.join(rootDir, self.filepath)
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        obj = context.active_object
        scn = context.scene

        fnAbsolute = bpy.path.abspath(self.filepath)

        if not hasMaterial(obj):
            self.report({'ERROR'}, "Object does not have a material")
            return {'FINISHED'}

        mhmat = MHMat()
        mhmat.prepare(obj, scn)

        checkImg = mhmat.checkAllTexturesAreSaved()
        if checkImg:
            self.report({'ERROR'}, checkImg)
            return {'FINISHED'}

        errtext = mhmat.writeMHmat(scn, obj, fnAbsolute)
        if errtext:
            self.report({'ERROR'}, errtext)
        else:
            self.report({'INFO'}, "A material file was written")

        return {'FINISHED'}
