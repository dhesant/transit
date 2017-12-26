#!/usr/bin/python3.6
import requests
from bs4 import BeautifulSoup

# Map bus routes to system ID's
routeid = {"8x": '56', "19": '75' }

# Create session cookie for HTML request
ssidcookie = {"5a41dea32347b": 'lpb8m4omcdcrk2fdm501g1h9p3'}

# Get Buses
def getRawBuses(routeid):
    r = requests.get("https://mobile.nwstbus.com.hk/nwp3/geteta.php?l=1&ssid=5a41dea32347b&sysid=" + routeid, cookies=ssidcookie)
    return r.text

route = "8x"
raw = getRawBuses(routeid[route])
soup = BeautifulSoup(raw, "lxml");

results = {"children": []}

for child in soup.find(id="nextbux_list").children:
    results["children"].append({
        'route': soup.find(id="nextbus_title").find('tr').contents[1].string,
        'eta': child.find_all("table")[0].td.string,
        'dest': child.find_all("table")[1].td.string,
    })
    
