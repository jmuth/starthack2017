from subprocess import Popen, PIPE
from selenium import webdriver
from path import compute_camera_values

import os, base64, time

abspath = lambda *p: os.path.abspath(os.path.join(*p))
ROOT = abspath(os.path.dirname(__file__))


def execute_command(command):
    result = Popen(command, shell=True, stdout=PIPE).stdout.read()
    if len(result) > 0 and not result.isspace():
        raise Exception(result)


def do_screen_capturing(url, screen_path, width, height):
    print("Capturing screen..")
    driver = webdriver.Chrome()
    # it save service log file in same directory
    # if you want to have log file stored else where
    # initialize the webdriver.PhantomJS() as
    # driver = webdriver.PhantomJS(service_log_path='/var/log/phantomjs/ghostdriver.log')
    driver.set_script_timeout(30)
    if width and height:
        driver.set_window_size(width, height)

    driver.get(url)
    time.sleep(8)

    driver.save_screenshot(screen_path)
    driver.quit()

def do_crop(params):
    print("Croping captured image..")
    command = [
        'convert',
        params['screen_path'],
        '-crop', '%sx%s+%s+%s' % (params['width'], params['height'], params['width_offset'], params['height_offset']),
        params['crop_path']
    ]
    execute_command(' '.join(command))

def get_screen_shot(**kwargs):
    url = kwargs['url']
    width = int(kwargs.get('width', 1024)) # screen width to capture
    height = int(kwargs.get('height', 768)) # screen height to capture
    filename = kwargs.get('filename', 'screen.png') # file name e.g. screen.png
    path = kwargs.get('path', ROOT) # directory path to store screen

    crop = kwargs.get('crop', False) # crop the captured screen
    crop_width = int(kwargs.get('crop_width', width)) # the width of crop screen
    crop_height = int(kwargs.get('crop_height', height)) # the height of crop screen
    crop_offset_width = int(kwargs.get('crop_offset_width', 0)) # the offset width of crop screen
    crop_offset_height = int(kwargs.get('crop_offset_height', 0)) # the offset height of crop screen
    crop_replace = kwargs.get('crop_replace', False) # does crop image replace original screen capture?

    screen_path = abspath(path, filename)
    crop_path = screen_path

    do_screen_capturing(url, screen_path, width, height)

    if crop:
        if not crop_replace:
            crop_path = abspath(path, 'crop_'+filename)
        params = {
            'width': crop_width, 'height': crop_height,
            'crop_path': crop_path, 'screen_path': screen_path,
            'width_offset': crop_offset_width, 'height_offset': crop_offset_height
            }
        do_crop(params)

    return screen_path, crop_path

def screenshot_360(N, origin_x, origin_y, rayon_meter, tilt):
    for i in range (int(N)):
        url = "https://www.google.ch/maps/" + compute_camera_values(origin_x, origin_y, rayon_meter, tilt, i / N)
        screen_path, crop_path = get_screen_shot(
            url=url, path='out/', filename='sof_%d.png' % (i+1),
            crop=True, crop_replace=True,
            crop_width=1600, crop_height=900,
            crop_offset_width=200, crop_offset_height=200
        )