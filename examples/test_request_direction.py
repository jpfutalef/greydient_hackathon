import folium
import requests
from openrouteservice import client
from shapely import geometry
from shapely.geometry import Point, LineString, Polygon, MultiPolygon
from hackaton_directions import *

# Set up the connection to the openrouteservice api
api_key = 'your-API-key-here'  # Individual api key
ors = client.Client(key=api_key)  # Create client with api key

# get data with the road works from Rostok 
url = 'https://geo.sv.rostock.de/download/opendata/baustellen/baustellen.json'
rostock_json = requests.get(url).json()  # Get data as JSON

# chek the json has been correctly parsed
rostock_json

# get the coordinates of the road interruptions from the Rostok JSON
site_coords=[]
for site_data in rostock_json['features']:
    site_coords.append(site_data['geometry']['coordinates'])

# some plotting on a map
map_params = {'tiles': 'OpenStreetMap',
              'location': ([54.13207, 12.101612]),
              'zoom_start': 12}
map1 = folium.Map(**map_params) 
sites_poly = []
for coord in site_coords:
    folium.features.Marker(list(reversed(coord)),
                        popup='Construction point<br>{0}'.format(coord)).add_to(map1)

map1.save("map1.html")

# Get the driving directions by car given a start point and end point

startpoint = [12.115737, 54.084774]
endpoint = [12.072063, 54.103684]
route, summary = driving_directions(ors,startpoint,endpoint)

# first output is a list of all the coordinates to identify the road to be taken on the map, second
# output gives a summary of the route (distance in meters and duration in seconds)
print(summary)

# just some plots of the route on a map

# set the centerpoint on the route as the new midpoint of the map (pass y before x)
map_params.update({'location': ([(startpoint[1]+endpoint[1])/2,
                                 (startpoint[0]+endpoint[0])/2] ),
                   'zoom_start': 13})
map2 = folium.Map(**map_params)

# add the route to the map. Again, folium need to flip x and y in coordinates.
folium.PolyLine(locations=[(y, x) for x, y in route], 
                name='Route without construction sites',
                color='#FF0000',
                weight = 4,
                overlay=True).add_to(map2)

# pass the list of all the road works in addition to the start and end point to the method
# that provides directions avoiding the roadworks

route, summary = driving_directions_avoiding_points(ors,startpoint,endpoint,site_coords)

# compare the new summary with the original
print(summary)

# add the new route to the map.
folium.PolyLine(locations=[(y, x) for x, y in route], 
                name='Route avoiding construction sites',
                color='#00FF00',
                weight = 4,
                overlay=True).add_to(map2)

map2.save("map2.html")
