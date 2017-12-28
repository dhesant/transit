#!/usr/bin/python3
import requests
import xml.etree.ElementTree as ET
import dateutil.parser as dparser
import asyncio
from aiohttp import ClientSession

#############
# Functions #
#############

# Get Trams
async def getRawTrams(stopCode):
    async with ClientSession() as session:
        payload = {"stop_code": stopCode}
        async with session.get("https://hktramways.com/nextTram/geteat.php", params=payload) as resp:
            root = ET.fromstring(await resp.text())
            return root

async def getTrams(stopCode):
    # Special handler for Happy Valley
    if stopCode == "HVT":
        trams = await getRawTrams("HVT_B")
        trams.extend(await getRawTrams("HVT_K"))
    else:
        trams = await getRawTrams(stopCode)

    # Parse results into dict
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

def testTrams():
    loop = asyncio.get_event_loop()
    futures = []
    futures.append(asyncio.ensure_future(getTrams("HVT")))
    futures.append(asyncio.ensure_future(getTrams("59E")))
    loop.run_until_complete(asyncio.gather(*futures))
    loop.stop()
    for future in futures:
        print(future.result())
