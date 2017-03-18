import os

def images_to_video(image_folder, image_name):
	os.system("ffmpeg -f image2 -i %s%s%d.png video.mpg" % (image_folder, image_name))