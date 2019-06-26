#!/usr/bin/python
# -*- coding: utf-8 -*-

import math

class MHVertex:

    index: 0
    x: 0
    y: 0
    z: 0
    scale: 1.0
    vgroups: []

    def __init__(self, index, x, y, z, scale = 1.0, vgroups = None):
        self.index = index
        self.x = x
        self.y = y
        self.z = z
        self.scale = scale
        if not vgroups is None:
            self.vgroups = vgroups

    def distance(self, otherVertex):
        """Simple pythagora's for finding distance between two vertices in 3d space"""
        xdelta = abs(self.x - otherVertex.x)
        ydelta = abs(self.y - otherVertex.y)
        zdelta = abs(self.z - otherVertex.z)

        x2 = xdelta * xdelta
        y2 = ydelta * ydelta
        z2 = zdelta * zdelta

        # Just so we don't attempt a square root of zero
        if (x2 + y2 + z2) < 0.0001:
            return 0.0

        return math.sqrt(x2 + y2 + z2)

    def addVGroup(self, vgroup):
        if not vgroup in self.vgroups:
            self.vgroups.append(vgroup)

    def __str__(self):
        return "VERTEX(" + str(self.index) + ": " + str(self.x) + " " + str(self.y) + " " + str(self.z) + ")"
