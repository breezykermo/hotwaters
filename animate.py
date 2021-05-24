import bpy
import json
from datetime import datetime, timedelta
from bpy import context, data, ops
from mathutils import Vector
from math import floor
from random import randint

SCRIPTS_PATH = "/Users/lachlankermode/code/uoa/blender-scripts/"

with open(SCRIPTS_PATH + "ships.json", "r") as f:
    SHIPS = json.load(f)

with open(SCRIPTS_PATH + "ports.json", "r") as f:
    PORTS = json.load(f)

def warp(port):
    if port["Name"] == "Napier":
        port["Latitude"] = port["Latitude"] - 60.5
    if port["Name"] == "El Aaiun":
        port["Latitude"] = port["Latitude"] + 10
    return port
PORTS = [warp(x) for x in PORTS]

port_map = {}
for port in PORTS:
    port_map[port['Name']] = (port['Latitude'], port['Longitude'])

def gs(): return bpy.context.selected_objects[0]
def get_object(name): return bpy.context.scene.objects.get(name)
def select_object(o): o.select_set(True)
def get_lat_from_port(port): return port[0]
def set_hide(obj, vl):
    obj.hide_viewport = vl
    obj.hide_render = vl

w = 1 # weight
START_PORT = port_map['El Aaiun']
START_DATE = datetime.strptime('2011-01-01T12:00:00.000Z', '%Y-%m-%dT%H:%M:%S.000Z')
END_DATE = datetime.strptime('2020-01-01T12:00:00.000Z', '%Y-%m-%dT%H:%M:%S.000Z')
LENGTH_OF_ANIMATION_IN_FRAMES = 250

DATE_ARRAY = [START_DATE+timedelta(days=x) for x in range((END_DATE-START_DATE).days)]
FIRST_FRAME = 1
LAST_FRAME = 9500
WHITE_MAT = bpy.data.materials.get("White")
FRAGMENTS_MAT = bpy.data.materials.get("Fragments")

def assign_material(mat, ob):
    if ob.data.materials:
        ob.data.materials[0] = mat
    else:
        ob.data.materials.append(mat)

def create_cylinder():
    bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=2, enter_editmode=False, align='WORLD', location=(0,0,0), scale=(1, 1, 1))
    c = gs()
    c.rotation_euler[0] = 1.5708
    bpy.ops.object.editmode_toggle()

def make_polyline(objname, curvename, cList):
    curvedata = bpy.data.curves.new(name=curvename, type='CURVE')
    curvedata.dimensions = '3D'

    objectdata = bpy.data.objects.new(objname, curvedata)
    objectdata.location = (0,0,0) #object origin
    bpy.context.scene.collection.objects.link(objectdata)

    polyline = curvedata.splines.new('POLY')
    polyline.points.add(len(cList)-1)
    for num in range(len(cList)):
        x, y, z = cList[num]
        polyline.points[num].co = (x, y, z, w)

    return polyline

def bevel_polyline(objname, bevel_objname):
    line = get_object(objname)
    line.data.bevel_mode = 'OBJECT'
    line.data.bevel_object = bpy.data.objects[bevel_objname]

def get_keyframe_no(date):
    if date is None: return -1
    value = min(DATE_ARRAY, key=lambda d: abs(d - date))
    return DATE_ARRAY.index(value) * 2.5

def get_date_from_keyframe(frame):
    distance_along = frame / LAST_FRAME
    print(distance_along)
    nearest_idx = floor(len(DATE_ARRAY) * distance_along)
    print(nearest_idx)
    return DATE_ARRAY[nearest_idx].strftime("%b %Y")

def create_text(name, location, scale=(2,2,2), hidden=False):
    bpy.data.curves.new(type="FONT",name=name).body = name
    font_obj = bpy.data.objects.new("Font Object", bpy.data.curves[name])
    bpy.context.scene.collection.objects.link(font_obj)
    font_obj.name = name
    font_obj.location = location
    font_obj.scale = scale
    if hidden:
        set_hide(font_obj, True)
        font_obj.keyframe_insert(data_path="hide_viewport", frame=FIRST_FRAME)
        font_obj.keyframe_insert(data_path="hide_render", frame=FIRST_FRAME)

    assign_material(WHITE_MAT, font_obj)
    return font_obj

def ship_tmpl_from_lat(lat):
    dg = int((lat + 90.0) * 6) - 70
    dg = str(dg % 360).zfill(3)
    tmpl = get_object('Ship.' + dg)
    return tmpl

def get_port_template(port):
    lat = get_lat_from_port(port)
    return ship_tmpl_from_lat(lat)

def animate_curve_attempt_1(start_location, end_location, anim_start, anim_end):
    ops.curve.primitive_nurbs_path_add(enter_editmode=True, align='WORLD')
    ops.curve.subdivide(number_cuts=1)
    ops.object.mode_set(mode='OBJECT')
    curve = context.active_object
    points = curve.data.splines[0].points
    fst = points[0]
    lst = points[len(points)-1]
    # TODO: work out how to remove middle verts...
    fst.co = Vector((start_location.x, start_location.y, start_location.z, 0))
    lst.co = Vector((end_location.x, end_location.y, end_location.z, 0))
    curve.hide_viewport = True
    curve.hide_render= True
    fst.keyframe_insert(data_path='co', frame=FIRST_FRAME)
    fst.keyframe_insert(data_path='co', frame=anim_end)
    lst.keyframe_insert(data_path='co', frame=FIRST_FRAME)
    lst.keyframe_insert(data_path='co', frame=anim_end)
    curve.keyframe_insert(data_path='hide_viewport', frame=FIRST_FRAME)
    curve.keyframe_insert(data_path='hide_viewport', frame=anim_end)
    curve.keyframe_insert(data_path='hide_render', frame=FIRST_FRAME)
    curve.keyframe_insert(data_path='hide_render', frame=anim_end)

    # line extending
    # line_name = ship["Name"] + "_line"
    # curve_name = ship["Name"] + "_curve"
    # polyline = make_polyline(line_name, curve_name, [start_location, start_location])
    # bevel_polyline(line_name, "A_TemplateBezier")

    curve.hide_viewport = False
    curve.hide_render= False
    lst.co = start_location.xyzz
    curve.keyframe_insert(data_path='hide_viewport', frame=anim_start)
    curve.keyframe_insert(data_path='hide_render', frame=anim_start)
    fst.keyframe_insert(data_path='co', frame=anim_start)
    lst.keyframe_insert(data_path='co', frame=anim_start)

def animate_ship_attempt_1(new_ship, start_location, end_location, anim_start, anim_end):
    set_hide(new_ship, False)
    new_ship.keyframe_insert(data_path="hide_viewport", frame=(anim_start))
    new_ship.keyframe_insert(data_path="hide_render", frame=(anim_start))
    new_ship.keyframe_insert(data_path='location', frame=(anim_start))

    set_hide(new_ship, True)
    new_ship.location = end_location
    new_ship.keyframe_insert(data_path="hide_viewport", frame=anim_end)
    new_ship.keyframe_insert(data_path="hide_render", frame=anim_end)
    new_ship.keyframe_insert(data_path="location", frame=anim_end)

def create_trail(start_location, end_location):
    ops.curve.primitive_bezier_curve_add(enter_editmode=True, align='WORLD')
    curve = context.active_object
    curve.data.resolution_u = 60
    bez_points = curve.data.splines[0].bezier_points

    for bez_point in bez_points:
        bez_point.handle_left_type = 'FREE'
        bez_point.handle_right_type = 'FREE'

    start_pt = bez_points[0]
    start_pt.co = start_location
    start_pt.handle_left = Vector((start_pt.co.x, start_pt.co.y + 5, start_pt.co.z))
    start_pt.handle_right = Vector((start_pt.co.x + randint(-2, 2), start_pt.co.y - 3, start_pt.co.z))

    end_pt = bez_points[1]
    end_pt.co = end_location
    end_pt.handle_left = Vector((end_pt.co.x + randint(-2, 2), end_pt.co.y - (3 + randint(1,8)), end_pt.co.z))
    end_pt.handle_right = Vector((end_pt.co.x, end_pt.co.y + 5, end_pt.co.z))
    ops.object.mode_set(mode='OBJECT')
    return curve

def animate_ship_with_trail(ship, start_location, end_location, anim_start, anim_end):
    trail_curve = create_trail(start_location, end_location)
    assign_material(FRAGMENTS_MAT, trail_curve)

    # animate ship along path
    ship.location = (0.0, 0.0, 0.0)
    follow_path = ship.constraints.new(type='FOLLOW_PATH')
    follow_path.target = trail_curve
    follow_path.forward_axis = 'TRACK_NEGATIVE_Z'
    follow_path.up_axis = 'UP_Y'
    follow_path.use_fixed_location = True

    follow_path.offset_factor = 0.0
    set_hide(ship, False)
    ship.keyframe_insert(data_path="hide_viewport", frame=(anim_start))
    ship.keyframe_insert(data_path="hide_render", frame=(anim_start))
    ship.keyframe_insert(data_path="location", frame=(anim_start))
    follow_path.keyframe_insert(data_path='offset_factor', frame=(anim_start))

    follow_path.offset_factor = 1.0
    set_hide(ship, True)
    ship.keyframe_insert(data_path="hide_viewport", frame=(anim_end))
    ship.keyframe_insert(data_path="hide_render", frame=(anim_end))
    follow_path.keyframe_insert(data_path='offset_factor', frame=(anim_end))

    # animate bevel factor along path
    # ops.curve.primitive_bezier_circle_add(location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0))
    tube = get_object('ReferenceTube')
    trail_curve.data.bevel_mode = 'OBJECT'
    trail_curve.data.bevel_object = tube

    set_hide(trail_curve, True)
    trail_curve.keyframe_insert(data_path='hide_viewport', frame=(FIRST_FRAME))
    trail_curve.keyframe_insert(data_path='hide_render', frame=(FIRST_FRAME))
    trail_curve.data.bevel_factor_end = 0.0
    set_hide(trail_curve, False)
    b1_kf = trail_curve.data.keyframe_insert(data_path='bevel_factor_end', frame=(anim_start))
    trail_curve.keyframe_insert(data_path='hide_viewport', frame=(anim_start))
    trail_curve.keyframe_insert(data_path='hide_render', frame=(anim_start))
    trail_curve.data.bevel_factor_end= 1.0
    set_hide(trail_curve, True)
    b2_kf = trail_curve.data.keyframe_insert(data_path='bevel_factor_end', frame=(anim_end))
    trail_curve.keyframe_insert(data_path='hide_viewport', frame=(anim_end))
    trail_curve.keyframe_insert(data_path='hide_render', frame=(anim_end))

    # TODO: change the trail_curve bevel_factor_end keyframes to linear to match up

def set_sail(ship):
    anim_start = get_keyframe_no(ship['Departure'])
    anim_end = get_keyframe_no(ship['Arrival'])
    anim_end = anim_start + 200 if anim_end < 0 else anim_end
    start_location = get_port_template(START_PORT).location
    end_location = Vector((0,0,0)) if anim_end < 0 else get_port_template(ship['ports'][0]).location

    new_ship = create_text(ship['Name'], start_location, scale=(1,1,1), hidden=True)
    assign_material(WHITE_MAT, new_ship)

    # animate_ship_attempt_1(new_ship, start_location, end_location, anim_start, anim_end)
    # animate_curve_attempt_1(start_location, end_location, anim_start, anim_end)

    context.scene.frame_set(FIRST_FRAME)
    animate_ship_with_trail(new_ship, start_location, end_location, anim_start, anim_end)

def add_port_name(port):
    loc = ship_tmpl_from_lat(port['Latitude']).location.copy()
    loc.y = loc.y - 1.5
    if (port["Name"] == "El Aaiun"):
        loc.x = loc.x - 2.5
    if (port["Name"] == "Whangarei /Northport"):
        loc.y = loc.y - 1

    create_text(port["Name"], loc, scale=(0.8,0.8,0.8))

def animate_ships():
    for port in PORTS:
        add_port_name(port)

    for ship in SHIPS:
        ship['ports'] = [port_map[x] for x in ship['Port Destination s']]

        if ship['Departure'] is not None:
            ship['Departure'] = datetime.strptime(ship['Departure'], '%Y-%m-%dT%H:%M:%S.000Z')
        if ship['Arrival'] is not None:
            ship['Arrival'] = datetime.strptime(ship['Arrival'], '%Y-%m-%dT%H:%M:%S.000Z')

        set_sail(ship)

def animate_clock():
    # setup anim curve
    ops.curve.primitive_bezier_circle_add(enter_editmode=True)
    ops.curve.subdivide(number_cuts=((360 // 4) - 1))
    anim_curve = context.active_object
    anim_curve.scale = (0.8, 0.8, 0.8)
    bez_points = anim_curve.data.splines[0].bezier_points
    for i in range(0, len(bez_points), 1):
        pt = bez_points[i]
        pt.co = get_object(f"Ship.{str(i+1).zfill(3)}").location
    ops.object.mode_set(mode='OBJECT')

    panel = get_object('ClockPanel_datetext')

    # follow path constraint
    follow_path = panel.constraints.new(type='FOLLOW_PATH')
    follow_path.target = anim_curve
    follow_path.forward_axis = 'TRACK_NEGATIVE_Z'
    follow_path.up_axis = 'UP_Y'
    follow_path.use_fixed_location = True

    follow_path.offset_factor = 0.0
    follow_path.keyframe_insert(data_path='offset_factor', frame=(FIRST_FRAME))
    follow_path.offset_factor = 1.0
    follow_path.keyframe_insert(data_path='offset_factor', frame=(LAST_FRAME))

    # duplicate as line
    # clock_line = anim_curve.copy()
    # clock_line.data = anim_curve.data.copy()
    # context.scene.collection.objects.link(clock_line)
    # clock_line.name = 'ClockLoopLine'
    # tube = get_object('ReferenceTube')
    # clock_line.data.bevel_mode = 'OBJECT'
    # clock_line.data.bevel_object = tube
    # clock_line.data.bevel_factor_end= 1.0
    # clock_line.data.resolution_u = 500
    # clock_line.scale = (0.72, 0.72, 0.72)
    # assign_material(WHITE_MAT, clock_line)



def update_clock(self):
    frame = bpy.context.scene.frame_current
    datetext = get_object('ClockPanel_datetext')
    datetext.data.body = get_date_from_keyframe(frame)

bpy.app.handlers.frame_change_post.append(update_clock)

# automate animations
animate_ships()
animate_clock()

