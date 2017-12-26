#!/usr/bin/python3.6
import requests
from bs4 import BeautifulSoup
import datetime
import dateutil.parser as dparser

# Map bus routes to system ID's
routeid = { "8X": '56', "19": '191' }
operator = { "8X": 'citybus', "19": 'citybus' }

# Create session cookie for HTML request
ssidcookie = {"5a41dea32347b": 'lpb8m4omcdcrk2fdm501g1h9p3'}

# Get HTML from NWST
def getRawBuses(routeid):
    r = requests.get("https://mobile.nwstbus.com.hk/nwp3/geteta.php?l=1&ssid=5a41dea32347b&sysid=" + routeid, cookies=ssidcookie)
    return r.text

# Parse 
def getBuses(route):
    raw = getRawBuses(routeid[route])
    
    if (raw == ":("):
        return None
    
    soup = BeautifulSoup(raw, "lxml");
    
    results = {"children": []}
    
    for child in soup.find(id="nextbux_list").children:
        results["children"].append({
            'route': soup.find(id="nextbus_title").find('tr').contents[1].string.upper(),
            #'route': route,
            'operator': operator[route],
            'eta': dparser.parse(child.find_all("table")[0].td.string),
            'dest': child.find_all("table")[1].find_all('td')[0].string.replace("To: ", "" ,1),
            'isArrived': (True if child.find_all("table")[1].find_all('td')[1].string == "Arrived" else False)
        })

    return results

print(getBuses("8X"))
