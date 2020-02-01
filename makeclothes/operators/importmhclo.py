#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
import os
from mathutils import Vector
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from ..utils import getClothesRoot, loadObjFile
from ..core_makeclothes_functionality import _loadMeshJson

class import_mhclo:
    def __init__(self):
        self.obj_file = None
        self.xs = None
        self.ys = None
        self.zs = None
        self.author = "unknown"
        self.license = "CC0"
        self.name = "imported_cloth"
        self.description = "no description"
        self.tags = ""
        self.zdepth = 50
        self.first = 0
        self.verts = {}
        self.delverts = []
        self.delete = False
        self.delete_group = "Delete"
        return

    def update(self, human):

        if human is None:
            return

        hverts = human.data.vertices
        hl = len(hverts)        # number of base vertices

        # test if we inside mesh, if not, leave
        #
        if self.xs[0] >= hl or self.xs[1] > hl \
            or self.ys[0] >= hl or self.ys[1] >= hl \
            or self.zs[0] >= hl or self.zs[1] >= hl:
            return

        # get sizes
        #
        s0 = abs(hverts[self.xs[0]].co[0] - hverts[self.xs[1]].co[0]) / self.xs[2]
        s2 = abs(hverts[self.ys[0]].co[2] - hverts[self.ys[1]].co[2]) / self.ys[2]
        s1 = abs(hverts[self.zs[0]].co[1] - hverts[self.zs[1]].co[1]) / self.zs[2]

        dverts = self.clothes.data.vertices

        for n in range(len(dverts)):
            s = self.verts[n]
            (n1, n2, n3) = s["verts"]

            # test if we inside mesh, if not, no chance
            #
            if n1 >= hl or n2 > hl or n3 >= hl:
                continue

            offset = [s["offsets"][0]*s0, s["offsets"][1]*s1, s["offsets"][2]*s2]
            dverts[n].co = \
                s["weights"][0] * hverts[n1].co + \
                s["weights"][1] * hverts[n2].co + \
                s["weights"][2] * hverts[n3].co + \
                Vector(offset)

        # if delete_verts is existing, create a group on the body
        #
        if self.delete:
            ogroups = human.vertex_groups

            # delete old group if already there
            #
            if self.delete_group in ogroups:
                vg = ogroups.get(self.delete_group)
                ogroups.remove(vg)
            #
            # now for security reasons do a local copy of delete_verts
            # with vertex number lower than the maxnumber of the human
            #
            dellist = []
            for n in  self.delverts:
                if n < hl:
                    dellist.append(n)
            #
            # and create new one
            #
            vgrp = ogroups.new(name=self.delete_group)
            vgrp.add(dellist, 1, 'ADD') 
        return


    def load (self, context, props):
        realpath = os.path.realpath(os.path.expanduser(props.filepath))
        folder = os.path.dirname(realpath)

        try:
            fp = open(props.filepath, "r")
        except:
            return None

        vn = 0
        status = ""

        for line in fp:
            words= line.split()

            l = len(words)

            if l == 0:
                status = ""
                continue

            # at least grab what you get from the comment
            #
            if words[0] == '#':
                if l > 2:
                    key = words[1].lower()
                    if "author" in key:
                        self.author = words[2]
                    elif "license" in key:
                        if "by" in line.lower():
                            self.license = "CC-BY"
                        elif "apgl" in line.lower():
                            self.license = "AGPL"
                    elif "description" in key:
                        self.description = " ".join(words[2:])
                continue

            # read vertices lines
            #
            if status == 'v':
                if words[0].isnumeric() is False:
                    status = ""
                    continue
                if l == 1:
                    v = int(words[0])
                    self.verts[vn] = {'verts': (v,v,v), 'weights': (1,0,0), 'offsets': Vector((0,0,0))}
                else:
                    v0 = int(words[0])
                    v1 = int(words[1])
                    v2 = int(words[2])
                    w0 = float(words[3])
                    w1 = float(words[4])
                    w2 = float(words[5])
                    d0 = float(words[6])
                    d1 = float(words[7])
                    d2 = float(words[8])
                    self.verts[vn] = {'verts': (v0,v1,v2), 'weights': (w0,w1,w2), 'offsets': Vector((d0,-d2,d1))}
                vn += 1
                continue
            elif status == 'd':
                if words[0].isnumeric() is False:
                    status = ""
                    continue
                sequence = False
                for v in words:
                    if v == "-":
                        sequence = True
                    else:
                        v1 = int(v)
                        if sequence:
                            for vn in range(v0,v1+1):
                                self.delverts.append(vn)
                            sequence = False
                        else:
                            self.delverts.append(v1)
                        v0 = v1
                continue

            key = words[0]
            status = ""
            if key == 'obj_file':
                self.obj_file = os.path.join(folder, words[1])
                print ("Loading: " + self.obj_file + "\n")
            elif key == 'verts':
                if len(words) > 1:
                    self.first = int(words[1])      # this value will be ignored, we always start from zero
                    status = "v"
            elif key == 'x_scale':
                self.xs = (int(words[1]), int(words[2]), float(words[3]))
            elif key == 'y_scale':
                self.ys = (int(words[1]), int(words[2]), float(words[3]))
            elif key == 'z_scale':
                self.zs = (int(words[1]), int(words[2]), float(words[3]))
            elif key == 'name':
                self.name = words[1]
            elif key == 'z_depth':
                self.zdepth = int(words[1])
            elif key == 'tag':
                if self.tags != "":
                    self.tags += ","
                self.tags += words[1].lower()
            elif key == 'delete_verts':
                self.delete = True
                status = 'd'

        fp.close

        if self.obj_file != "":
            obj = loadObjFile(context, self.obj_file)
            if obj is not None:
                self.clothes = obj
                context.active_object.MhObjectType = "Clothes"
                context.active_object.MhClothesName = self.name
                context.active_object.MhClothesTags = self.tags
                context.active_object.MhClothesDesc = self.description
                context.active_object.MhZDepth = self.zdepth
                context.scene.MhClothesAuthor = self.author
                context.scene.MhClothesLicense = self.license
                if self.delete is True:
                    self.delete_group = "Delete_" + self.name
                    context.active_object.MhDeleteGroup = self.delete_group
        return

    def setScalings (self, context, human):
        (baseMeshType, meshConfig) = _loadMeshJson(human)
        for bodypart in meshConfig["dimensions"]:
            dims = meshConfig["dimensions"][bodypart]
            # 
            # I think it is okay to check only one dimension to figure out on
            # what the piece of cloth was created
            #
            if dims['xmin'] == self.xs[0] and dims['xmax'] == self.xs[1]:
                context.active_object.MhOffsetScale = bodypart
        return

class MHC_OT_ImportClothesOperator(bpy.types.Operator, ImportHelper):
    """Import existent .mhclo file"""
    bl_idname = "makeclothes.import_mhclo"
    bl_label = "Import existent .mhclo file"
    bl_options = {'REGISTER', 'UNDO'}
    filename_ext = ".mhclo"

    filter_glob: StringProperty(
            default="*.mhclo",
            options={'HIDDEN'},
    )

    filepath: bpy.props.StringProperty(
        name="File Path", 
        description="File path used for importing the mhclo file", 
        maxlen= 1024)

    @classmethod
    def poll(self, context):
        return True

    def invoke(self, context, event):
        self.filepath = getClothesRoot("")
        wm = context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        humanObj = None
        for obj in context.scene.objects:
            if hasattr(obj, "MhObjectType"):
                if obj.MhObjectType == "Basemesh":
                    humanObj = obj
                    break

        im = import_mhclo()
        im.load (context, self.properties)
        if humanObj is not None:
            im.update(humanObj)                 # update on human
            im.setScalings(context, humanObj)   # and try to add offset scales
        return {'FINISHED'}
