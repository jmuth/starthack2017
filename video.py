import os

def images_to_video(image_folder, image_format, output_video_filename):
	os.system("convert -delay 1x4 -antialias %s*%s %s" % (image_folder, image_format, output_video_filename))