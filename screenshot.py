from subprocess import Popen, PIPE
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import os, base64, time

abspath = lambda *p: os.path.abspath(os.path.join(*p))
ROOT = abspath(os.path.dirname(__file__))


def execute_command(command):
    result = Popen(command, shell=True, stdout=PIPE).stdout.read()
    if len(result) > 0 and not result.isspace():
        raise Exception(result)

def do_screen_capturing(driver, url, screen_path, width, height):

    # it save service log file in same directory
    # if you want to have log file stored else where
    # initialize the webdriver.PhantomJS() as
    # driver = webdriver.PhantomJS(service_log_path='/var/log/phantomjs/ghostdriver.log')
    driver.set_script_timeout(30)

    if width and height:
        driver.set_window_size(width, height)

    driver.get(url)

    time.sleep(6)

    # disable label
    # Click menu button
    menu_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "searchbox-hamburger"))
    )

    # Click menu button
    menu_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "searchbox-hamburger"))
    )
    
    driver.execute_script('arguments[0].click()', menu_button)

    # Click disable able
    disable_label_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "widget-settings-sub-button-label"))
    )
    

    #wait.until(lambda driver : driver.find_element_by_xpath("//*[contains(@class,'widget-settings-sub-button-label')]"))

    '''
    # Element invisible during a few ms
    time.sleep(0.5)

    driver.find_element_by_class_name('widget-settings-sub-button-label').click()
    '''

    #disable_label_button = driver.find_element_by_class_name('widget-settings-sub-button-label')
    driver.execute_script('arguments[0].click()', disable_label_button)

    time.sleep(1)

    driver.save_screenshot(screen_path)

def do_crop(params):
    command = [
        'convert',
        params['screen_path'],
        '-crop', '%sx%s+%s+%s' % (params['width'], params['height'], params['width_offset'], params['height_offset']),
        params['crop_path']
    ]
    execute_command(' '.join(command))

def get_screen_shot(**kwargs):
    driver = kwargs['driver']

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

    do_screen_capturing(driver, url, screen_path, width, height)


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

def screenshot_url(driver, url, nb):
    try:
        get_screen_shot(
            driver=driver, url=url, path='out/', filename='sof_%s.png' % str(nb).zfill(5),
            crop=True, crop_replace=True,
            crop_width=1600, crop_height=900,
            crop_offset_width=200, crop_offset_height=200
        )
        return 0
    except Exception as err:
        return -1