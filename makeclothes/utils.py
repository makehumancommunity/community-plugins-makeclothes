#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Author: Joel Palmius

import os
import io
import sys
import inspect

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
