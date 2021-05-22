from bpy import context, data, ops

ops.curve.primitive_bezier_curve_add(enter_editmode=True)
ops.curve.subdivide(number_cuts=1)

