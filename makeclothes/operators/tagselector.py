#!/usr/bin/python
# -*- coding: utf-8 -*-

import bpy
from ..extraproperties import mh_tags

class MHC_OT_TagSelector(bpy.types.Operator):
    """select tags for filtering clothes"""
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
        usertags = set()
        for group in mh_tags.keys():
            setattr(sc, 'MHTags_'+group.lower(), "none")

        #
        # now fill in the tags from MhClothesTags
        #

        for tag in tags:

            if len(tag) == 0:       # avoid empty tags
                continue

            found = False
            for group, gr_items in mh_tags.items():
                for item in gr_items:
                    if tag == item[0]:
                        setattr(sc, 'MHTags_'+group.lower(), tag)
                        found = True
                        break
                if found:
                    break

            # if tag is not found, put it in the user tags
            #
            if not found:
                usertags.add(tag)

        sc.MHAdditionalTags = ', '.join(sorted(usertags))
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        for group in mh_tags.keys():
            layout.prop(context.scene, 'MHTags_'+group.lower())
        layout.prop(context.scene, 'MHAdditionalTags')


    def execute(self, context):

        # sample tags to form a string
        #
        sc = context.scene
        context.object.MhClothesTags = ""
        #
        # throw away additional blanks between commas etc
        #
        addtags = ",".join(elem.strip() for elem in sc.MHAdditionalTags.split(","))
        defaulttags = [getattr(sc, 'MHTags_'+group.lower()) for group in mh_tags.keys()]

        for tag in [*defaulttags, addtags]:
            if tag != "none" and len(tag) > 0:
                if len(context.object.MhClothesTags) > 0:
                    context.object.MhClothesTags += ","
                #
                # TODO: should we exclude further characters here?
                #
                context.object.MhClothesTags += tag
        return {'FINISHED'}
