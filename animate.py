import bpy
import json
from datetime import datetime, timedelta

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

START_PORT = port_map['El Aaiun']
START_DATE = datetime.strptime('2011-01-01T12:00:00.000Z', '%Y-%m-%dT%H:%M:%S.000Z')
END_DATE = datetime.strptime('2020-01-01T12:00:00.000Z', '%Y-%m-%dT%H:%M:%S.000Z')
LENGTH_OF_ANIMATION_IN_FRAMES = 250

DATE_ARRAY = [START_DATE+timedelta(days=x) for x in range((END_DATE-START_DATE).days)]
FIRST_FRAME = 1
LAST_FRAME = len(DATE_ARRAY)

def get_closest_date_idx(date):
    if date is None: return -1
    value = min(DATE_ARRAY, key=lambda d: abs(d - date))
    return DATE_ARRAY.index(value)

def create_ship(name):
    location = get_port_template(START_PORT).location
    bpy.data.curves.new(type="FONT",name=name).body = name
    font_obj = bpy.data.objects.new("Font Object", bpy.data.curves[name])
    bpy.context.scene.collection.objects.link(font_obj)
    font_obj.name = name
    font_obj.location = location
    font_obj.scale = (0.2, 0.2, 0.2)
    return font_obj

def get_port_template(port):
    lat = get_lat_from_port(port)
    dg = int((lat + 90.0) * 2) + 160
    dg = str(dg % 360).zfill(3)
    tmpl = get_object('Ship.' + dg)
    return tmpl

for ship in SHIPS:
    ship['ports'] = [port_map[x] for x in ship['Port Destination s']]

    if ship['Departure'] is not None:
        ship['Departure'] = datetime.strptime(ship['Departure'], '%Y-%m-%dT%H:%M:%S.000Z')
    if ship['Arrival'] is not None:
        ship['Arrival'] = datetime.strptime(ship['Arrival'], '%Y-%m-%dT%H:%M:%S.000Z')

    anim_start = get_closest_date_idx(ship['Departure'])
    anim_end = get_closest_date_idx(ship['Arrival'])

    # start keyframes
    new_ship = create_ship(ship['Name'])
    if anim_start > 0:
        new_ship.keyframe_insert(data_path="hide_viewport", frame=(anim_start))
        new_ship.keyframe_insert(data_path='location', frame=(anim_start))

    # end keyframes
    new_ship.hide_viewport = True
    new_ship.location = get_port_template(ship['ports'][0]).location
    new_ship.keyframe_insert(data_path="hide_viewport", frame=anim_end)
    new_ship.keyframe_insert(data_path="location", frame=anim_end)

    # hide to begin with
    new_ship.keyframe_insert(data_path="hide_viewport", frame=FIRST_FRAME)

