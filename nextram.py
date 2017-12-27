#!/usr/bin/python3
import requests
import xml.etree.ElementTree as ET
import dateutil.parser as dparser

#############
# Functions #
#############

# Get Trams
def getRawTrams(stopCode):
    payload = {"stop_code": stopCode}
    r = requests.get("https://hktramways.com/nextTram/geteat.php", params=payload)
    return r.content

def getXmlTrams(stopCode):
    root = ET.fromstring(getRawTrams(stopCode))
    return root

def getTrams(stopCode):
    if stopCode == "HVT":
        trams = getXmlTrams("HVT_B")
        trams.extend(getXmlTrams("HVT_K"))
    else:
        trams = getXmlTrams(stopCode)

    results = []

    for child in trams:
        results.append({
            "route": child.attrib.get("dest_stop_code"),
            "operator": "hktramways",
            "eta": dparser.parse(child.attrib.get("eat")),
            "dest": child.attrib.get("tram_dest_en"),
            "isArrived": (True if child.attrib.get("is_arrived") == "1" else False),
            "isLast": (True if child.attrib.get("is_last_tram") == "1" else False),
        })

    return results
