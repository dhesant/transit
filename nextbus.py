#!/usr/bin/python3.6
import requests
from bs4 import BeautifulSoup
import datetime
import dateutil.parser as dparser

# Map bus routes to system ID"s
operator = { "8x": "citybus", "19": "citybus" }
stopcode = { "8x":
             {2552: "002552||8X-ISR-1||3||I",
              1214: "001214||8X-HVL-1||23||O"},
             "19":
             {2552: "002552||19-ISR-1||8||I",
              1214: "001214||19-THR-3||23||O"}}

# Create session cookie for HTML request
ssid = "5a41dea32347b"
ssidcookie = { ssid: "lpb8m4omcdcrk2fdm501g1h9p3"}

# Get raw data from nwstbus.com.hk
def getRawBuses(route, stop):
    payload = { "info": stopcode[route][stop], "ssid": ssid, "sysid": 34 }
    r = requests.get("https://mobile.nwstbus.com.hk/nwp3/set_etasession.php", params=payload, cookies=ssidcookie)
    if (r.text != "OK"):
        return None

    payload = { "l": "1", "ssid": ssid, "sysid": 34 }
    r = requests.get("https://mobile.nwstbus.com.hk/nwp3/geteta.php", params=payload, cookies=ssidcookie)
    if (r.text == ":("):
        return None

    return r.text

# Get list of next buses
def getBuses(route, stop):
    # Sanitize route number to lowercase
    route = route.lower()

    # Get and verify raw data from nwstbus.com.hk
    raw = getRawBuses(route, stop)
    if (raw == None):
        return None

    # Parse results into a dictionary
    soup = BeautifulSoup(raw, "lxml");
    
    results = []
    
    for child in soup.find(id="nextbux_list").children:
        results.append({
            "route": soup.find(id="nextbus_title").find("tr").contents[1].string.upper(),
            #"route": route,
            "operator": operator[route],
            "eta": dparser.parse(child.find_all("table")[0].td.string),
            "dest": child.find_all("table")[1].find_all("td")[0].string.replace("To: ", "" ,1),
            "isArrived": (True if child.find_all("table")[1].find_all("td")[1].string == "Arrived" else False)
        })

    return results

#print(getBuses("8X"))
