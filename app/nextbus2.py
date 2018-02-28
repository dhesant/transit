import secrets
import asyncio
import requests
from aiohttp import ClientSession


def getSysCode():
    return secrets.token_urlsafe(42)


def getRouteList():
    apiURL = "http://mobile.nwstbus.com.hk/api6/getroutelist2.php?rno=&l=1&syscode=" + getSysCode()

    r = requests.get(apiURL)
    routes = []
    for route in r.text.split("<br>"):
        if route == '':
            break
        raw = route.split("||")
        if len(raw) == 11:
            parsed = {
                'operator': raw[0],
                'route': raw[1],
                'destCode': raw[2],
                'serviceCount': raw[3],
                'originName': raw[4],
                'destName': raw[5],
                # 'unknown6': raw[6],
                'variantCode': raw[7],
                # 'serviceID': raw[8],
                # 'bound': raw[9],
                'remarks': raw[10].replace("|*|", "", 1),
                }
            routes.append(parsed)
        else:
            print("Unable to parse: " + str(raw))

    return routes


async def getRouteServices(route):
    async with ClientSession() as session:
        apiURL = "http://mobile.nwstbus.com.hk/api6/getvariantlist.php?id=" + route['variantCode'] + "&l=1&syscode=" + getSysCode()
        async with session.get(apiURL) as resp:
            r = await resp.text()

    services = []
    for service in r.split("<br>"):
        if service == '':
            break
        raw = service.split("||")
        if len(raw) == 5:
            splitCode = raw[4].split("***")
            parsed = {
                'route': route,
                # 'operator': splitCode[0],
                'serviceCode': splitCode[1],
                'startCount': splitCode[2],
                'endCount': splitCode[3],
                'serviceID': splitCode[4],
                'bound': splitCode[5],
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
        futures.append(asyncio.ensure_future(getRouteServices(route)))

    loop.run_until_complete(asyncio.gather(*futures))
    loop.stop()

    services = []
    for future in futures:
        services.extend(future.result())
    return services


async def getRouteStops(service):
    async with ClientSession() as session:
        info = "1|*|" + service['route']['operator'] + "||" + service['serviceCode'] + "||" + service['startCount'] + "||" + service['endCount']
        apiURL = "https://mobile.nwstbus.com.hk/api6/ppstoplist.php?info=" + info + "&l=1&syscode=" + getSysCode()
        async with session.get(apiURL) as resp:
            r = await resp.text()

    stops = []
    for stop in r.split("<br>"):
        if stop == '':
            break
        raw = stop.split("||")
        parsed = {
            'service': service,
            # 'serviceCode': raw[1],
            'stopCount': raw[2],
            'stopID': raw[3],
            'poleID': raw[4],
            'location': {
                'latitude': raw[5],
                'longitude': raw[6],
                },
            'stopName': raw[7],
            # 'destName': raw[8],
            'fares': {
                'adultFare': raw[10],
                'childFare': raw[12],
                'seniorFare': raw[13],
                },
            }
        stops.append(parsed)
    return stops


async def getRouteStopsAll(route):
    services = await getRouteServices(route)

    allStops = []
    for service in services:
        stops = await getRouteStops(service)
        allStops.extend(stops)

    return allStops


async def getNextBus(stop):
    async with ClientSession() as session:
        apiURL = "http://mobile.nwstbus.com.hk/api6/getnextbus2.php?stopid=" + stop['stopID'] + "&service_no=" + stop['service']['route']['route'] + "&removeRepeatedSuspend=Y&interval=60&l=1&bound=" + stop['service']['bound'] + "&stopseq=" + stop['stopCount'] + "&rdv=" + stop['service']['serviceCode'] + "&syscode=" + getSysCode()
        async with session.get(apiURL) as resp:
            return await resp.text()


def printRouteStops(routeName):
    routes = getRouteList()
    for r in routes:
        if r['route'] == routeName:
            route = r
            stops = runAsync(getRouteStopsAll(route))
            for stop in stops:
                stopCode = stop['service']['route']['route'] + "||" + stop['stopID'] + "||" + stop['stopCount'] + "||" + stop['service']['bound'] + "||" + stop['service']['serviceCode']
                print(stop['service']['route']['route'] + " (" + stop['service']['route']['destName'] + "): " + stop['stopName'] + " (" + stopCode + ")")


def runAsync(func):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(func)

    loop.run_until_complete(asyncio.gather(future))
    loop.close()

    return future.result()


routes = getRouteList()
print(routes[0])

r = routes[0]
v = runAsync(getRouteServices(r))
s = runAsync(getRouteStopsAll(r))
