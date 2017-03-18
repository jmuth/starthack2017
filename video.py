import os


def images_to_video(image_folder, image_format, output_video_filename):
    os.system("ffmpeg -f image2 -i %s%s %s" % (image_folder, image_format, output_video_filename))
