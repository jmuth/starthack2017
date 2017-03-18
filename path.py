from math import sin, cos, pi, asin, atan2, sqrt

def coordinate_distance(lat1, lon1, lat2, lon2):
    R = 6378.137 # Radius of earth in KM
    dLat = lat2 * pi / 180.0 - lat1 * pi / 180.0
    dLon = lon2 * pi / 180.0 - lon1 * pi / 180.0
    a = sin(dLat/2) * sin(dLat/2) + cos(lat1 * pi / 180.0) * cos(lat2 * pi / 180.0) * sin(dLon/2.0) * sin(dLon/2.0)
    c = 2.0 * atan2(sqrt(a), sqrt(1.0-a));
    d = R * c
    return d * 1000.0 # meters

def meter_to_coordinate(m_x, m_y, lat):
	coord_x = m_x / 6378137.0
	#coord_y = m_y / (6378137.0 * cos(lat / 360 * 2 * pi))
	coord_y = m_y / (6378137.0 * cos(lat / 360.0 * 2 * pi))
	return (coord_x, coord_y)

# Return string for google maps address
# Takes x and y coordinates, rayon of the rotation, tilt and revolution (between 0 and 1)
def compute_camera_values(origin_x, origin_y, rayon_meter, tilt, rev):
	
	tilt_rayon_meter = rayon_meter * sin(tilt / 360.0 * 2.0 * pi)

	(x_offset, y_offset) = meter_to_coordinate(tilt_rayon_meter * sin(rev * 2.0 * pi), tilt_rayon_meter * cos(rev * 2.0 * pi), origin_x)

	x = origin_x + x_offset * 180 / pi
	y = origin_y + y_offset * 180 / pi

	#meter_rayon = coordinate_distance(origin_x, origin_y, x, y)
	h = (360.0 - 90.0 - 360.0 * rev) % 360.0
	altitude = rayon_meter * cos(tilt / 360.0 * 2.0 * pi)
	return "@" + str(x) + "," + str(y) + "," + str(altitude) + "a," + "35y," + str(h) + "h,"+ str(tilt) + "t/data=!3m1!1e3"
