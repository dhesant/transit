#!/usr/bin/python3.6
import requests
from bs4 import BeautifulSoup
import datetime
import dateutil.parser as dparser
import random
import asyncio
from aiohttp import ClientSession

# Map bus routes to system ID"s
operator = { "8x": "citybus", "19": "citybus" }
stopcode = { "8x":
             {2552: "002552||8X-ISR-1||3||I",
              1214: "001214||8X-HVL-1||23||O"},
             "19":
             {2552: "002552||19-ISR-1||8||I",
              1214: "001214||19-THR-3||23||O"}}

# Get raw data from nwstbus.com.hk
async def getRawBuses(route, stop):
    # Create session with unique ssid cookie
    ssid = '%013x' % random.randrange(16**13)
    ssidcookie = { ssid: '%026x' % random.randrange(16**26)}
    async with ClientSession(cookies=ssidcookie) as session:

        payload = { "info": stopcode[route][stop], "ssid": ssid, "sysid": 34 }
        async with session.get("https://mobile.nwstbus.com.hk/nwp3/set_etasession.php", params=payload) as resp:
            #assert resp.status == 200
            if (resp.text() != "OK"):
                return ""

            await resp.read()
            payload = { "l": "1", "ssid": ssid, "sysid": 34 }
            async with session.get("https://mobile.nwstbus.com.hk/nwp3/geteta.php", params=payload) as resp:
                #assert resp.status == 200
                if (resp.text() == ":("):
                    return ""
                return await resp.text()

# Get list of next buses
async def getBuses(route, stop):
    # Sanitize route number to lowercase
    route = route.lower()

    # Get and verify raw data from nwstbus.com.hk
    raw = await getRawBuses(route, stop)
    if (raw == ""):
        return []

    # Import HTML for parsing
    soup = BeautifulSoup(raw, "lxml")

    # Ensure entries exist
    if soup.find(id="nextbux_list").contents[0].find_all('table') == []:
        return []

    # Parse entries into dict
    results = []
    for child in soup.find(id="nextbux_list").children:
        results.append({
            "route": soup.find(id="nextbus_title").find("tr").contents[1].string.upper(),
            "operator": operator[route],
            "eta": dparser.parse(child.find_all("table")[0].td.string),
            "dest": child.find_all("table")[1].find_all("td")[0].string.replace("To: ", "" ,1),
            "isArrived": (True if child.find_all("table")[1].find_all("td")[1].string == "Arrived" else False),
            "isLast": False,
        })

    return results

def testBuses():
    loop = asyncio.get_event_loop()
    futures = []
    futures.append(asyncio.ensure_future(getBuses("8x", 2552)))
    futures.append(asyncio.ensure_future(getBuses("19", 2552)))
    loop.run_until_complete(asyncio.gather(*futures))
    loop.stop()
    for future in futures:
        print(future.result())
    
