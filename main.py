from path import compute_camera_values

if __name__ == '__main__':

	N = 10.0
	for i in range (int(N)):
		# Top-down Eiffel Tower
		#print("https://www.google.ch/maps/" + compute_camera_values(48.8584, 2.2945, 1200, 90.0 * i / N, 0.0))

		# 360 Eiffel Tower
		print("https://www.google.ch/maps/" + compute_camera_values(48.8584, 2.2945, 1200, 40, i / N))