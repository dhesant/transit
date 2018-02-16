#!/usr/bin/python3.6
#import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import dateutil.parser as dparser
#import random
import asyncio
from aiohttp import ClientSession

# Map bus routes to system ID"s
operator = { "8x": "citybus", "19": "citybus", "1": "citybus" }
_disabled_stopcode = { "8x":
              {
                  2552: "8X||002552||3||I||8X-ISR-1",
                  1214: "8X||001214||23||O||8X-HVL-1"},
              "19":
              {
                  2552: "19||002552||8||I||19-ISR-1",
                  1214: "19||001214||23||O||19-THR-3"},
             "1":
             {
                 2552: "1||002552||1||I||1-FEV-1",}
              }

# Get raw data from nwstbus.com.hk
async def getRawBuses(route, stopcode):
    async with ClientSession() as session:
        params = { "info": stopcode }
        async with session.get("https://mobile.nwstbus.com.hk/text/set_etasession.php", params=params) as resp:
            await resp.read()
        
        params = { "l": "1" }
        async with session.get("https://mobile.nwstbus.com.hk/text/geteta.php", params=params) as resp:
            return await resp.text()
        
# Get raw data from nwstbus.com.hk
def getRawBusesSync(route, stopcode):
    s = requests.Session()
    
    params = { "info": stopcode }
    resp = s.get("https://mobile.nwstbus.com.hk/text/set_etasession.php", params=params)

    params = { "l" : "1" }
    resp = s.get("https://mobile.nwstbus.com.hk/text/geteta.php", params=params)
    return resp.text
    
# Get list of next buses
async def getBuses(route, stopcode):
    # Sanitize route number to lowercase
    route = route.lower()

    # Get and verify raw data from nwstbus.com.hk
    raw = await getRawBuses(route, stopcode)
    if (raw == ""):
        return []

    # Import HTML for parsing
    soup = BeautifulSoup(raw, "lxml")

    # Parse entries into dict
    results = []
    for row in soup.body.find_all('tr')[1:]:
        eta = dparser.parse(row.find_all('td')[0].string)
        # Ensure time in in future (i.e. midnight the next day)
        if ((eta - datetime.today()) <= timedelta(minutes=-5)):
            eta = eta + timedelta(days=1)
        results.append({
            "route": soup.body.h2.contents[0].string.replace("Route ", "", 1),
            "operator": operator[route],
            "eta": eta,
            "dest": row.find_all('td')[1].string.replace("To: ", "" ,1),
            "isArrived": (True if row.find_all('td')[2].string == "Arrived" else False),
            "isLast": False,
        })

    return results

def testBuses():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    futures = []
    futures.append(asyncio.ensure_future(getRawBuses("8x", "8X||002552||3||I||8X-ISR-1")))
    futures.append(asyncio.ensure_future(getBuses("8x", "8X||001214||23||O||8X-HVL-1")))
    loop.run_until_complete(asyncio.gather(*futures))
    loop.stop()
    for future in futures:
        print(future.result())
    
