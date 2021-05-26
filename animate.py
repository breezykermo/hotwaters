import bpy
import json
from datetime import datetime, timedelta
from bpy import context, data, ops
from mathutils import Vector
from math import floor
from random import randint

DROPBOX_PREFIX = "/home/lachie"
SCRIPTS_PATH = DROPBOX_PREFIX + "/Dropbox (Brown)/blender/blender-scripts/"
FONT_PATH =  DROPBOX_PREFIX + "/Dropbox (Brown)/blender/slowboil/union_regular.otf"

with open(SCRIPTS_PATH + "ships.json", "r") as f:
    SHIPS = json.load(f)

with open(SCRIPTS_PATH + "ports.json", "r") as f:
    PORTS = json.load(f)

def warp(port):
    port["display_name"] = port["Name"]
    if port["Name"] == "Napier":
        port["Latitude"] = port["Latitude"] - 60.5
    if port["Name"] == "El Aaiun":
        port["display_name"] =  "El Aaiun, Western Sahara"
        port["Latitude"] = port["Latitude"] + 10
    if port["Name"] == "Taranaki":
        port["Latitude"] = port["Latitude"] + 2.5
    if port["Name"] == "Port Elizabeth":
        port["display_name"] =  "Port Elizabeth, South Africa"
        port["Latitude"] = port["Latitude"] + 35


    return port
PORTS = [warp(x) for x in PORTS]

def gs(): return bpy.context.selected_objects[0]
def get_object(name): return bpy.context.scene.objects.get(name)
def select_object(o): o.select_set(True)
def get_lat_from_port(port): return port[0]
def set_hide(obj, vl):
    obj.hide_viewport = vl
    obj.hide_render = vl

w = 1 # weight
START_DATE = datetime.strptime('2011-10-01T12:00:00.000Z', '%Y-%m-%dT%H:%M:%S.000Z')
END_DATE = datetime.strptime('2021-06-01T12:00:00.000Z', '%Y-%m-%dT%H:%M:%S.000Z')
LENGTH_OF_ANIMATION_IN_FRAMES = 250

DATE_ARRAY = [START_DATE+timedelta(days=x) for x in range((END_DATE-START_DATE).days)]
FIRST_FRAME = 1
TIME_MULTIPLIER = 20
WHITE_MAT = bpy.data.materials.get("White")
FRAGMENTS_MAT = bpy.data.materials.get("Fragments")
PORTS_VECTORS = {}
SHIP_MATERIALS = {}
PORT_MATERIALS = {}

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
    return DATE_ARRAY.index(value) * TIME_MULTIPLIER

LAST_FRAME = len(DATE_ARRAY) * TIME_MULTIPLIER
print("Last frame is: " + str(LAST_FRAME))

def get_date_from_keyframe(frame):
    distance_along = frame / LAST_FRAME
    nearest_idx = floor(len(DATE_ARRAY) * distance_along)
    return DATE_ARRAY[nearest_idx].strftime("%b %Y")

UNION_FONT = bpy.data.fonts.load(FONT_PATH)

def create_text(name, location, scale=(2,2,2), hidden=False):
    bpy.data.curves.new(type="FONT",name=name).body = name
    font_obj = bpy.data.objects.new("Font Object", bpy.data.curves[name])
    bpy.context.scene.collection.objects.link(font_obj)
    font_obj.name = name
    font_obj.location = location
    font_obj.scale = scale
    font_obj.data.font = UNION_FONT
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

def create_trail(start_location, end_location, inverse=False):
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
    end_pt.handle_left = Vector((end_pt.co.x + randint(-2, 2), end_pt.co.y - ((3 + randint(1,8)) if not inverse else (-3 - randint(1,8))), end_pt.co.z))
    end_pt.handle_right = Vector((end_pt.co.x, end_pt.co.y + 5, end_pt.co.z))
    ops.object.mode_set(mode='OBJECT')
    return curve

def get_one_yr_in_frames():
    magic_date = datetime(2012, 10, 1, 12, 0)
    one_yr_in_frames = DATE_ARRAY.index(magic_date) * TIME_MULTIPLIER
    return one_yr_in_frames

def animate_ship_with_trail(ship, start_location, end_location, anim_start, anim_end, should_stall=False):
    trail_curve = create_trail(start_location, end_location, inverse=should_stall)
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

    hide_frame = anim_end if not should_stall else (anim_end + get_one_yr_in_frames())

    ship.keyframe_insert(data_path="hide_viewport", frame=(hide_frame))
    ship.keyframe_insert(data_path="hide_render", frame=(hide_frame))

    follow_path.keyframe_insert(data_path='offset_factor', frame=(anim_end))

    # animate bevel factor along path
    # ops.curve.primitive_bezier_circle_add(location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0))
    # tube = get_object('ReferenceTube')
    # trail_curve.data.bevel_mode = 'OBJECT'
    # trail_curve.data.bevel_object = tube
    #
    set_hide(trail_curve, True)
    trail_curve.keyframe_insert(data_path='hide_viewport', frame=(FIRST_FRAME))
    trail_curve.keyframe_insert(data_path='hide_render', frame=(FIRST_FRAME))
    # trail_curve.data.bevel_factor_end = 0.0
    set_hide(trail_curve, False)
    # b1_kf = trail_curve.data.keyframe_insert(data_path='bevel_factor_end', frame=(anim_start))
    trail_curve.keyframe_insert(data_path='hide_viewport', frame=(anim_start))
    trail_curve.keyframe_insert(data_path='hide_render', frame=(anim_start))
    # trail_curve.data.bevel_factor_end= 1.0
    set_hide(trail_curve, True)
    # b2_kf = trail_curve.data.keyframe_insert(data_path='bevel_factor_end', frame=(anim_end))
    trail_curve.keyframe_insert(data_path='hide_viewport', frame=(hide_frame))
    trail_curve.keyframe_insert(data_path='hide_render', frame=(hide_frame))

    # TODO: work out how to do this
    # for fc in trail_curve.animation_data.action.fcurves:
    #     fc.extrapolation = 'LINEAR' # Set extrapolation type

def get_color(mat):
    return mat.node_tree.nodes["Emission"].inputs[0].default_value

def keyframe_color(mat, vl, frame):
    mat.node_tree.nodes["Emission"].inputs[0].default_value = vl
    ei = mat.node_tree.nodes["Emission"].inputs[0]
    ei.keyframe_insert(data_path='default_value', frame=frame)


glows = [0, 48, 96, 144]
white_color = (1.0, 1.0, 1.0, 1.0)
light_color = (1.0, 1.0, 0.5, 1.0)

def light_up_ports(ports, start_frame):
    print("Lighting up " + str(ports) + " at frame " + str(start_frame))

    anim_starts = [t+start_frame-12 for t in glows]
    anim_mids = [t+start_frame+24 for t in glows]
    anim_ends = [t+start_frame+72 for t in glows]

    for idx, port in enumerate(ports):
        original_color = get_color(PORT_MATERIALS[port])
        keyframe_color(PORT_MATERIALS[port], white_color, anim_starts[idx])
        keyframe_color(PORT_MATERIALS[port], light_color, anim_mids[idx])
        keyframe_color(PORT_MATERIALS[port], white_color, anim_ends[idx])


def set_sail(ship):
    anim_start = floor(get_keyframe_no(ship['Departure']))
    anim_end = floor(get_keyframe_no(ship['Arrival']))
    start_location = PORTS_VECTORS['El Aaiun']
    ship_first_port = ship['Port Destination s'][0]
    end_location = PORTS_VECTORS[ship_first_port]


    new_ship = create_text(ship['Name'], start_location, scale=(1,1,1), hidden=True)

    SHIP_MATERIALS[ship['Name']] = WHITE_MAT.copy()
    assign_material(SHIP_MATERIALS[ship['Name']], new_ship)
    should_stall = False

    if ship['Name'] == 'NM Cherry Blossom':
        end_location = Vector((end_location.x, end_location.y + 1, end_location.z))
        should_stall = True

    context.scene.frame_set(FIRST_FRAME)

    animate_ship_with_trail(new_ship, start_location, end_location, anim_start, anim_end, should_stall=should_stall)
    light_up_ports(ship["Port Destination s"], anim_end)


def add_port_name(port):
    loc = ship_tmpl_from_lat(port['Latitude']).location.copy()
    loc.y = loc.y - 1.5
    if (port["Name"] == "El Aaiun"):
        loc.x = loc.x - 7
    if (port["Name"] == "Whāngarei"):
        loc.x = loc.x + 2
    if (port["Name"] == "Port Elizabeth"):
        loc.y = loc.y + 2.5

    new_port = create_text(port["display_name"], loc, scale=(0.8,0.8,0.8))
    PORT_MATERIALS[port['Name']] = WHITE_MAT.copy()
    assign_material(PORT_MATERIALS[port['Name']], new_port)
    PORTS_VECTORS[port["Name"]] = loc

def animate_ships():
    for port in PORTS:
        add_port_name(port)

    for ship in SHIPS:
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
    anim_curve.scale = (0.6, 0.6, 0.6)
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

