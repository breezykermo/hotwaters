from bpy import context, data, ops
from math import cos, pi, sin, tan
from random import TWOPI, randint, uniform

ops.curve.primitive_bezier_circle_add(enter_editmode=True)
ops.curve.subdivide(number_cuts=18)

curve = context.active_object

bez_points = curve.data.splines[0].bezier_points

sz = len(bez_points)
print(sz)
i_to_theta = TWOPI / sz
for i in range (0, sz, 1):
    if i % 6 == 0:
        bez_points[i].co.z = 0.5

    if i % 2 == 0:
        bez_points[i].handle_right *= 2.0
        bez_points[i].handle_left *= 0.5
    elif i % 4 == 0:
        bez_points[i].handle_right.z -= 5.0
        bez_points[i].handle_left.z -= 5.0
    else:
        bez_points[i].co *= 0.5

    scalar = 2.0 + 2.0 * cos(i * i_to_theta)

    bez_points[i].co *= scalar

ops.transform.resize(value=(3.0, 3.0, 1.0))
ops.object.mode_set(mode='OBJECT')
ops.object.convert(target='MESH')

skin_mod = curve.modifiers.new(name='Skin', type='SKIN')
subsurf_mod = curve.modifiers.new(name='Subsurf', type='SUBSURF')
stretch_mod = curve.modifiers.new(name='SimpleDeform', type='SIMPLE_DEFORM')

skin_mod.use_smooth_shade = True
subsurf_mod.levels = 3
subsurf_mod.render_levels = 3
stretch_mod.deform_method = 'STRETCH'
stretch_mod.factor = 0.5
