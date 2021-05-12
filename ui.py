bl_info = {
    "name": "Say Hello",
    "blender": (2, 83, 0),
    "category": "Object",
}

import bpy

class CombMapProps(bpy.types.PropertyGroup):
  obj_name : bpy.props.StringProperty(name="OBJ")
  uv_name : bpy.props.StringProperty(name="UV")
  ps_name : bpy.props.StringProperty(name="PS")
  img_name : bpy.props.StringProperty(name="IMG")
  
  voro_smooth_pts : bpy.props.IntProperty(name="Smoothing Points", default=4, min=0)
  voro_smooth_exp : bpy.props.FloatProperty(name="Smoothing Exponent", default=1.0, min=0)
  voro_smooth_max_angle : bpy.props.FloatProperty(name="Maximum Smoothing Angle", default=180.0, min=0.0, max=180.0)
    
class COMB_MAP_OT_render(bpy.types.Operator):
    """Render hair particle direction onto a given image. Uses CombMapProps."""
    bl_idname = "comb_map.render"
    bl_label = "Render Comb Map"
    bl_options = {'REGISTER'}  # 'UNDO'
    
    def execute(self, context):
        print("Rendering...")
        comb_bake = bpy.data.texts["comb_bake.py"].as_module()
        comb_bake.bake( {'hek'} )
        
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return True
    
    def check(self, context):
        return True
        
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=240)
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Wow!")
        
class PANEL123_PT_SayHello(bpy.types.Panel): #bpy.types.Operator
    """Says Hello in console"""      # Use this as a tooltip for menu items and buttons.
    """
    bl_idname = "console.hello"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Say Hello"         # Display name in the interface.
    bl_options = {'REGISTER'}  # 'UNDO' Enable undo for the operator.
    """
    bl_label = "My Panel"
    bl_idname = "my_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Library Texture List"
    #bl_context = "objectmode"

    """
    def execute(self, context):        # execute() is called when running the operator.

        print( self.text )
        
        return {'FINISHED'}            # Lets Blender know the operator finished successfully.

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    """
    
    def draw(self, context):
        layout = self.layout
        comb_map_props = context.scene.comb_map_props
        obj = bpy.context.active_object
        
        col = layout.column(align=True)
        obj_box = col.box()
        row = obj_box.row()
        row.label(text="Active object: " + context.object.name)
        
        obj_box.prop_search(context.scene.comb_map_props, "ps_name", obj, "particle_systems", icon='PARTICLE_DATA')
        obj_box.prop_search(context.scene.comb_map_props, "uv_name", obj.data, "uv_layers", icon='DOT')
        obj_box.prop_search(context.scene.comb_map_props, "img_name", bpy.data, "images", icon='TEXTURE')
        
        col.separator()
        
        smoothing_box = col.box()
        smoothing_box.prop(context.scene.comb_map_props, "voro_smooth_pts")
        smoothing_box.prop(context.scene.comb_map_props, "voro_smooth_exp")
        smoothing_box.prop(context.scene.comb_map_props, "voro_smooth_max_angle")
        
        col.separator()
        
        col.operator( 'comb_map.render', text="Render" )
      
def register():
    bpy.utils.register_class(CombMapProps)
    bpy.utils.register_class(COMB_MAP_OT_render)
    bpy.utils.register_class(PANEL123_PT_SayHello)
    bpy.types.Scene.comb_map_props = bpy.props.PointerProperty(type=CombMapProps)

def unregister():
    bpy.utils.unregister_class(CombMapProps)
    bpy.utils.unregister_class(COMB_MAP_OT_render)
    bpy.utils.unregister_class(PANEL123_PT_SayHello)
    del bpy.types.Scene.comb_map_props


# This allows you to run the script directly from Blender's Text editor
# to test the add-on without having to install it.
if __name__ == "__main__":
    register()