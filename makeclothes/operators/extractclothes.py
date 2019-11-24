#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy, bmesh
from ..core_makeclothes_functionality import _loadMeshJson

_extractGroupDescription = "You can create a new mesh based on a vertex group in an imported human. Note that this is only possible if you imported with \"detailed helpers\". Without that, the only group possible to extract will be \"body\" and \"helpers\"."

def EvaluateGroupsCallback(self, context):
    _extractGroup = []

    if hasattr (context, "object"):
        (meshtype, jlines) = _loadMeshJson(context.object)
        cnt = 1
        for gname in jlines["select_groups"]:
            gl_name = gname.lower()
            _extractGroup.append((gname, gl_name.capitalize(), "Create clothes from " + gl_name, cnt))
            cnt += 1
    return (_extractGroup)

class MHC_OT_ExtractClothesOperator(bpy.types.Operator):
    """Extract one helper vertex group as clothes"""
    bl_idname = "makeclothes.extract_clothes"
    bl_label = "Extract helper as clothes"
    bl_options = {'REGISTER', 'UNDO'}

    extract: bpy.props.EnumProperty(items=EvaluateGroupsCallback, name="Extract", description=_extractGroupDescription)

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

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'extract')

    def execute(self, context):

        humanObj = context.active_object
        scn = context.scene

        (meshtype, jlines) = _loadMeshJson(humanObj)
        what = self.extract

        if not what in jlines["select_groups"]:
            self.report({'ERROR'}, "No such group: " + what)
            return {'FINISHED'}

        groupNames = jlines["select_groups"][what]

        if len(groupNames) < 1:
            self.report({'ERROR'}, what + " is empty")
            return {'FINISHED'}

        for groupName in groupNames:
            if not self.checkHasGroup(humanObj, groupName):
                self.report({'ERROR'}, "This mesh does not have the " + groupName + " vertex group. Maybe you didn't import with detailed helpers?")
                return {'FINISHED'}

        # when a mesh was loaded by normal wavefront loader, the groups can be used also, but the mesh transformations must be
        # applied before
        #
        context.view_layer.objects.active = humanObj
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

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
