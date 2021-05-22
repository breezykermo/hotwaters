from bpy import context, data, ops
from mathutils import Euler, Matrix, Quaternion, Vector

ops.curve.primitive_bezier_circle_add(enter_editmode=False)
curve = context.active_object
curve.name = 'Heart Curve'
bez_points = curve.data.splines[0].bezier_points

for bez_point in bez_points:
    bez_point.handle_left_type = 'FREE'
    bez_point.handle_right_type = 'FREE'

# Left point.
bez_points[0].co = Vector((-1.0, 0.3, 0.0))
bez_points[0].handle_left = Vector((-1.0, -0.25, 0.0))
bez_points[0].handle_right = Vector((-1.0, 1.0, 0.0))

# Top-middle point.
bez_points[1].co = Vector((0.0, 0.5, 0.0))
bez_points[1].handle_left = Vector((0.0, 1.0, 0.0))
bez_points[1].handle_right = Vector((0.0, 1.0, 0.0))

# Right point.
bez_points[2].co = Vector((1.0, 0.3, 0.0))
bez_points[2].handle_left = Vector((1.0, 1.0, 0.0))
bez_points[2].handle_right = Vector((1.0, -0.25, 0.0))

# Bottom point.
bez_points[3].co = Vector((0.0, -1.0, 0.0))
bez_points[3].handle_left = Vector((0.5, -0.5, 0.0))
bez_points[3].handle_right = Vector((-0.5, -0.5, 0.0))

## Convert curve to mesh
ops.object.convert(target='MESH', keep_original=True)

heart_mesh = context.active_object
heart_mesh.name = 'Heart Mesh'

ops.object.mode_set(mode='EDIT')
ops.mesh.select_all(action='SELECT')

ops.mesh.edge_face_add()

ops.mesh.quads_convert_to_tris(ngon_method='CLIP')

ops.mesh.symmetrize(direction='NEGATIVE_X', threshold=0.0001)

ops.mesh.select_all(action='SELECT')
ops.mesh.tris_convert_to_quads(face_threshold=1.396264, shape_threshold=1.396264)
