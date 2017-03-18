from math import *

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


# tuple CamPoint {x, y, altitude, tilt, h, time}

import numpy as np
import scipy as sp


# Add full rotation around center
def add_rotation(path, center_point, radius, tilt, N, time_beg, time_end, rot_beg = 0, rot_width = 360):
    rad_tilt = tilt / 360.0 * 2.0 * pi
    sin_radius = radius * sin(rad_tilt)

    for i in range(int(N)):
        rev = 2.0 * pi * (rot_beg + (rot_width) * float(i) / (N-1)) / 360
        (x_offset, y_offset) = meter_to_coordinate(sin_radius * sin(rev), sin_radius * cos(rev), center_point[0])
        x = center_point[0] + x_offset * 180 / pi
        y = center_point[1] + y_offset * 180 / pi
        altitude = center_point[2] + radius * cos(rad_tilt)
        h = (360.0 - 90.0 - (rot_beg + (rot_width) * float(i) / (N-1)))

        time = time_beg + (time_end - time_beg) * float(i) / N

        path[0].append(x)
        path[1].append(y)
        path[2].append(altitude)
        path[3].append(tilt)
        path[4].append(h)
        path[5].append(time)

# This doesn't add the first and the last one
def add_traveling(path, p_a, p_b, N, time_beg, time_end, altitude_offset = 0):
    d_x = p_b[0] - p_a[0] 
    d_y = p_b[1] - p_a[1]
    d_a = p_b[2] - p_a[2]

    h = (acos(d_x / sqrt(d_x * d_x + d_y * d_y)) / (2.0 * pi) * 360) % 360
    if d_y < 0:
        h = (h + 90) % 360

    for i in range(1, int(N)):
        x = p_a[0] + d_x * float(i) / (N+1)
        y = p_a[1] + d_y * float(i) / (N+1)
        altitude = altitude_offset + p_a[2] + d_a * float(i) / (N+1)

        time = time_beg + (time_end - time_beg) * float(i) / (N+1)

        path[0].append(x)
        path[1].append(y)
        path[2].append(altitude)
        path[3].append(78.0)
        path[4].append(h)        
        path[5].append(time)



def path_at(path, i):
    return (path[0][i], path[1][i], path[2][i], path[3][i], path[4][i], path[5][i])

def point_to_string(p):
    return "@" + str(p[0]) + "," + str(p[1]) + "," + str(p[2]) + "a," + "35y," + str((p[4] % 360)) + "h,"+ str(p[3])


from scipy.interpolate import CubicSpline
# return a list of camera point uniformly sample in time
def spline_interpolation(path, nb_frame):
    frame_rate = (path[5][-1] - path[5][0]) / (nb_frame-1)

    res_list = []

    spline_x = CubicSpline(path[5], path[0])
    spline_y = CubicSpline(path[5], path[1])
    spline_a = CubicSpline(path[5], path[2])
    spline_tilt = CubicSpline(path[5], path[3])

    list_t = []
    for i in range(int(nb_frame)):
        list_t.append(frame_rate * i)
    
    x = spline_x(list_t)
    y = spline_y(list_t)
    a = spline_a(list_t)
    tilt = spline_tilt(list_t)

    # make sure that h is monotically decreasing

    spline_h = CubicSpline(path[5], path[4])
    h = spline_h(list_t)
    #h = [hh % 360 for hh in h]
    time = list_t
    return (x, y, a, tilt, h, time)

NB_PT = 5

def radians_from_circle(x, y):
    return (atan2(-y, x) / (2.0 * pi) * 360.0 + 90) % 360

# Get a list of destination (in the right order)
# Will do a half-rotation around each destination
# Need to first compute entry degree
def plan_trip(list_places, radius = 800, tilt = 55, time_per_destination = 2.0):

    path = [[],[],[],[],[],[]]

    # Compute direction between two destination.
    # We want to end with it as the last direction for the rotation

    # And start the next rotation with this direction
    time = 0.0
    current_h = 0
    next_h = 0

    sens = 1
    for x in range(len(list_places)-1):
        time_in = time
        time_out = time + time_per_destination

        # next_dir is the target dir for the end of this rotation
        dx = list_places[x+1][0] - list_places[x][0]
        dy = list_places[x+1][1] - list_places[x][1]

        distance = sqrt(dx * dx + dy * dy)

        # direction to the next destination
        '''
        if dx == 0.0:
            if dy < 0:
                h = 90
            else:
                h = 270
        else:
            h = (atan(dy / dx) / (2.0 * pi) * 360) % 360

        if dy == 0.0:
            if dx < 0:
                h = 180
            else:
                h = 0

        h = abs(h) + 90
        '''
        h = atan2(-dy, dx) / (2.0 * pi) * 360.0 + 90

        print("dx: " + str(dx / distance) + " dy: " + str(dy / distance) + " h: " + str(h))
        
        # threshold so spline interpolate rotation during traveling as well
        #h = h - 15

        end_h = (h + sens * 90) % 360;
        print("end_h: " + str(end_h))

        if x == 0:
            current_h = ( end_h + 180 )

        rot_width = abs(end_h - current_h)
        if rot_width < 90:
            rot_width = rot_width + 269 
        add_rotation(path, list_places[x], radius, tilt, NB_PT, time_in, time_out, current_h % 360, - sens * rot_width)

        time_travel = distance / 0.02 * time_per_destination

        current_h = (end_h + 180) % 360;
        print(current_h)
        #current_h = (current_h + sens * (end_h - current_h)) % 360

        sens = sens * (-1)

        time = time + time_per_destination + time_travel


    time_in = time
    time_out = time + time_per_destination
    add_rotation(path, list_places[-1], radius, tilt, NB_PT, time_in, time_out, (current_h) % 360, - sens * 180 )

    # add points in between destinations at higher altitude

    for x in range(len(path[0])-1):
        if abs(path[4][x] - path[4][x+1]) > 360:
             path[4][x+1] =  path[4][x] + (path[4][x+1] - path[4][x]) % 360  

    if False:
        return path

    spline_h = CubicSpline(path[5], path[4])
    for x in range(0, len(list_places) - 1):
        distance = sqrt(dx * dx + dy * dy)
        time_travel = distance / 0.02 * time_per_destination

        idx = (x + 1) * NB_PT + x

        dx = list_places[x+1][0] - list_places[x][0]
        dy = list_places[x+1][1] - list_places[x][1]
        #h = (atan(dy / dx) / (2.0 * pi) * 360 - 90) % 360
        '''
        if dx == 0.0:
            if dy < 0:
                h = 90
            else:
                h = 270
        else:
            h = (atan(dy / dx) / (2.0 * pi) * 360) % 360

        if dy == 0.0:
            if dx < 0:
                h = 180
            else:
                h = 0

        h = abs(h) + 90
        '''
        h = atan2(-dy, dx) / (2.0 * pi) * 360.0 + 90
        distance_m = coordinate_distance(list_places[x][0], list_places[x][1], list_places[x+1][0], list_places[x+1][1])
        path[0].insert(idx, (list_places[x][0] + list_places[x+1][0]) / 2.0)
        path[1].insert(idx, (list_places[x][1] + list_places[x+1][1]) / 2.0)
        path[2].insert(idx, (list_places[x][2] + list_places[x+1][2] + distance_m * 0.5) / 2.0)
        path[3].insert(idx, 40.0)
        time_inter = (path[5][idx - 1] + path[5][idx]) / 2.0
        #path[4].insert(idx, h)       
        path[4].insert(idx, spline_h(time_inter))        
        path[5].insert(idx, time_inter)

    #print(path[2])
    #print(path[5])

    return path

'''
def plan_trip(list_places, radius = 800, tilt = 55, time_per_destination = 2.0):

    path = [[],[],[],[],[],[]]

    # Compute direction between two destination.
    # We want to end with it as the last direction for the rotation

    # And start the next rotation with this direction
    time = 0.0
    current_h = 0
    next_h = 0
    for x in range(len(list_places)-1):
        time_in = time
        time_out = time + time_per_destination

        # next_dir is the target dir for the end of this rotation
        dx = list_places[x+1][0] - list_places[x][0]
        dy = list_places[x+1][1] - list_places[x][1]

        distance = sqrt(dx * dx + dy * dy)


        h = (acos(dx / distance) / (2.0 * pi) * 360) % 360

        # threshold so spline interpolate rotation during traveling as well
        #h = h - 15

        if x == 0:
            current_h = ( h + 180 ) % 360

        add_rotation(path, list_places[x], radius, tilt, 5, time_in, time_out, current_h, (h - current_h) % 360 )

        time_travel = distance / 0.02 * time_per_destination

        current_h = h
        time = time + time_per_destination + time_travel


    time_in = time
    time_out = time + time_per_destination
    add_rotation(path, list_places[-1], radius, tilt, 5, time_in, time_out, current_h, 180 )

    # add points in between destinations at higher altitude

    spline_h = CubicSpline(path[5], path[4])
    for x in range(1, len(list_places)):
        distance = sqrt(dx * dx + dy * dy)
        time_travel = distance / 0.02 * time_per_destination

        idx = x * 5 + (x - 1)

        distance_m = coordinate_distance(path[0][idx-1], path[1][idx-1], path[0][idx], path[1][idx])
        path[0].insert(idx, (path[0][idx - 1] + path[0][idx]) / 2.0)
        path[1].insert(idx, (path[1][idx - 1] + path[1][idx]) / 2.0)
        path[2].insert(idx, (path[2][idx - 1] + path[2][idx] + distance_m * 0.5) / 2.0)
        path[3].insert(idx, 40.0)
        time_inter = (path[5][idx - 1] + path[5][idx]) / 2.0
        path[4].insert(idx, spline_h(time_inter))        
        path[5].insert(idx, time_inter)

    #print(path[2])
    #print(path[5])

    return path
'''
'''
def plan_trip(list_places, radius = 800, time_per_destination = 2.0):

    path = [[],[],[],[],[],[]]

    # Compute direction between two destination.
    # We want to end with it as the last direction for the rotation

    # And start the next rotation with this direction
    time = 0.0
    current_h = 0
    next_h = 0
    for x in range(len(list_places)-1):
        time_in = time
        time_out = time + time_per_destination

        # next_dir is the target dir for the end of this rotation
        dx = list_places[x+1][0] - list_places[x][0]
        dy = list_places[x+1][1] - list_places[x][1]

        distance = sqrt(dx * dx + dy * dy)

        h = (acos(dx / distance) / (2.0 * pi) * 360) % 360

        # threshold so spline interpolate rotation during traveling as well
        #h = h - 15

        if x == 0:
            current_h = ( h + 180 ) % 360

        add_rotation(path, list_places[x], radius, 40, 5, time_in, time_out, current_h, (h - current_h) % 360 )

        time_travel = distance / 0.02 * time_per_destination

        if x != 0:
            # add a point in between the current destination and the next at higher altitude
            # do this only if we travel a certain distance
            distance_m = coordinate_distance(path[0][-6], path[1][-6], path[0][-5], path[1][-5])
            path[0].insert(len(path[0]) - 5, (path[0][-6] + path[0][-5]) / 2.0)
            path[1].insert(len(path[1]) - 5, (path[1][-6] + path[1][-5]) / 2.0)
            path[2].insert(len(path[2]) - 5, (path[2][-6] + path[2][-5] + distance_m * 0.5) / 2.0)
            path[3].insert(len(path[3]) - 5, 60.0)
            path[4].insert(len(path[4]) - 5, path[4][-6])        
            path[5].insert(len(path[5]) - 5, (path[5][-6] + path[5][-5]) / 2.0)

        current_h = h
        time = time + time_per_destination + time_travel


    time_in = time
    time_out = time + time_per_destination
    add_rotation(path, list_places[-1], radius, 40, 5, time_in, time_out, current_h, 180 )

    # add a point in between the current destination and the next at higher altitude
    # do this only if we travel a certain distance
    distance = sqrt(dx * dx + dy * dy)
    distance_m = coordinate_distance(path[0][-6], path[1][-6], path[0][-5], path[1][-5])
    time_travel = distance / 0.02 * time_per_destination

    path[0].insert(len(path[0]) - 5, (path[0][-6] + path[0][-5]) / 2.0)
    path[1].insert(len(path[1]) - 5, (path[1][-6] + path[1][-5]) / 2.0)
    path[2].insert(len(path[2]) - 5, (path[2][-6] + path[2][-5] + distance_m * 0.5) / 2.0)
    path[3].insert(len(path[3]) - 5, 40.0)
    path[4].insert(len(path[4]) - 5, path[4][-6])        
    path[5].insert(len(path[5]) - 5, (path[5][-6] + path[5][-5]) / 2.0)
    return path
'''