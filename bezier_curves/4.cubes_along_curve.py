from bpy import context, data, ops
from mathutils import geometry

ops_mesh = ops.mesh

count = 16

ops.curve.primitive_bezier_curve_add(enter_editmode=True)
ops.transform.vertex_random(offset=1.0, uniform=0.1, normal=0.01, seed=0)
ops.object.mode_set(mode='OBJECT')

bez_curve = context.active_object
bez_points = bez_curve.data.splines[0].bezier_points

points_on_curve = geometry.interpolate_bezier(
    bez_points[0].co,
    bez_points[0].handle_right,
    bez_points[1].handle_left,
    bez_points[1].co,
    count,
)

ops.object.empty_add(type='PLAIN_AXES', location=bez_curve.location)
group = context.active_object

cube_rad = 0.5 / count
for point in points_on_curve:
    ops_mesh.primitive_cube_add(size=cube_rad, location=point)
    cube = context.active_object
    cube.parent = group
