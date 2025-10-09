# MakeClothes 2 for MakeHuman Version II

This repository contains a version of MakeClothes which is capable to work with MakeHuman Version I und also II. For Version II there is also material editor included.

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

* Select MakeHuman version (this will determine path names and if the built-in material editor can be used).
* Import a mesh with "import predefined human". Makeclothes sets character mesh-type to hm08.
* Create clothes, for MakeHuman version I clothes may only consist of triangles or quads. MakeHuman version II deals with each kind of geometry. Be aware that the result of polygons with a high vertex-count may behave bad in animations.
* Assign vertex groups to human and clothes using the same names. Cloth-vertices may only be in one group.
* Add delete groups in case parts of the human should not be visible under the clothes.
* If MakeHuman II is used, you can add a material accordingly. For makehuman I a dummy material is created and you need to use the MakeHuman editor itself.


The basic workflow for a different mesh (custom base) is:

* switch to MakeHuman version II.
* add the name of the standard base. It will determine the subfolders inside MakeHuman II. A config-file for that mesh must also be in the data-folder. It will be used for dimensions.
* import obj file or load file with the standard base.
* Create clothes.
* Assign vertex groups to human (or basis) and clothes using the same names. Cloth-vertices may only be in one group.
* Add delete groups in case parts of the base should not be visible under the clothes.
* A material can be added as well.

## Material Editor (only for MakeHuman Version II)

_The material editor is limited to the material keywords which are provided by MakeHuman II. With shader type PBR all parameters can be used in Makehuman II (except litsphere)._

| key                      | Source | Description |
| :----------------------- | :-------: | :---------- |
| tag                      | Input box of material menu | tags added to the material, used for filtering |
| name                     | Input box of material menu | name added to the material |
| description              | Input box of material menu | description added to the material |
| license                  | Input box of mesh menu | licence is copied from mesh licence |
| author                   | Input box of mesh menu | author is copied from mesh licence if not "unknown" |
| ambientColor             | Color entry of AO Separator | grey-scale, used with no ambient occlusion map, otherwise white |
| diffuseColor             | Base Color entry of principled shader | base color, used when no diffuse texture is given |
| emissiveColor            | Emission Color entry of principled shader | emission color, used when no emission texture is given and emission color is not black |
| aomapTexture             | file name from aomapTexture node | ambient occlusion texture, a method to use ambient light, this is usually a grey map. So only one channel is used. |
| diffuseTexture           | file name from diffuseTexture node | diffuse texture for the used colors. |
| emissiveTexture          | file name from emissiveTexture node | texture for illumination. |
| metallicRoughnessTexture | file name from metallicRoughnessTexture node | a standard method using green channel for roughness and blue channel for metallic entry. |
| normalmapTexture         | file name from normalmapTexture node | normal map to simulate higher detail by colors. |
| aomapIntensity           | Fac of AO Mixer multiplied by 2 | intensity of the ambient occlusion map, without map ambient occkusion from a grey-scale, 1.0 is normal, up to 2.0 |
| emissiveFactor           | Color Strenght fof  principled shader, values 0-255 | intensity of light. 0-255 will be recalculated to 0-1. Blender may use bloom effects to visualize bright light |
| metallicFactor           | Metallic entry of principled shader | metallic factor of a material, in case of a given texture it is 1.0 which is the value how much the metallic texture is used |
| normalmapIntensity       | Strength entry of Normalmap node | intensity of normals |
| pbrMetallicRoughness     | Roughness entry of principled shader | roughness factor of a material, in case of a texture it is 1.0 which is the value how much the roughness texture is used |
| shader                   | Selection box of material menu | shader type (pbr, toon, phong, litsphere) |
| shaderParam litsphereTexture | Selection box of material menu |  a default litsphere map for litsphere shader, no effect for other shaders |
| alphaToCoverage          | Check box of material menu | parameter to be used when having multiple transparent layers (classical used for hair) |
| transparent              | Check box of material menu | shader should use alpha channel, because material is transparent |
| backfaceCull             | Check box of material menu | material used for front and backside (false: both sides are visible) |


