
import pyproj
from openrouteservice import client
from shapely import geometry
from shapely.geometry import Point, LineString, Polygon, MultiPolygon

def create_buffer_polygon(point_in, resolution=10, radius=10):
    convert = pyproj.Transformer.from_crs("epsg:4326", 'epsg:32632')  # WGS84 to UTM32N
    convert_back = pyproj.Transformer.from_crs('epsg:32632', "epsg:4326")  # UTM32N to WGS84
    point_in_proj = convert.transform(*point_in)
    point_buffer_proj = Point(point_in_proj).buffer(radius, resolution=resolution)  # 10 m buffer

    # Iterate over all points in buffer and build polygon
    poly_wgs = []
    for point in point_buffer_proj.exterior.coords:
        poly_wgs.append(convert_back.transform(*point))  # Transform back to WGS84

    return poly_wgs

# method to provide directions driving by car given a start and an end position
def driving_directions(ors,start, end):
    # Request normal route between appropriate locations without construction sites
    request_params = {'coordinates': [start,end],
                    'format_out': 'geojson',
                    'profile': 'driving-car',
                    'preference': 'shortest',
                    'instructions': 'false', }
    route = ors.directions(**request_params)

    directions = route['features'][0]['geometry']['coordinates']
    route_summary = route['features'][0]['properties']['summary']
    return directions, route_summary

# method to provide directions avoiding certain coordinates on a map
def driving_directions_avoiding_points(ors,start, end, list_avoid):

    # get the driving directions of the normal route
    request_params = {'coordinates': [start,end],
                    'format_out': 'geojson',
                    'profile': 'driving-car',
                    'preference': 'shortest',
                    'instructions': 'false', }
    route_normal = ors.directions(**request_params)


    # Create buffer polygons around construction sites with 10 m radius and low resolution
    sites_poly = []
    for coord in list_avoid:
        site_poly_coords = create_buffer_polygon(coord,
                                            resolution=2,  # low resolution to keep polygons lean
                                            radius=10)
        sites_poly.append(site_poly_coords)

    # Buffer route with 0.009 degrees 
    route_buffer = LineString(route_normal['features'][0]['geometry']['coordinates']).buffer(0.009)
    
    # Identify which avoidance coordinates fall into the buffer Polygon
    sites_buffer_poly = []
    for site_poly in sites_poly:
        poly = Polygon(site_poly)
        if route_buffer.intersects(poly):
            sites_buffer_poly.append(poly)
    
    # update the driving direction options with the areas that should be avoided
    request_params['options'] = {'avoid_polygons': geometry.mapping(MultiPolygon(sites_buffer_poly))}
    route_detour = ors.directions(**request_params)

    directions = route_detour['features'][0]['geometry']['coordinates']
    route_summary = route_detour['features'][0]['properties']['summary']
    return directions, route_summary

