import bpy
import json
from datetime import datetime

with open("/Users/lachlankermode/Desktop/blender/data/ships.json", "r") as f:
    SHIPS = json.load(f)

with open("/Users/lachlankermode/Desktop/blender/data/ports.json", "r") as f:
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

def create_ship(name):
    location = get_port_template(START_PORT).location
    bpy.data.curves.new(type="FONT",name=name).body = name
    font_obj = bpy.data.objects.new("Font Object", bpy.data.curves[name])
    bpy.context.scene.collection.objects.link(font_obj)
    font_obj.name = name
    font_obj.location = location
    font_obj.scale = (0.1, 0.1, 0.1)
    return font_obj

def get_port_template(port):
    lat = get_lat_from_port(port)
    dg = str(int((lat + 90.0) * 2)).zfill(3)
    tmpl = get_object('Ship.' + dg)
    return tmpl

def ship_set_sail(port, name):
    ship = create_ship(name)
    tmpl = get_port_template(port)
    select_object(tmpl)
    # TODO: set sail...

for ship in SHIPS:
    ship['ports'] = [port_map[x] for x in ship['Port Destination s']]
    if ship['Departure'] is not None:
        ship['Departure'] = datetime.strptime(ship['Departure'], '%Y-%m-%dT%H:%M:%S.000Z')
    if ship['Arrival'] is not None:
        ship['Arrival'] = datetime.strptime(ship['Arrival'], '%Y-%m-%dT%H:%M:%S.000Z')
    print(ship)
    # ship_set_sail(ship['ports'][0], ship['Name'])

