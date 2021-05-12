import bpy
import math
#from functools import reduce
import colorsys
import mathutils
from mathutils import Vector
#import numpy as np
import random

def write_pixel_to_image( img, co, hsv ):
    rgb = colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2])
    px_byte_offset = co[1] * 4 * img.size[0] + co[0] * 4
    img.pixels[px_byte_offset+0] = rgb[0]
    img.pixels[px_byte_offset+1] = rgb[1]
    img.pixels[px_byte_offset+2] = rgb[2]

def vec_to_hue(vec):
    rad = math.atan2(vec.y,vec.x)
    hue = rad / math.pi / 2
    hue += 1 if hue < 0 else 0 
    return hue

def append_rgb_to_buf( buf, rgb ):
    buf.append(rgb[0])
    buf.append(rgb[1])
    buf.append(rgb[2])
    buf.append(1)
    
def append_hsv_to_buf( buf, hsv ):
    append_rgb_to_buf( buf, colorsys.hsv_to_rgb(hsv[0], hsv[1], hsv[2]) )

def mean_weighted_vector( vecs_with_weights ): #[ (Vector(), weight), ... ]
    #zipped = zip( vecs, weights )
    mean = Vector()
    for (vec, weight) in vecs_with_weights:
        mean += vec * weight
    #weighted_mean = reduce( lambda a,b:( (a[0]*a[1] + b[0]*b[1]).normalized(), a[1]+b[1] ), vecs_with_weights )
    
    """
    if ( weighted_mean.length == 0.0 ):
        # return vec with most weight
    """
    if ( mean.length <= 0.001 ):
        print("Warning: mean.length is VERY small: " + str(mean.length))
    
    return mean.normalized()
        
def render_voronoi( img, points, vecs, smoothing_points=4, smoothing_exponent=2.0, max_angle_diff=181.0 ):
    """
    Renders a voronoi diagram using a kd-tree
    
    img: Blender image that will be written to
    points: 2D points for building the kd-tree
    vecs: 2D vectors that correspond to each point from points
    smoothing_points: The n-nearest points for used for color smoothing
    smoothing_exponent: Exponent for color smoothing. Higher exponents create sharper gradients
    max_angle_diff: The maximum vector angle difference between any 2 points. If the difference between the
        angles is greater than this, then no color smoothing will be done between these points
    """
    max_angle_diff_rad = math.radians(max_angle_diff)
    smoothing_points = max(smoothing_points,1)
    
    kd = mathutils.kdtree.KDTree(len(points))
    
    for i, co in enumerate(points):
        kd.insert(co, i)
        
    kd.balance()
    
    buffer = []
    dims = img.size
    
    for y in range(0, img.size[1]):
        for x in range(0, img.size[0]):
            uv_co = (x/img.size[0],y/img.size[1])
            found_list = kd.find_n( (uv_co[0],uv_co[1],0), smoothing_points ) # [ (co, index, dist), ... ]
            nearest_vec = vecs[found_list[0][1]]
            
            allowable_points = found_list
            
            if ( max_angle_diff < 180.0 ):
                allowable_points = found_list[0:1]
                for found in found_list[1:]:
                    vec = vecs[found[1]]
                    if ( abs( nearest_vec.angle(vec) ) < max_angle_diff_rad):
                        allowable_points.append(found)
            
            mean = mean_weighted_vector( list(map( lambda a:(vecs[a[1]],(a[2]+0.0000001)**-smoothing_exponent) , allowable_points )))
            if ( mean.length <= 0.001 ):
                mean = nearest_vec
            append_hsv_to_buf( buffer, (vec_to_hue( mean ), 1.0, 1.0 ))
            
            
                
            """
            (co, index, dist) = kd.find((x,y,0))
            append_hsv_to_buf( buffer, (vec_to_hue(vecs[index]),1.0,1.0) )
            #write_pixel( img, (x,y), colors[index] )
            """
            
            
    img.pixels = buffer

def test():      
    image = bpy.data.images['voronoi_2d_small']
    dims = image.size
    points = [ (.25, .26,0), ( .76, .25,0), ( .755, .755,0), ( .26, .75,0) ]
    vecs = [ Vector((-1,-1.01,0.0)), Vector((1,-1.02,0)), Vector((1.03,1,0)), Vector((-1,1.04,0)) ]
    colors = [ (1,1,1), (0.66,1,1), (0.33,1,1) ]

    rand_points = []
    rand_colors = []
    rand_vecs = []
    num_points = 12

    for i in range(0, num_points):
        rand_points.append( (random.uniform(0, 1), random.uniform(0, 1), 0) )
        rand_colors.append( (random.random(), 1, 1) )
        rand_vecs.append( Vector( (random.uniform(-1,1), random.uniform(-1,1), 0.0 ) ) )
        
    render_voronoi( image, rand_points, rand_vecs, 6, 20.0, 45.0 )
    
#test()