import webbrowser
from selenium import webdriver

# webbrowser.open('http://www.sightsmap.com/')


# elem = driver.find_element_by_id("searchfield")

import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome()
driver.get("http://www.sightsmap.com/")
# assert "Python" in driver.title
elem = driver.find_element_by_id("searchfield")
elem.send_keys('London')
elem.send_keys(Keys.RETURN)
time.sleep(2)
assert "No results found." not in driver.page_source
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

print(markers)

driver.quit()
# driver.close()