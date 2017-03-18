from path import compute_camera_values
from screenshot import screenshot_360
from sights import getSights
from video import images_to_video

if __name__ == '__main__':
	screenshot_360(25.0, 48.8584, 2.2945, 1200, 40)
	images_to_video("out/", "sof_")
	#mark = getSights('London')
	#print(mark)