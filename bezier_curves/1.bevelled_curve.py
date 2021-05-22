from bpy import context, data, ops

ops.curve.primitive_bezier_circle_add(radius=1.0,
                                      location=(0.0, 0.0, 0.0),
                                      enter_editmode=True)

ops.curve.subdivide(number_cuts=16)

ops.transform.vertex_random(offset=1.0, uniform=0.1, normal=0.0, seed=0)

ops.transform.resize(value=(2.0, 2.0, 3.0))

ops.object.mode_set(mode='OBJECT')

obj_data = context.active_object.data
obj_data.fill_mode = 'FULL'
obj_data.extrude = 0.125
obj_data.bevel_depth = 0.125
obj_data.resolution_u = 20
obj_data.render_resolution_u = 32

## create a control curve
ops.curve.primitive_bezier_circle_add(radius=0.25, enter_editmode=True)
ops.curve.subdivide(number_cuts=4)
ops.transform.vertex_random(offset=1.0, uniform=0.1, normal=1.0, seed=0)
bevel_control = context.active_object
bevel_control.data.name = bevel_control.name = 'Bevel Control'

# Set the main curve's bevel control to the bevel control curve.
obj_data.bevel_object = bevel_control
ops.object.mode_set(mode='OBJECT')

# Create taper control curve.
ops.curve.primitive_bezier_curve_add(enter_editmode=True)
ops.curve.subdivide(number_cuts=3)
ops.transform.vertex_random(offset=1.0, uniform=0.1, normal=1.0, seed=0)
taper_control = context.active_object
taper_control.data.name = taper_control.name = 'Taper Control'

# Set the main curve's taper control to the taper control curve.
obj_data.taper_object = taper_control
ops.object.mode_set(mode='OBJECT')
