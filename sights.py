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
    elem = driver.find_element_by_id("searchfield")
    elem.send_keys(name)
    elem.send_keys(Keys.RETURN)
    time.sleep(2)

    #  get the displayed markers
    num = (driver.execute_script("return mapMarkersArray.length"))
    markers = []
    for i in range(num):
        request = "return mapMarkersArray[" + str(i) + "]"
        title = request + ".marker.title"
        lat = request + ".poi.lat"
        lng = request + ".poi.lng"

        marker = [driver.execute_script(title),
                  driver.execute_script(lat),
                  driver.execute_script(lng)
                  ]

        markers.append(marker)

    # quit browser
    driver.quit()
    print("Success")
    return markers

def get_elevation():
    gmaps = googlemaps.Client(key='INSERT_KEY_HERE')
    elevation = gmaps.elevation((39.7391536, -104.9847034))
    print(elevation)
