#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy, bmesh

_select_groups_map = dict()
_select_groups_map["BODY"] = ["body"]
_select_groups_map["SKIRT"] = ["helper-skirt"]
_select_groups_map["TIGHTS"] = ["helper-tights"]
_select_groups_map["EYES"] = ["helper-l-eye", "helper-r-eye"]
_select_groups_map["HAIR"] = ["helper-hair"]
_select_groups_map["EYELASHES"] = ["helper-l-eyelashes","helper-r-eyelashes"]
_select_groups_map["TEETH"] = ["helper-upper-teeth","helper-lower-teeth"]
_select_groups_map["TONGUE"] = ["helper-tongue"]
_select_groups_map["GENITALS"] = ["helper-genital"]
_select_groups_map["HELPERS"] = ["HelperGeometry"]

class MHC_OT_ExtractClothesOperator(bpy.types.Operator):
    """Extract one helper vertex group as clothes"""
    bl_idname = "makeclothes.extract_clothes"
    bl_label = "Extract helper as clothes"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(self, context):
        if context.active_object is not None:
            if not hasattr(context.active_object, "MhObjectType"):
                return False
            if context.active_object.select_get():
                if context.active_object.MhObjectType == "Basemesh":
                    return True
        return False

    def checkHasGroup(self, humanObj, groupName):
        for group in humanObj.vertex_groups:
            if group.name == groupName:
                return True
        return False

    def execute(self, context):

        humanObj = context.active_object
        scn = context.scene

        what = scn.MhExtractClothes

        if not what in _select_groups_map:
            self.report({'ERROR'}, "No such group: " + what)
            return {'FINISHED'}

        groupNames = _select_groups_map[what]

        if len(groupNames) < 1:
            self.report({'ERROR'}, what + " is empty")
            return {'FINISHED'}

        for groupName in groupNames:
            if not self.checkHasGroup(humanObj, groupName):
                self.report({'ERROR'}, "This mesh does not have the " + groupName + " vertex group. Maybe you didn't import with detailed helpers?")
                return {'FINISHED'}

        mesh = bpy.data.meshes.new("clothes")
        newObj = bpy.data.objects.new("clothes", mesh)

        for ob in context.selected_objects:
            ob.select_set(False)

        context.collection.objects.link(newObj)
        context.view_layer.objects.active = newObj

        bmOld = bmesh.new()
        bmOld.from_mesh(humanObj.data)

        bmNew = bmOld.copy()

        groupIndexes = dict()

        for group in humanObj.vertex_groups:
            vg = newObj.vertex_groups.new(name=group.name)
            if group.name in groupNames:
                groupIndexes[group.index] = group.name

        print(groupIndexes)

        vertsToDelete = []
        for vert in humanObj.data.vertices:
            doDelete = True
            if len(vert.groups) > 0:
                # Assume each vertex belongs to only one group
                gidx = vert.groups[0].group
                if not gidx in groupIndexes:
                    vertsToDelete.append(vert.index)

        vertsToDelete.sort(reverse=True)

        for vertIdx in vertsToDelete:
            bmNew.verts.ensure_lookup_table()
            v = bmNew.verts[vertIdx]
            bmNew.verts.remove(v)

        mesh = context.object.data

        bmNew.to_mesh(mesh)
        bmNew.free()

        bmOld.free()

        newObj.location = humanObj.location

        newObj.MhObjectType = "Clothes"

        # This is a stupid way to do it, but:
        #
        # * cloning a bmesh keeps vgroup index settings on each vertex
        # * cloning a bmesh *does not* also clone vgroups
        # * You can't create a vgroup with a specific index (index is read-only)
        #
        # Thus the only recourse is copying all vgroups and then delete the ones not relevant

        for group in humanObj.vertex_groups:
            vg = newObj.vertex_groups.new(name=group.name)

        groupsToKeep = []

        for vgidx in groupIndexes.keys():
            name = groupIndexes[vgidx]
            groupsToKeep.append(name)

        for group in newObj.vertex_groups:
            if not group.name in groupsToKeep:
                newObj.vertex_groups.remove(group)

        self.report({'INFO'}, "Extracted " + what)
        return {'FINISHED'}
