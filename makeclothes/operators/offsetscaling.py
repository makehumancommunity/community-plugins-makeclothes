#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from ..core_makeclothes_functionality import _loadMeshJson

_offsetScalingDescription = "Offset-Scaling"

def EvaluateScalingCallback(self, context):
    _extractScaling = []


    if hasattr (context, "object"):
        humanObj = None
        for obj in context.scene.objects:
            if hasattr(obj, "MhObjectType"):
                if obj.MhObjectType == "Basemesh":
                    humanObj = obj
                    break
        if humanObj is not None:
            (meshtype, jlines) = _loadMeshJson(humanObj)
            cnt = 1
            for gname in jlines["dimensions"]:
                gl_name = gname.lower()
                _extractScaling.append((gname, gl_name.capitalize(), "Use scaling of " + gl_name, cnt))
                cnt += 1
    return (_extractScaling)

class MHC_OT_GetOffsetScaling(bpy.types.Operator):
    """Select an offset scaling used to get the dimensions for clothes"""
    bl_idname = "makeclothes.offset_scaling"
    bl_label = "Offset Scaling"
    bl_options = {'REGISTER', 'UNDO'}

    scaling: bpy.props.EnumProperty(items=EvaluateScalingCallback, name="scaling", description=_offsetScalingDescription)

    @classmethod
    def poll(self, context):
        if context.active_object is not None:
            if not hasattr(context.active_object, "MhObjectType"):
                return False
            if context.active_object.select_get():
                if context.active_object.MhObjectType != "Basemesh":
                    return True
        return False

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'scaling')

    def execute(self, context):
        context.active_object.MhOffsetScale =  self.scaling
        self.report({'INFO'}, "Scaling is based on " + self.scaling)
        return {'FINISHED'}
