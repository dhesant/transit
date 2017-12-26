#!/usr/bin/python3
import requests
import xml.etree.ElementTree as ET

#############
# Functions #
#############

# Get Trams
def getTrams(stopCode):
    r = requests.get("https://hktramways.com/nextTram/geteat.php?stop_code=" + stopCode)
    root = ET.fromstring(r.content)
    return root

# Get ETA for the tram
def getTramETA(elem):
    return int(elem.attrib.get("arrive_in_second"))

########
# Code #
########

# Get Trams for HVT
trams = getTrams("HVT_B")
trams.extend(getTrams("HVT_K"))

# Sort entries by ETA (only necessary for extended entries)
trams[:] = sorted(trams, key=getTramETA)
    
# Print Output
print("Route\tDestination\tETA")

for child in trams:
    if child.attrib.get("is_arrived") == "1":
        if child.attrib.get("is_last_tram") == "1":
            print("Tram\t" + child.attrib.get("tram_dest_en") + "\tArrived (Last Tram)")
        else:
            print("Tram\t" + child.attrib.get("tram_dest_en") + "\tArrived")
    else:
        print("Tram\t" + child.attrib.get("tram_dest_en") + "\t" + child.attrib.get("arrive_in_minute"))
    
