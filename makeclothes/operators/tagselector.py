#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy, bmesh
from ..extraproperties import mh_tags

class MHC_OT_TagSelector(bpy.types.Operator):
    bl_idname = "makeclothes.tag_selector"
    bl_label = "Edit tags"
    bl_options = {'REGISTER'}
    @classmethod
    def poll(cls, context):
        obj = context.object
        return True

    def invoke(self, context, event):
        #
        # here we can fill in the tags
        #
        sc = context.scene
        tags = context.object.MhClothesTags.split(",")
        #
        # reset everything
        #
        usertags = ""
        sc.MHTags_activity = sc.MHTags_dresscode = sc.MHTags_period = sc.MHTags_type = "none"
        #
        # now fill in the tags from MhClothesTags
        #
        for tag in tags:
            if len(tag) == 0:       # avoid empty tags
                continue
            found = 0
            for item in mh_tags["gender"]:
                if tag == item[0]:
                    sc.MHTags_gender = tag
                    found = 1
                    break
            if found:
                continue

            for item in mh_tags["dresscode"]:
                if tag == item[0]:
                    sc.MHTags_dresscode = tag
                    found = 1
                    break
            if found:
                continue

            for item in mh_tags["activity"]:
                if tag == item[0]:
                    sc.MHTags_activity = tag
                    found = 1
                    break
            if found:
                continue

            for item in mh_tags["period"]:
                if tag == item[0]:
                    sc.MHTags_period = tag
                    found = 1
                    break
            if found:
                continue

            for item in mh_tags["type"]:
                if tag == item[0]:
                    sc.MHTags_type = tag
                    found = 1
                    break
            if found:
                continue
            #
            #
            # everything not found is put in the user-tag
            #
            if len(usertags) > 0:
                usertags += ","
            usertags += tag

        sc.MHAdditionalTags = usertags
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, 'MHTags_gender')
        layout.prop(context.scene, 'MHTags_dresscode')
        layout.prop(context.scene, 'MHTags_activity')
        layout.prop(context.scene, 'MHTags_period')
        layout.prop(context.scene, 'MHTags_type')
        layout.prop(context.scene, 'MHAdditionalTags')


    def execute(self, context):

        # sample tags to form a string
        #
        sc = context.scene;
        context.object.MhClothesTags = ""
        #
        # throw away additional blanks between commas etc
        #
        addtags = ",".join(elem.strip() for elem in sc.MHAdditionalTags.split(","))

        for tag in (sc.MHTags_gender, sc.MHTags_dresscode, sc.MHTags_activity, sc.MHTags_activity, sc.MHTags_period, sc.MHTags_type, addtags):
            if tag != "none" and len(tag) > 0:
                if len(context.object.MhClothesTags) > 0:
                    context.object.MhClothesTags += ","
                #
                # TODO: should we exclude further characters here?
                #
                context.object.MhClothesTags += tag
        return {'FINISHED'}
