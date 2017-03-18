from path import compute_camera_values
# from screenshot import screenshot_360
from sights import getSights

if __name__ == '__main__':
	# screenshot_360(25.0, 48.8584, 2.2945, 1200, 40)
	mark = getSights('London')
	print(mark)