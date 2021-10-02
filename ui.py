import bpy

from .comb_bake import bake_from_props

def gather_props( context ):
    return {
        'obj' : context.active_object,
        'uv_name' : context.scene.comb_map_props.uv_name,
        'ps_name' : context.scene.comb_map_props.ps_name,
        'img_name' : context.scene.comb_map_props.img_name,
        
        'voro_smooth_pts' : context.scene.comb_map_props.voro_smooth_pts,
        'voro_smooth_exp' : context.scene.comb_map_props.voro_smooth_exp,
        'voro_smooth_max_angle' : context.scene.comb_map_props.voro_smooth_max_angle,
    }
    
def verify_props( props ):
    if props['obj'] is None:
        return {'is_valid': False, 'message':"No Object is selected."}
    
    if props['uv_name'] == '':
        return {'is_valid': False, 'message':"No UVMap is selected."}
    
    if props['ps_name'] == '':
        return {'is_valid': False, 'message':"No Particle System is selected."}
    
    if props['img_name'] == '':
        return {'is_valid': False, 'message':"No Image is selected."}
    
    return {'is_valid': True, 'message':None}

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
        #print("Rendering comb map...")
        
        props = gather_props( context )
        validation = verify_props( props )
        
        if not validation['is_valid']:
            self.report( {'ERROR_INVALID_INPUT'}, validation['message'] )
            return {'CANCELLED'}
        
        bake_from_props( props )
        
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return True
    
    def check(self, context):
        return True
      
    """  
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=240)
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.label(text="Wow!")
    """
        
class COMB_MAP_PT_bake(bpy.types.Panel): #bpy.types.Operator
    """A UI panel for the comb bake operator"""
    bl_label = "My Panel"
    bl_idname = "my_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bake Comb Map"
    #bl_context = "objectmode"
    
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
    bpy.utils.register_class(COMB_MAP_PT_bake)
    bpy.types.Scene.comb_map_props = bpy.props.PointerProperty(type=CombMapProps)

def unregister():
    bpy.utils.unregister_class(CombMapProps)
    bpy.utils.unregister_class(COMB_MAP_OT_render)
    bpy.utils.unregister_class(COMB_MAP_PT_bake)
    del bpy.types.Scene.comb_map_props

if __name__ == "__main__":
    register()