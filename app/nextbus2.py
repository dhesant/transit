import requests
import secrets
import asyncio
from aiohttp import ClientSession

def getSysCode():
    return secrets.token_urlsafe(42)

def getRouteList():
    apiURL = "http://mobile.nwstbus.com.hk/api6/getroutelist2.php?rno=&l=1&syscode=" + getSysCode()

    r = requests.get(apiURL)
    routes = [];
    for route in r.text.split("<br>"):
        if (route == ''):
            break
        raw = route.split("||")
        if (len(raw) == 11):
            parsed = {
                'operator': raw[0],
                'route': raw[1],
                'destCode': raw[2],
                'serviceCount': raw[3],
                'originName': raw[4],
                'destName': raw[5],
                #'unknown6': raw[6],
                'variantCode': raw[7],
                'serviceID': raw[8],
                'direction': raw[9],
                'remarks': raw[10],
                }
            routes.append(parsed)
        else:
            print("Unable to parse: " + str(raw))
            
    return routes

async def getRouteServices(variantCode):
    async with ClientSession() as session:
        apiURL = "http://mobile.nwstbus.com.hk/api6/getvariantlist.php?id=" + variantCode + "&l=1&syscode=" + getSysCode()
        async with session.get(apiURL) as resp:
            r = await resp.text()

    services = []
    for service in r.split("<br>"):
        if (service == ''):
            break
        raw = service.split("||")
        if (len(raw) == 5):
            splitCode = raw[4].split("***")
            parsed = {
                'operator': splitCode[0],
                'serviceCode': splitCode[1],
                'startCount': splitCode[2],
                'endCount': splitCode[3],
                'serviceID': splitCode[4],
                'direction': splitCode[5],
                'description': raw[3],
            }
            services.append(parsed)
        else:
            print("Unable to parse: " + str(raw))

    return services

def getAllRouteServices():
    routes = getRouteList()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    futures = []

    for route in routes:
        futures.append(asyncio.ensure_future(getRouteServices(route['variantCode'])))

    loop.run_until_complete(asyncio.gather(*futures))
    loop.stop()

    services = []
    for future in futures:
        services.extend(future.result())
    return services

async def getRouteStops(service):
    async with ClientSession() as session:
        info = "1|*|" + service['operator'] + "||" + service['serviceCode'] + "||" + service['startCount'] + "||" + service['endCount'];
        apiURL = "https://mobile.nwstbus.com.hk/api6/ppstoplist.php?info=" + info + "&l=1&syscode=" + getSysCode()
        async with session.get(apiURL) as resp:
            r = await resp.text()

    stops = []
    for stop in r.split("<br>"):
        if (stop == ''):
            break
        raw = stop.split("||")
        parsed = {
            'serviceCode': raw[1],
            'stopCount': raw[2],
            'stopID': raw[3],
            'poleID': raw[4],
            'location': {
                'latitude': raw[5],
                'longitude': raw[6],
                },
            'stopName': raw[7],
            'destName': raw[8],
            'fares': {
                'adultFare': raw[10],
                'childFare': raw[12],
                'seniorFare': raw[13],
                },
            }
        stops.append(parsed)
    return stops

async def getRouteStopsAll(route):
    services = await getRouteServices(route['variantCode'])

    allStops = []
    for service in services:
        stops = await getRouteStops(service)
        allStops.extend(stops)

    return allStops

def _sync_getRouteStopsAll(route):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    futures = []

    futures.append(asyncio.ensure_future(getRouteStopsAll(route)))

    loop.run_until_complete(asyncio.gather(*futures))
    loop.stop()

    stops = []
    for future in futures:
        stops.extend(future.result())
    return stops
    

def printRouteStops(routeName):
    routes = getRouteList()
    for r in routes:
        if (r['route'] == routeName):
            route = r
            stops = _sync_getRouteStopsAll(route)
            for stop in stops:
                stopCode = r['route'] + "||" + stop['stopID'] + "||" + stop['stopCount'] + "||" + route['direction'] + "||" + stop['serviceCode']
                print(r['route'] + " (" + r['destName'] + "): " + stop['stopName'] + " (" + stopCode + ")")

routes = getRouteList()
print(routes[0])
services = getAllRouteServices()
print(services[0])
