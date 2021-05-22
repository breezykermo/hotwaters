import bpy
import json
from datetime import datetime, timedelta
from bpy import context, data, ops
from mathutils import Vector

SCRIPTS_PATH = "/home/lachie/Dropbox (Brown)/blender/blender-scripts/"

with open(SCRIPTS_PATH + "ships.json", "r") as f:
    SHIPS = json.load(f)

with open(SCRIPTS_PATH + "ports.json", "r") as f:
    PORTS = json.load(f)

port_map = {}
for port in PORTS:
    port_map[port['Name']] = (port['Latitude'], port['Longitude'])

def gs(): return bpy.context.selected_objects[0]
def get_object(name): return bpy.context.scene.objects.get(name)
def select_object(o): o.select_set(True)
def get_lat_from_port(port): return port[0]

w = 1 # weight
START_PORT = port_map['El Aaiun']
START_DATE = datetime.strptime('2011-01-01T12:00:00.000Z', '%Y-%m-%dT%H:%M:%S.000Z')
END_DATE = datetime.strptime('2020-01-01T12:00:00.000Z', '%Y-%m-%dT%H:%M:%S.000Z')
LENGTH_OF_ANIMATION_IN_FRAMES = 250

DATE_ARRAY = [START_DATE+timedelta(days=x) for x in range((END_DATE-START_DATE).days)]
FIRST_FRAME = 1
LAST_FRAME = len(DATE_ARRAY)

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

def get_closest_date_idx(date):
    if date is None: return -1
    value = min(DATE_ARRAY, key=lambda d: abs(d - date))
    return DATE_ARRAY.index(value)

def create_text(name, location, scale=(2,2,2)):
    bpy.data.curves.new(type="FONT",name=name).body = name
    font_obj = bpy.data.objects.new("Font Object", bpy.data.curves[name])
    bpy.context.scene.collection.objects.link(font_obj)
    font_obj.name = name
    print(location)
    font_obj.location = location
    font_obj.scale = scale
    return font_obj

def ship_tmpl_from_lat(lat):
    dg = int((lat + 90.0) * 2) + 120
    dg = str(dg % 360).zfill(3)
    tmpl = get_object('Ship.' + dg)
    return tmpl

def get_port_template(port):
    lat = get_lat_from_port(port)
    return ship_tmpl_from_lat(lat)

def set_sail(ship):
    anim_start = get_closest_date_idx(ship['Departure'])
    anim_end = get_closest_date_idx(ship['Arrival'])

    # start keyframes
    new_ship = create_text(ship['Name'], get_port_template(START_PORT).location)
    start_location = get_port_template(START_PORT).location
    if anim_start > 0:
        new_ship.keyframe_insert(data_path="hide_viewport", frame=(anim_start))
        new_ship.keyframe_insert(data_path='location', frame=(anim_start))

    # end keyframes
    new_ship.hide_viewport = True
    end_location = get_port_template(ship['ports'][0]).location
    new_ship.location = end_location
    new_ship.keyframe_insert(data_path="hide_viewport", frame=anim_end)
    new_ship.keyframe_insert(data_path="location", frame=anim_end)

    # hide to begin with
    new_ship.keyframe_insert(data_path="hide_viewport", frame=FIRST_FRAME)

    # line extending
    # line_name = ship["Name"] + "_line"
    # curve_name = ship["Name"] + "_curve"
    # polyline = make_polyline(line_name, curve_name, [start_location, start_location])
    # bevel_polyline(line_name, "A_TemplateBezier")

    if False:
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
        fst.keyframe_insert(data_path='co', frame=FIRST_FRAME)
        fst.keyframe_insert(data_path='co', frame=anim_end)
        lst.keyframe_insert(data_path='co', frame=FIRST_FRAME)
        lst.keyframe_insert(data_path='co', frame=anim_end)
        curve.keyframe_insert(data_path='hide_viewport', frame=FIRST_FRAME)
        curve.keyframe_insert(data_path='hide_viewport', frame=anim_end)

        curve.hide_viewport = False
        lst.co = start_location.xyzz
        curve.keyframe_insert(data_path='hide_viewport', frame=anim_start)
        fst.keyframe_insert(data_path='co', frame=anim_start)
        lst.keyframe_insert(data_path='co', frame=anim_start)

def add_port_name(port):
    loc = ship_tmpl_from_lat(port['Latitude']).location.copy()
    loc.y = loc.y - 1
    if (port["Name"] == "El Aaiun"):
        loc.x = loc.x - 5
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

        # set_sail(ship)

animate_ships()


