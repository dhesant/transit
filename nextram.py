import requests
import xml.etree.ElementTree as ET

# XML Parser
def parseETA(stopCode):
    r = requests.get("https://hktramways.com//nextTram/geteat.php?stop_code=" + stopCode)
    root = ET.fromstring(r.content)

    return root

# Get Trams for HVTc
hvt = parseETA("HVT_B")
hvt.extend(parseETA("HVT_K"))

# Get ETA as int from XML entry
def getETA(elem):
    return int(elem.attrib.get("arrive_in_second"))

# Sort entries by ETA
hvt[:] = sorted(hvt, key=getETA)
    
# Print Output
print("Destination\tETA")

for child in hvt:
    if child.attrib.get("is_arrived") == "1":
        if child.attrib.get("is_last_tram") == "1":
            print(child.attrib.get("tram_dest_en") + "\tArrived (Last Tram)")
        else:
            print(child.attrib.get("tram_dest_en") + "\tArrived")
    else:
        print(child.attrib.get("tram_dest_en") + "\t" + child.attrib.get("arrive_in_minute"))
        
    #print(child.attrib.items())
    
