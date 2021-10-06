import bpy
import math
import colorsys
from mathutils import Vector
import numpy as np

from .voronoi_2d_texture import render_voronoi

# gives UV coordinate where hair spawned
#mod = o.modifiers[0]
# mod.type = "ParticleSystem"
#o.particle_systems[0].particles[0].uv_on_emitter(mod)

# NOTES
# triangulate then mathutil.geometry.barycenter_transform ??
# same but with mathutils.geometry.closest_point_on_tri(p,a,b,c) to project onto tris

def force_object_mode():
    bpy.ops.object.mode_set(mode = 'OBJECT')
    
def vec_to_hue(vec):
    rad = math.atan2(vec.y,vec.x)
    hue = rad / math.pi / 2
    hue += 1 if hue < 0 else 0 
    return hue

def particle_to_face_relative_direction(particle):
    p_world_dir = particle_world_direction(particle)
    p_local_dir = o.matrix_world @ p_world_dir
    return 0
    
def particle_world_direction(particle):
    return particle.hair_keys[1] - particle.hair_keys[0]
    
def mk_image():
    size = 128,128
    image = bpy.data.images.new("MyImage", width=size[0], height=size[1])

    ## For white image
    # pixels = [1.0] * (4 * size[0] * size[1])

    pixels = [None] * size[0] * size[1]
    for x in range(size[0]):
        for y in range(size[1]):
            # assign RGBA to something useful
            r = x / size[0]
            g = y / size[1]
            b = (1 - r) * g
            a = 1.0

            pixels[(y * size[0]) + x] = [r, g, b, a]

    # flatten list
    pixels = [chan for px in pixels for chan in px]

    # assign pixels
    image.pixels = pixels

    # write image
    image.filepath_raw = "/tmp/temp.png"
    image.file_format = 'PNG' # OPEN_EXR ???
    #image.save()

def get_face_id_from_particle(particle, o):   
    local_p_loc = o.matrix_world.inverted() @ particle.location
    
    (hit, loc, norm, face_index) = o.closest_point_on_mesh(local_p_loc)
    return face_index

# convert a 3D vector into object space
def world_vec_to_object_space(v, o):
    return o.matrix_world @ v

# returns an nparray of 3 coefficients that solve the linear combination: v = a*b1 + b*b2 + c*b3
# b1, b2, b3, v are 3D vectors
def get_coefficients_from_linear_combo(b1, b2, b3, v):
    #basis = np.array( [ [b1.x, b1.y, b1.z],[b2.x, b2.y, b2.z],[b3.x, b3.y, b3.z] ] )
    basis = np.array( [ [b1.x, b2.x, b3.x],[b1.y, b2.y, b3.y],[b1.z, b2.z, b3.z] ] )
    result = [v.x, v.y, v.z]
    coefficients = np.linalg.solve(basis, result) 
    # print(coefficients)
    return coefficients

def particle_direction_to_uv_direction(p, o_eval, uvmap_str):
    face_id = get_face_id_from_particle(p, o_eval)
    #print("face_id: " + str(face_id))
    loop_indices = o_eval.data.polygons[face_id].loop_indices

    v0 = o_eval.data.vertices[o_eval.data.loops[loop_indices[0]].vertex_index].co
    v1 = o_eval.data.vertices[o_eval.data.loops[loop_indices[1]].vertex_index].co
    v2 = o_eval.data.vertices[o_eval.data.loops[loop_indices[2]].vertex_index].co

    #print("v0: " + str(v0))
    #print("v1: " + str(v1))
    #print("v2: " + str(v2))

    # 1--b--2
    # |
    # a
    # |
    # 0

    a = v0 - v1
    b = v2 - v1

    # generate a basis vector ortho to a and b
    c = a.cross(b)

    # object space coordinates
    v = p.hair_keys[1].co - p.hair_keys[0].co
    #print("v: " + str(v))

    coefficients = get_coefficients_from_linear_combo(a,b,c,v)
    a_coef = float(coefficients[0])
    b_coef = float(coefficients[1])
    #print("a:" + str(a_coef) + ", b:" + str(b_coef))

    v0_uv = o_eval.data.uv_layers[uvmap_str].data[loop_indices[0]].uv
    v1_uv = o_eval.data.uv_layers[uvmap_str].data[loop_indices[1]].uv
    v2_uv = o_eval.data.uv_layers[uvmap_str].data[loop_indices[2]].uv

    #print("v0_uv: " + str(v0_uv))
    #print("v1_uv: " + str(v1_uv))
    #print("v2_uv: " + str(v2_uv))

    #a_uv = v1_uv - v0_uv
    #b_uv = v2_uv - v0_uv
    a_uv = v0_uv - v1_uv
    b_uv = v2_uv - v1_uv
    v_uv = (a_coef * a_uv) + (b_coef * b_uv)

    #print("a_coef: " + str(a_coef) + ", b_coef: " + str(b_coef))
    #print("v_uv:" + str(v_uv))

    #hue = vec_to_hue(v_uv)
    return v_uv

def bake_comb_to_image( obj, uv_name, ps_name, img_name, voro_smooth_pts, voro_smooth_exp, voro_smooth_max_angle ):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    o_eval = obj.evaluated_get(depsgraph)
    image = bpy.data.images[img_name]
    mod = o_eval.modifiers[0]
    
    voro_points = []
    voro_vecs = []
        
    for p in o_eval.particle_systems[ps_name].particles:   
        uv_dir = particle_direction_to_uv_direction(p, o_eval, uv_name) # THIS BOY SPITTING OUT SLIGHTLY WRONG DATA
        uv = p.uv_on_emitter(mod)
        
        voro_vecs.append( Vector( (uv_dir.x, uv_dir.y, 0.0) ) )
        voro_points.append( Vector( (uv.x, uv.y, 0.0) ) )
        
        """
        hue = vec_to_hue(uv_dir)
        rgb = colorsys.hsv_to_rgb(hue,1.0,1.0)
        print("hue: " + str(hue))
        print("rgb: " + str(rgb))
        
        
        uv_to_px_co = {'x': int(image.size[0] * uv.x), 'y' : int(image.size[1] * uv.y)}
        px_byte_offset = uv_to_px_co['y'] * 4 * image.size[0] + uv_to_px_co['x'] * 4
        image.pixels[px_byte_offset+0] = rgb[0]
        image.pixels[px_byte_offset+1] = rgb[1]
        image.pixels[px_byte_offset+2] = rgb[2]
        """
        
    render_voronoi( image, voro_points, voro_vecs, voro_smooth_pts, voro_smooth_exp, voro_smooth_max_angle )
        
def bake_from_props( props ):
    #print("Baking from props...")
    bake_comb_to_image( props['obj'], props['uv_name'], props['ps_name'], props['img_name'], props['voro_smooth_pts'], props['voro_smooth_exp'], props['voro_smooth_max_angle'] )

       
