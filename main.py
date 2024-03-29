from path import *
from screenshot import *
from video import *
from selenium import webdriver
import threading, timeit, sys
from queue import Queue
from sights import get_sights
from except_file import except_already_existing

NB_THREADS = 4
NB_FRAMES = 1800
NAME_PLACE = 'Manhattan'
N_SIGHTS = 4


# from sights import get_sights

def worker():
    driver = webdriver.Chrome('/Users/valentin/Documents/Hackathons/StartHack/chromedriver')
    #driver = webdriver.Chrome()

    while not q.empty():
        item = q.get()
        url = item[0]
        image_nb = item[1]
        if screenshot_url(driver, url, image_nb) == 0:
            print(threading.current_thread().name + " computed image " + str(image_nb) + ", %d remaining" % q.qsize())
            q.task_done()
        else:
            print(threading.current_thread().name + " failed to compute image " + str(image_nb)  + ", %d remaining !!!!!!!!!" % q.qsize())
            q.task_done()
            q.put(item)

if __name__ == '__main__':
    except_array =except_already_existing()
    # except_array = []

    sights = get_sights(NAME_PLACE)[:N_SIGHTS]

    # looping back to the first sight
    sights.append(sights[0])

    start = timeit.default_timer()

    p_eiffel = (48.8584, 2.2945, 60)
    p_triomphe = (48.8738, 2.2950, 60)
    p_chaillot = (48.8620159, 2.2878386, 80)
    p_grand_palais = (48.8663031, 2.3127906, 80)
    p_louvre = (48.8612266, 2.3357741, 80)
    p_monmartre = (48.8866677, 2.3430436, 120)

    paris = [p_eiffel, p_triomphe, p_chaillot, p_grand_palais, p_louvre, p_monmartre, p_eiffel]

    # # fribourg
    p_poya = (46.8133523,7.1645176, 60)
    p_cathedral = (46.8062408,7.1629309, 60)
    p_st_michel = (46.8066934,7.157652, 60)
    p_perolle = (46.7940545,7.1470015, 60)

    fribourg = [p_poya, p_cathedral]

    path = [[],[],[],[],[],[]]
    path = plan_trip(sights, 1200)

    '''
    # ensure that h are in monotically decreasing
    for x in range(1, len(path[4])):
        while path[4][x] > path[4][x - 1]:
            path[4][x] = path[4][x] - 360.0
    '''

    interpolated_path = spline_interpolation(path, NB_FRAMES)

    q = Queue()
    for i in range(len(interpolated_path[0])):
        if (i+1) not in except_array:
            url = "https://www.google.ch/maps/" + point_to_string(path_at(interpolated_path, i)) + "t/data=!3m1!1e3"
            q.put((url, i + 1))

    for i in range(NB_THREADS):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()

    q.join()

    '''
    driver = webdriver.Chrome()

    missed = []
    for i in range(len(interpolated_path[0])):
        print("Creating image %d/%d..." % (i + 1, len(interpolated_path[0])))
        url = "https://www.google.ch/maps/" + point_to_string(path_at(interpolated_path, i)) + "t/data=!3m1!1e3"
        n = i + 1
        try:
            screenshot_url(driver, url, n)
        except Exception as err:
            miss_screenshot = [url, n]
            print("[ERROR] shot", n, "missed:", url)
            missed.append(miss_screenshot)

    print("[INFO] try to recover missed shots")
    while(len(missed) != 0):
        try:
            shot_to_try = missed.pop(-1)
            screenshot_url(shot_to_try[0], shot_to_try[1])
        except Exception as err:
            print("[ERROR] shot", n, "missed again:", url)
            missed.append(miss_screenshot)

    driver.quit()
    '''
    images_to_video('out/sof_\%5d', '.png', 'videos/' + NAME_PLACE + '.mp4')

    stop = timeit.default_timer()

    print("Time taken: %d seconds" % (stop - start))

    '''
    import matplotlib.pyplot as plt
    ax = plt.axes()
    ax.plot(path[0], path[1], 'o', interpolated_path[0], interpolated_path[1], '-')

    import matplotlib.pyplot as plt
    ax = plt.axes()
    ax.plot(path[0], path[1], 'o', interpolated_path[0], interpolated_path[1], '-')

    d_x = [sin(h * 2.0 * pi / 360 + pi / 4.0) * 0.003 for h in path[4]]
    d_y = [cos(h * 2.0 * pi / 360 + pi / 4.0) * 0.003 for h in path[4]]

    #for i in range(len(path[0])):
    #   plt.arrow(path[0][i], path[1][i], d_x[i], d_y[i], fc="k", ec="k", head_width=0.001, head_length=0.001 )
    #plt.arrow(interpolated_path[0][i], interpolated_path[1][i], d_x[i], d_y[i], fc="k", ec="k", head_width=0.00001, head_length=0.001 )

    plt.show()
    print(interpolated_path[4])
	'''
# Point {x, y, z}
# CameraPoint {p, t, h}
