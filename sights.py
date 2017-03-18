import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import googlemaps

def get_sights(name='Fribourg'):
    print("Getting sights of:", name)
    driver = webdriver.Chrome()
    # enter website
    driver.get("http://www.sightsmap.com/")
    # search the site
    time.sleep(3)
    elem = driver.find_element_by_id("searchfield")
    elem.send_keys(name)
    elem.send_keys(Keys.RETURN)
    time.sleep(4)

    # # Wait for the element
    # num = WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.CLASS_NAME, "searchbox-hamburger"))
    # )

    success = False
    max_try = 5
    i = 0
    while not success:
        try:
            #  get the displayed markers
            ++i
            num = (driver.execute_script("return mapMarkersArray.length"))
            if num != 0:
                success = True
            else:
                print("[WAIT] sightsmap not ready yet")
                time.sleep(2)
        except Exception as err:
            if i <= max_try:
                print("[ERROR] sightsmap timed out, try again (iteration:,", i, ")")
                time.sleep(3)
            else:
                quit()


    markers = []
    for i in range(num):
        request = "return mapMarkersArray[" + str(i) + "]"
        title = request + ".marker.title"
        lat = request + ".poi.lat"
        lng = request + ".poi.lng"
        rank = request + ".poi.tcrank"

        marker = [driver.execute_script(lat),       # latitude
                  driver.execute_script(lng),       # longitude
                  60,                               # camera height (fixed for this moment)
                  driver.execute_script(title),     # name
                  driver.execute_script(rank)       # local rank
                  ]

        markers.append(marker)

    sorted(markers, key=lambda markers: markers[4])

    # quit browser
    driver.quit()
    print("[INFO] Success. Get sights: ", markers)
    return markers

def get_elevation():
    gmaps = googlemaps.Client(key='INSERT_KEY_HERE')
    elevation = gmaps.elevation((39.7391536, -104.9847034))
    print(elevation)
