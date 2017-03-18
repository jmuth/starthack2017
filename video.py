import os

def images_to_video(image_folder, image_format, output_video_filename):
	os.system("mmfpeg -f image2 -i %ssof_\%5d%s %s" % (image_folder, image_format, output_video_filename))