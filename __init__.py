'''
template source: https://github.com/JacquesLucke/code_autocomplete/tree/master/addon_development/addon_templates
'''

bl_info = {
    "name": "Comb Bake",
    "description": "",
    "author": "Fred",
    "version": (1, 0, 2),
	"blender": (2, 93, 0),
    "location": "View3D",
    "warning": "Work in progress.",
    "wiki_url": "",
    "category": "Object" }


import bpy

# load and reload submodules
##################################

import importlib
from . import ui
from . import comb_bake

#from . import comb_bake
from .ui import CombMapProps, COMB_MAP_OT_render, COMB_MAP_PT_bake

importlib.reload(ui)
importlib.reload(comb_bake)
importlib.reload(voronoi_2d_texture)

classes = [CombMapProps, COMB_MAP_OT_render, COMB_MAP_PT_bake]
# register
##################################

import traceback

def register():
    for cls in classes:
        try: bpy.utils.register_class(cls)
        except: traceback.print_exc()
    
    bpy.types.Scene.comb_map_props = bpy.props.PointerProperty(type=CombMapProps)
    #print("Registered {} with {} modules".format(bl_info["name"], len(modules)))

def unregister():
    for cls in classes:
        try: bpy.utils.unregister_class(cls)
        except: traceback.print_exc()

    del bpy.types.Scene.comb_map_props
    #print("Unregistered {}".format(bl_info["name"]))
