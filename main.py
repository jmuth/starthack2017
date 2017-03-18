from path import *
from screenshot import *
from video import *
#from sights import get_sights

if __name__ == '__main__':
	#get_sights('London')

	p_eiffel = (48.8584, 2.2945, 60)
	p_triomphe = (48.8738, 2.2950, 60)
	p_chaillot = (48.8620159,2.2878386, 80)
	p_grand_palais = (48.8663031,2.3127906, 80)
	p_louvre = (48.8612266,2.3357741, 80)
	p_monmartre = (48.8866677,2.3430436, 120)

	path = [[],[],[],[],[],[]]

	path = plan_trip((p_eiffel, p_triomphe, p_chaillot, p_grand_palais, p_louvre, p_monmartre))

	# ensure that h are in monotically decreasing
	for x in range(1,len(path[4])):
		if path[4][x] > path[4][x-1]:
			path[4][x] = path[4][x] - 360.0

	#for i in range(len(path[0])):
	#	print("https://www.google.ch/maps/" + point_to_string(path_at(path, i)) + "t/data=!3m1!1e3")

	#print([int(x) for x in path[4]])
	interpolated_path = spline_interpolation(path, 150)

	print("+++++++ Interpolated path +++++++")

	for i in range(len(interpolated_path[0])):
		print("Creating image %d/%d..." % (i+1, len(interpolated_path[0])))
		screenshot_url("https://www.google.ch/maps/" + point_to_string(path_at(interpolated_path, i)) + "t/data=!3m1!1e3", i+1)

	images_to_video('out/', '.png', 'path.mp4')

#	print([int(x) for x in interpolated_path[4]])

	'''
	import matplotlib.pyplot as plt
	ax = plt.axes()
	ax.plot(path[0], path[1], 'o', interpolated_path[0], interpolated_path[1], '-')

	#d_x = [sin(h * 2.0 * pi / 360 + pi / 4.0) * 0.003 for h in path[4]]
	#d_y = [cos(h * 2.0 * pi / 360 + pi / 4.0) * 0.003 for h in path[4]]

	#for i in range(len(path[0])):
	#	plt.arrow(path[0][i], path[1][i], d_x[i], d_y[i], fc="k", ec="k", head_width=0.001, head_length=0.001 )
		#plt.arrow(interpolated_path[0][i], interpolated_path[1][i], d_x[i], d_y[i], fc="k", ec="k", head_width=0.00001, head_length=0.001 )


	#ax.axis([48.84, 48.9, 2.28, 2.32])
	#ax.arrow( 1.5, 0.8, 0.2, -0.2, fc="k", ec="k", head_width=0.05, head_length=0.1 )

	plt.show()
	print(interpolated_path[4])
	'''
# Point {x, y, z}
# CameraPoint {p, t, h}
