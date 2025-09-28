# MakeClothes 2 for MakeHuman Version II

This repository contains a version of MakeClothes which is capable to work with MakeHuman Version I und also II.

## Requirements

This version is tested with blender version 4.5 LTS. There is a MakeClothes inside [the makehuman plugin for blender II](https://github.com/makehumancommunity/mpfb2), which can be used for MakeHuman Version 1 or for the hm08 mesh of Version 2.

This version of MakeClothes should be used for MakeHuman Version 2, especially for non-hm08 meshes.

hm08 base-meshes are supplied in a blend file to make the work easier. For different meshes you need your custom base to be loaded.

Makeclothes is usually able to determine the path the clothes have to be saved to. When you use Makehuman II with sandboxed APPDATA on Windows, the system is only able to deal with one python version.

Nevertheless, the expected path is always shown. You can use an alternative path as well.

## Usage

More detailed information is presented here: [Introduction to MakeClothes](https://static.makehumancommunity.org/assets/creatingassets/makeclothes/introduction.html)

_the changes for version II will be added soon._

When installed, you will find a "MakeClothes2" panel on the N-shelf in blender.

The basic workflow for hm08 mesh including helper is:

* Import a mesh with "import predefined human". Makeclothes sets character mesh-type to hm08.
* Create clothes, for MakeHuman version I clothes may only consist of triangles or quads. MakeHuman version II deals with each kind of geometry. Be aware that the result of polygons with a high vertex-count may behave bad in animations.
* Assign vertex groups to human and clothes using the same names. Cloth-vertices may only be in one group.
* Add delete groups in case parts of the human should not be visible under the clothes.


The basic workflow for a different mesh (custom base) is:

* switch to MakeHuman version II
* add the name of the standard base. It will determine the subfolders inside MakeHuman II. A config-file for that mesh must also be in the data-folder. It will be used for dimensions.
* import obj file or load file with the standard base
* Create clothes
* Assign vertex groups to human (or basis) and clothes using the same names. Cloth-vertices may only be in one group.
* Add delete groups in case parts of the base should not be visible under the clothes.
