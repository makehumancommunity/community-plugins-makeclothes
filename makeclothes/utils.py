#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Author: Joel Palmius

import os
import io
import sys
import bpy
import inspect
from addon_utils import check, paths, enable, modules

# we need this for the standard obj-loader 
#
from mathutils import Matrix
from bpy_extras.io_utils import axis_conversion
from io_scene_obj import import_obj

LEAST_REQUIRED_MAKESKIN_VERSION = 20200116
_TRACING = True

def getMyDocuments():
    import sys
    if sys.platform == 'win32':
        import winreg
        try:
            k = winreg.HKEY_CURRENT_USER
            for x in ['Software', 'Microsoft', 'Windows', 'CurrentVersion', 'Explorer', 'Shell Folders']:
                k = winreg.OpenKey(k, x)

            name, type = winreg.QueryValueEx(k, 'Personal')

            if type == 1:
                print(("Found My Documents folder: %s" % name))
                return name
        except Exception as e:
            print("Did not find path to My Documents folder")
    if sys.platform.startswith('linux'):
        try:
            from .xdg_parser import XDG_PATHS
            doc_folder = XDG_PATHS.get('DOCUMENTS', '')
            if doc_folder and doc_folder != "":
                print("Using " + doc_folder + " as user root")
                return doc_folder
        except:
            print("Error when trying to get DOCUMENTS dir")
    return os.path.expanduser("~")

#
# use exact the same method as makehuman if a makehuman.conf file exists

def pathFromConfigFile():
    configFile = ''
    if sys.platform.startswith('linux'):
        configFile = os.path.expanduser('~/.config/makehuman.conf')

    elif sys.platform.startswith('darwin'):
        configFile = os.path.expanduser('~/Library/Application Support/MakeHuman/makehuman.conf')

    elif sys.platform.startswith('win32'):
        configFile = os.path.join(os.getenv('LOCALAPPDATA', ''), 'makehuman.conf')

    configPath = ''

    if os.path.isfile(configFile):
        with io.open(configFile, 'r', encoding='utf-8') as f:
            configPath = f.readline().strip()

    homepath = ""
    if os.path.isdir(configPath):
        homepath = os.path.normpath(configPath).replace("\\", "/")
    return (homepath)


def getMHDirectory():
    mydocs = pathFromConfigFile()

    if len(mydocs) == 0:
        mydocs = getMyDocuments()

    mhdir = os.path.join(mydocs, "makehuman", "v1py3")
    return mhdir

def getClothesRoot(subdir = None):
    if subdir is None:
        subdir = "clothes"
    mhdir = getMHDirectory()
    return os.path.join(mhdir,"data",subdir)

# 
# function to call standard object loader
#
def loadObjFile(context, filename):
    #
    # remember all objects
    #
    oldnames = []
    for obj in context.scene.objects:
        oldnames.append (obj.name)

    global_matrix = (Matrix.Scale(1.0, 4) @ 
        axis_conversion(from_forward='-Y',to_forward='-Z', from_up='Z', to_up='-Y',).to_4x4())
    import_obj.load(context, filename, use_split_objects=False,
        use_groups_as_vgroups=True, global_matrix=global_matrix)

    #
    # get all objects and figure out the new mesh
    #
    for obj in context.scene.objects:
        if obj.name not in oldnames:
           context.view_layer.objects.active = obj
           bpy.ops.object.shade_smooth()
           bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
           return (obj)

    return (None)

def checkMakeSkinAvailable():
    for path in paths():
        for mod_name, mod_path in bpy.path.module_names(path):
            is_enabled, is_loaded = check(mod_name)
            if mod_name == "makeskin":
                return is_enabled and is_loaded
    return False

def trace(message = None):
    global _TRACING
    if _TRACING:
        info = dict()

        stack = inspect.currentframe().f_back
        info["line_number"] = str(stack.f_lineno)
        info["caller_name"] = stack.f_globals["__name__"]
        info["file_name"] = stack.f_globals["__file__"]
        info["caller_method"] = inspect.stack()[1][3]

        stack = inspect.stack()
        info["caller_class"] = str(stack[1][0].f_locals["self"].__class__)

        print("TRACE {}.{}():{}".format(info["caller_name"], info["caller_method"], info["line_number"]))
