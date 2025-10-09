#!/usr/bin/python
# -*- coding: utf-8 -*-

import re, os

class MHMATKey:

    def __init__(self, keyName, defaultValue=None, keyGroup="Various"):
        self.keyName = keyName
        self.defaultValue = defaultValue
        self.keyNameLower = keyName.lower()
        self.keyGroup = keyGroup

    def lineMatchesKey(self, inputLine):
        if not inputLine:
            return False
        line = str(inputLine).lower()
        return line.startswith(self.keyNameLower)

    def parse(self, inputLine):
        raise ValueError('parse() should be overridden by specific key classes')

    def asString(self, value):
        return str(value)

# parse lines like name, description
#

class MHMATStringKey(MHMATKey):

    def __init__(self, keyName, defaultValue=None, keyGroup="Various"):
        MHMATKey.__init__(self, keyName=keyName, defaultValue=defaultValue, keyGroup=keyGroup)

    def parse(self, inputLine):
        line = str(inputLine).strip()
        value = None
        if self.lineMatchesKey(line):
            match = re.search(r'^([a-zA-Z]+)\s+(.*)$', line)
            if match:
                value = str(match.group(2)).strip()
        return self.keyName, value

# parse filenames like diffuseTexture, normalmapTexture ...
# 
# a path could be:
#   * absolute filepath 
#   * relative filepath like "materials/clothname.png"
#   * a filename
#
class MHMATFileKey(MHMATKey):

    def __init__(self, keyName, defaultValue=None, keyGroup="Various"):
        MHMATKey.__init__(self, keyName=keyName, defaultValue=defaultValue, keyGroup=keyGroup)
        self.blendMaterial = False

    def parseFile(self, inputLine, location):
        line = str(inputLine).strip()
        value = None
        if self.lineMatchesKey(line):
            match = re.search(r'^([a-zA-Z]+)\s+(.*)$', line)
            if match:
                value = str(match.group(2)).strip()
        if not self.blendMaterial:
            if not value.startswith("/"):
                value = location + "/" + value
        else:
            # TODO: handle case where location is absolute. We cannot use basename since the path
            # TODO: continues into the structure of the file
            value = location + "/" + value
        return self.keyName, value

class MHMATFloatKey(MHMATKey):

    def __init__(self, keyName, defaultValue=None, keyGroup="Various"):
        MHMATKey.__init__(self, keyName=keyName, defaultValue=defaultValue, keyGroup=keyGroup)

    def parse(self, inputLine):
        line = str(inputLine).strip()
        value = None
        if self.lineMatchesKey(line):
            match = re.search(r'^([a-zA-Z]+)\s+(.*)$', line)
            if match:
                value = str(match.group(2)).strip()
                value = float(value)
        return self.keyName, value

    def asString(self, value):
        return "%.4f" % value


class MHMATBooleanKey(MHMATKey):

    def __init__(self, keyName, defaultValue=None, keyGroup="Various"):
        MHMATKey.__init__(self, keyName=keyName, defaultValue=defaultValue, keyGroup=keyGroup)

    def parse(self, inputLine):
        line = str(inputLine).strip()
        value = None
        if self.lineMatchesKey(line):
            match = re.search(r'^([a-zA-Z]+)\s+(.*)$', line)
            if match:
                value = str(match.group(2)).strip().lower()
                if value != "":
                    value = value == "true" or value == "t" or value == "1"
        return self.keyName, value

class MHMATColorKey(MHMATKey):

    def __init__(self, keyName, defaultValue=None, keyGroup="Various"):
        MHMATKey.__init__(self, keyName=keyName, defaultValue=defaultValue, keyGroup=keyGroup)

    def parse(self, inputLine):
        line = str(inputLine).strip()
        value = None
        if self.lineMatchesKey(line):
            match = re.search(r'^([a-zA-Z]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)$', line)
            if match:
                red = float(str(match.group(2)).strip())
                green = float(str(match.group(3)).strip())
                blue = float(str(match.group(4)).strip())
                value = [red, green, blue]
        return self.keyName, value

    def asString(self, value):
        return "%.4f %.4f %.4f" % (value[0], value[1], value[2])


class MHMATStringShaderKey(MHMATKey):

    def __init__(self, keyName, defaultValue=None, keyGroup="Shader"):
        MHMATKey.__init__(self, keyName=keyName, defaultValue=defaultValue, keyGroup=keyGroup)

    def parse(self, inputLine):
        line = str(inputLine).strip()
        value = None
        if self.lineMatchesKey(line):
            match = re.search(r'^([a-zA-Z]+)\s+([^\s]+)\s+([^\s]+)$', line)
            if match:
                subkey = str(match.group(2))
                ivalue = str(match.group(3)).strip()
                value = [subkey, ivalue]
        return self.keyName, value

class MHMATBooleanShaderKey(MHMATKey):

    def __init__(self, keyName, defaultValue=None, keyGroup="Shader"):
        MHMATKey.__init__(self, keyName=keyName, defaultValue=defaultValue, keyGroup=keyGroup)

    def parse(self, inputLine):
        line = str(inputLine).strip()
        value = None
        if self.lineMatchesKey(line):
            match = re.search(r'^([a-zA-Z]+)\s+([^\s]+)\s+([^\s]+)$', line)
            if match:
                value = str(match.group(3)).strip()
                if value != "":
                    value = value == "true" or value == "t" or value == "1"
        return self.keyName, value

