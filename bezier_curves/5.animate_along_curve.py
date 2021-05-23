from bpy import context, data, ops

model = context.active_object

ops.curve.primitive_bezier_curve_add(location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0))
camera_path = context.active_object
camera_path.name = camera_path.data.name = 'Camera Path'

ops.object.camera_add(location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0))
camera = context.active_object

scene = context.scene

# follow path constraint
follow_path = camera.constraints.new(type='FOLLOW_PATH')
follow_path.target = camera_path
follow_path.forward_axis = 'TRACK_NEGATIVE_Z'
follow_path.up_axis = 'UP_Y'
follow_path.use_fixed_location = True

# tracking constraint
look_at = camera.constraints.new(type='TRACK_TO')
look_at.target = model
look_at.track_axis = 'TRACK_NEGATIVE_Z'
look_at.up_axis = 'UP_Y'

scene.frame_set(scene.frame_start)
follow_path.offset_factor = 0.0
follow_path.keyframe_insert(data_path='offset_factor')

camera_path.location = (0.0, 0.0, 0.0)
camera_path.keyframe_insert(data_path='location')

scene.frame_set(scene.frame_start + (scene.frame_end - scene.frame_start) // 2)
camera_path.location = (0.0, 0.0, 1.0)
camera_path.keyframe_insert(data_path='location')

scene.frame_set(scene.frame_end)
follow_path.offset_factor = 1.0
follow_path.keyframe_insert(data_path='offset_factor')

camera_path.location = (0.0, 0.0, 0.0)
camera_path.keyframe_insert(data_path='location')

fcurves = camera.animation_data.action.fcurves
for fcurve in fcurves:
    for kf in fcurve.keyframe_points:
        kf.interpolation = 'LINEAR'
        kf.interpolation = 'AUTO'
