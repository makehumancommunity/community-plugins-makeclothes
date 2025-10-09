#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Author: Joel Palmius, black-punkduck

import bpy
import json
import os
from bpy.props import BoolProperty, StringProperty, EnumProperty, IntProperty, CollectionProperty, FloatProperty

_licenses = [("CC0", "CC0", "Creative Commons Zero", 1),
    ("CC-BY", "CC-BY", "Creative Commons Attribution", 2),
    ("AGPL", "AGPL", "Affero Gnu Public License (don't use unless absolutely necessary)", 3)
]
_licenseDescription = "Set an output license for the clothes. This will have no practical effect apart from being included in the written MHCLO file."

_blendDescription = "Select human from blendfile"
_tagsDescription = "Select Tags for MakeHuman"
_tagsDescriptionAdd = "Enter Tags for MakeHuman, separate by comma"

_nameDescription = "This is the base name of all files and directories written. A directory with the name will be created, and in it files with will be named with the name plus .mhclo, .mhmat and .obj."
_descDescription = "This is the description of the clothes. It has no function outside being included as a comment in the produced .mhclo file."

_destination = [ ("clothes", "clothes", "Clothes subdir", 1),
    ("hair", "hair", "Hair subdir", 2),
    ("teeth", "teeth", "Teeth subdir", 3),
    ("eyebrows", "eyebrows", "Eyebrows subdir", 4),
    ("eyelashes", "eyelashes", "Eyelashes subdir", 5),
    ("tongue", "tongue", "Tongue subdir", 6)
]

_textures = [("COPY", "Copy", "Copy without rename", 1),
    ("NORMALIZE", "Normalize", "Copy to a name based on MHMAT filename", 2),
    ("KEEP", "Keep", "Keep the name as it is, no copy of textures", 3)
]

_texturesDescription = "Copy will copy textures to destination folder, keeping the same name. Normalize will copy them and rename the texture files to a standardized format. Keep does no copy."

_litspheres = [("lit_leather", "leather", "Leather litsphere. This is appropriate for all clothes, not only leather.", 1),
    ("lit_standard_skin", "standard skin", "Standard skin litsphere. This is appropriate for all skins.", 2),
    ("lit_african", "african skin", "African skin litsphere", 3),
    ("lit_asian", "asian skin", "Asian skin litsphere", 4),
    ("lit_caucasian", "caucasian skin", "Caucasian skin litsphere", 5),
    ("lit_toon01", "toon", "Toon skin litsphere", 6),
    ("skinmat_eye", "eye", "Eye litsphere", 7),
    ("lit_hair", "hair", "The standard hair litsphere without effects", 8),
    ("lit_matte", "matte", "A litsphere to create a mat finish e.g. for a suit", 9),
    ("lit_refl_sharp", "sharp reflection", "A litsphere designed to simulate reflection on dark leather (shoes)", 10),
    ("lit_refl_sharp_aniso", "sharp anisotropic reflection", "A anisotropic litsphere with a mat finish", 11),
    ("lit_refl_sharp_aniso_hard", "dark hair anisotropic reflection", "A sharp anisotropic litsphere, typically used for dark hair", 12),
    ("lit_refl_sharp_aniso_hard_blonde", "blonde anisotropic reflection", "A sharp anisotropic litsphere, typically used for blonde hair", 13)
]
_litsphereDescription = "A litsphere texture is used for emulate lighting and reflections inside MakeHuman. It thus has no effect outside MakeHuman. For any clothing (not just leather), you will want to use the \"leather\" litsphere."

_shaders = [("pbr", "PBR", "Shader uses physical based rendering", 1),
    ("phong", "PHONG", "Shader uses phong algorithm", 2),
    ("litsphere", "LITSPHERE", "Shader uses a litsphere for light", 3),
    ("toon", "TOON", "Shader uses a special toon effect", 4)
]
_shaderDescription = "Shadertype to be used in MakeHuman. It thus has no effect outside MakeHuman."

_destination_description = "This is the subdirectory (under data) where we should put the produced clothes"
_datafolder_description = "Add an alternative folder to write files, if none was given."

mh_tags = {}
mh_readitem = []

def enumlist_meshes(self, context):
    """Populate Mesh list"""
    scene = context.scene
    #
    # do that once, otherwise we will read this file again and again!
    # 
    global mh_readitem

    if len(mh_readitem) ==  0:
        cnt = 0
        blendpath = os.path.join(os.path.dirname(__file__), "humans")
        if os.path.isdir(blendpath):
            for filename in os.listdir(blendpath):
                if filename.endswith(".blend"):
                    filepath = os.path.join(blendpath, filename)

                    with bpy.data.libraries.load(filepath) as (data_from, data_to):
                        for obj in data_from.objects:
                            if obj.startswith("mh_"):
                                item = filename[:-6] + "-" + obj[3:]
                                load = os.path.join(filepath,obj)
                                mh_readitem.append((load, item, ""))
                                cnt += 1
        if cnt == 0:    # append dummy entry
            mh_readitem.append(("---", "---", ""))
    return mh_readitem

def extraProperties():
    #
    # properties used by all clothes are added to the scene
    #
    bpy.types.Scene.MhClothesLicense = bpy.props.EnumProperty(items=_licenses, name="clothes_license", description=_licenseDescription, default="CC0")
    bpy.types.Scene.MhClothesAuthor  = StringProperty(name="Author name", description="", default="unknown")

    # read the tag from a json file to keep things flexible
    #
    tagfile = os.path.join(os.path.dirname(__file__), "data", "tags.json")
    with open(tagfile, "r") as cfile: # the recommended way, in case something goes wrong
        tags = json.load(cfile)

    mh_sel = {}

    #tag groups can be loaded from the json file, for the sake of flexibility (see above...)

    for group, gr_values in tags.items():
        mh_tags[group] = []
        for cnt, (name, value) in enumerate(gr_values.items(), start=1):
            com = value.get('com', 'generic tag ' + name)             # preset for comment
            disp = value.get('text', name)
            if value.get('sel', False): # this one should be preselected
                mh_sel[group] = name
            mh_tags[group].append((name, disp, com, cnt)) # create entry
        setattr(bpy.types.Scene, 'MHTags_'+ group.lower(), EnumProperty(items=mh_tags[group], name=group.capitalize(),
                                                            description=_tagsDescription, default=mh_sel[group]))

    bpy.types.Scene.MH_predefinedMeshes = bpy.props.EnumProperty(items=enumlist_meshes, name="Human", description=_blendDescription)
    bpy.types.Scene.MHAdditionalTags = bpy.props.StringProperty(name="Additional tags", description=_tagsDescriptionAdd, default="")
    bpy.types.Scene.MHAltPath = bpy.props.StringProperty(name="Alternative data folder", description=_datafolder_description, default="")
    bpy.types.Scene.MHClothesDestination = bpy.props.EnumProperty(items=_destination, name="Clothes destination", description=_destination_description, default="clothes")
    bpy.types.Scene.MHVersion = BoolProperty(name="Use Makehuman version II", description="Must be marked, if you want to create an object for MakeHuman Version II", default=False)
    bpy.types.Scene.MHOverwrite = BoolProperty(name="Overwrite existent geometry", description="Must be marked, if you want to replace old geometry files (.mhclo, .obj)", default=False)
    bpy.types.Scene.MHOverwriteMat = BoolProperty(name="Overwrite existent material", description="Must be marked, if you want to replace old material (.mhmat file)", default=False)
    bpy.types.Scene.MhMsOverwrite = BoolProperty(name="Overwrite existing of blender objects", description="Overwrite existing material in blender", default=False)
    bpy.types.Scene.MHAllowMods = BoolProperty(name="Allow modifiers", description="Must be marked, if modifiers should be taken into account", default=True)
    bpy.types.Scene.MHDebugFile = BoolProperty(name="Save debug file", description="Must be marked, if a debug file should be saved", default=False)

    # Object properties, normally set by MPFB
    if not hasattr(bpy.types.Object, "MhObjectType"):
        bpy.types.Object.MhObjectType = StringProperty(name="Object type", description="This is what type of MakeHuman object is (such as Clothes, Eyes...)", default="")
    if not hasattr(bpy.types.Object, "MhClothesName"):
        bpy.types.Object.MhClothesName = StringProperty(name="Cloth name", description="Name of the piece of cloth. Also used to create the filename", default="newcloth")
    if not hasattr(bpy.types.Object, "MhClothesDesc"):
        bpy.types.Object.MhClothesDesc = StringProperty(name="Description", description="", default="no description")
    if not hasattr(bpy.types.Object, "MhClothesTags"):
        bpy.types.Object.MhClothesTags = StringProperty(name="Tags connected to the object", description="comma-separated list of tags", default = "")
    if not hasattr(bpy.types.Object, "MhOffsetScale"):
        bpy.types.Object.MhOffsetScale = StringProperty(name="OffSet Scale", description="Name of body part, where clothes are scaled to", default = "Torso")
    if not hasattr(bpy.types.Object, "MhDeleteGroup"):
        bpy.types.Object.MhDeleteGroup = StringProperty(name="Delete Group",
                description="The group contains the vertices to be deleted on the human which are hidden by your piece of cloth", default="Delete")
    if not hasattr(bpy.types.Object, "MhZDepth"):
        bpy.types.Object.MhZDepth = IntProperty(name="Z-Depth", description="", default=50)
    if not hasattr(bpy.types.Object, "MhMeshType"):
        bpy.types.Object.MhMeshType  = StringProperty(name="Mesh type", description="will contain future types, currently hm08", default="hm08")

    bpy.types.Scene.MhMsCreateDiffuse = BoolProperty(name="Create diffuse placeholder", description="Create a placeholder for a diffuse texture", default=True)
    bpy.types.Scene.MhMsCreateNormal = BoolProperty(name="Create normal map placeholder", description="Create a placeholder for a normal map", default=False)
    bpy.types.Scene.MhMsCreateRoughMetal = BoolProperty(name="Create roughness/metallic map placeholder", description="Create a placeholder for a roughness/metallic map", default=False)
    bpy.types.Scene.MhMsCreateAOMap = BoolProperty(name="Create ambient occlusion map placeholder", description="Create a placeholder for a ambient occlusion map", default=False)
    bpy.types.Scene.MhMsCreateEmission = BoolProperty(name="Create emission map placeholder", description="Create a placeholder for a emission map", default=False)

    # Metadata keys
    bpy.types.Object.MhMsName = StringProperty(name="Name", description="The name of this material. This name is used for exports e.g. with mhx2.", default="material")
    bpy.types.Object.MhMsTag = StringProperty(name="Tag", description="A category the material fits into, for example \"blond\" or \"female\". This will influence sorting and filtering in MH.", default="")
    bpy.types.Object.MhMsDescription = StringProperty(name="Description", description="A description of the material. It will have little practical effect apart from being written to the mhmat file.", default="")

    # Boolean keys
    bpy.types.Object.MhMsBackfaceCull = BoolProperty(name="Backface culling", description="If the back side of faces with the material should be invisible. This has no effect in exports, but may be important in MH", default=True)
    bpy.types.Object.MhMsAlphaToCoverage = BoolProperty(name="AlphaToCoverage", description="Use A2C hardware acceleration for rendering transparency in this material", default=True)
    bpy.types.Object.MhMsTransparent = BoolProperty(name="Transparent", description="Use transparent, when you expect that your object will be in front of another transparent object. Using the alpha-channel, MakeHuman is internally only able to render one transparent layer. Use this and switch backface culling off, when you create transparent hair.", default=False)
    bpy.types.Object.MhMsUseLit = BoolProperty(name="Use Litsphere", description="Use the litsphere shader when rendering material in MakeHuman. This does not have any effect on materials outside MakeHuman", default=True)

    # Options
    bpy.types.Object.MhMsShader = bpy.props.EnumProperty(items=_shaders, name="Shader", description=_shaderDescription, default="pbr")
    bpy.types.Object.MhMsLitsphere = bpy.props.EnumProperty(items=_litspheres, name="Litsphere", description=_litsphereDescription, default="lit_leather")
    bpy.types.Object.MhMsTextures = bpy.props.EnumProperty(items=_textures, name="Textures", description=_texturesDescription, default="COPY")
