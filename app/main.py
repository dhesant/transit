# from http://flask.pocoo.org/ tutorial
from flask import Flask, render_template
from datetime import datetime, timedelta
app = Flask(__name__)

from nextram import getTrams
from nextbus import getBuses
from math import ceil
import asyncio

@app.route("/") # take note of this decorator syntax, it's a common pattern
def index():
    return render_template("index.html")

@app.route("/transit/hvt")
def hvt():
    # Generate new async loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Get various route info
    routes = []
    routes.append(asyncio.ensure_future(getTrams("HVT")))
    routes.append(asyncio.ensure_future(getBuses("8x", "8X||002552||3||I||8X-ISR-1")))
    routes.append(asyncio.ensure_future(getBuses("19", "19||002552||8||I||19-ISR-1")))
    routes.append(asyncio.ensure_future(getBuses("1", "1||002552||6||I||1-FEV-1")))
    loop.run_until_complete(asyncio.gather(*routes))
    loop.stop()

    # Compile and sort route into by vehicle ETA
    vehicles = []
    for route in routes:
        vehicles.extend(route.result())

    vehicles = parseVehicleStream(vehicles, datetime.today())

    return render_template("transit.html", title="Happy Valley", stopinfo="Tram Terminus/Sanatorium", vehicles=vehicles)

@app.route("/transit/cwb")
def cwb():
    # Generate new async loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Get various route info
    routes = []
    routes.append(asyncio.ensure_future(getTrams("105")))
    loop.run_until_complete(asyncio.gather(*routes))
    loop.stop()

    # Compile and sort route into by vehicle ETA
    vehicles = []
    for route in routes:
        vehicles.extend(route.result())

    vehicles = parseVehicleStream(vehicles, datetime.today())

    return render_template("transit.html", title="Causeway Bay", stopinfo="Times Square", vehicles=vehicles)

@app.route("/transit/wanchai")
def wanchai():
    # Generate new async loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Get various route info
    routes = []
    routes.append(asyncio.ensure_future(getTrams("39E")))
    routes.append(asyncio.ensure_future(getBuses("1", "1||002427||22||O||1-HVU-1")))
    loop.run_until_complete(asyncio.gather(*routes))
    loop.stop()

    # Compile and sort route into by vehicle ETA
    vehicles = []
    for route in routes:
        vehicles.extend(route.result())

    vehicles = parseVehicleStream(vehicles, datetime.today())

    return render_template("transit.html", title="Wan Chai", stopinfo="Fenwick Street", vehicles=vehicles)

@app.route("/transit/central")
def central():
    # Generate new async loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Get various route info
    routes = []
    routes.append(asyncio.ensure_future(getTrams("27E")))
    routes.append(asyncio.ensure_future(getBuses("1", "1||001049||19||O||1-HVU-1")))
    loop.run_until_complete(asyncio.gather(*routes))
    loop.stop()

    # Compile and sort route into by vehicle ETA
    vehicles = []
    for route in routes:
        vehicles.extend(route.result())

    vehicles = parseVehicleStream(vehicles, datetime.today())

    return render_template("transit.html", title="Central", stopinfo="Douglas Street", vehicles=vehicles)

@app.route("/transit/tinhau")
def tinhau():
    # Generate new async loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Get various route info
    routes = []
    routes.append(asyncio.ensure_future(getTrams("40W")))
    routes.append(asyncio.ensure_future(getBuses("8x", "8X||001214||23||O||8X-HVL-1")))
    routes.append(asyncio.ensure_future(getBuses("19", "19||001214||23||O||19-THR-3")))
    loop.run_until_complete(asyncio.gather(*routes))
    loop.stop()

    # Compile and sort route into by vehicle ETA
    vehicles = []
    for route in routes:
        vehicles.extend(route.result())

    vehicles = parseVehicleStream(vehicles, datetime.today())

    return render_template("transit.html", title="Tin Hau", stopinfo="Queens College", vehicles=vehicles)

@app.route("/transit/fortress")
def fortress():
    # Generate new async loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Get various route info
    routes = []
    routes.append(asyncio.ensure_future(getTrams("34W")))
    routes.append(asyncio.ensure_future(getBuses("8x", "8X||001364||20||O||8X-HVL-1")))
    routes.append(asyncio.ensure_future(getBuses("19", "19||001364||20||O||19-THR-3")))
    loop.run_until_complete(asyncio.gather(*routes))
    loop.stop()

    # Compile and sort route into by vehicle ETA
    vehicles = []
    for route in routes:
        vehicles.extend(route.result())

    vehicles = parseVehicleStream(vehicles, datetime.today())

    return render_template("transit.html", title="Fortress Hill", stopinfo="King's Road", vehicles=vehicles)

@app.route("/transit/syp")
def syp():
    # Generate new async loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Get various route info
    routes = []
    routes.append(asyncio.ensure_future(getTrams("09E")))
    routes.append(asyncio.ensure_future(getBuses("1", "1||001061||12||O||1-HVU-1")))
    loop.run_until_complete(asyncio.gather(*routes))
    loop.stop()

    # Compile and sort route into by vehicle ETA
    vehicles = []
    for route in routes:
        vehicles.extend(route.result())

    vehicles = parseVehicleStream(vehicles, datetime.today())

    return render_template("transit.html", title="Sai Ying Pun", stopinfo="Hill Road", vehicles=vehicles)

if __name__ == "__main__":
    app.run()

def parseVehicleStream(vehicles, time):
    v2 = []
    for vehicle in vehicles:
        if ((vehicle['eta'] - time) <= timedelta(minutes=30)):
            v2.append(getVehicleStatus(vehicle, time))

    return sorted(v2, key=lambda k: k['eta'])

def getVehicleStatus(vehicle, time):
    if vehicle['isArrived']:
        if vehicle['isLast']:
            vehicle['status'] = "Arrived (Last Vehicle)"
        else:
            vehicle['status'] = "Arrived"
    else:
        dtime = vehicle['eta'] - time
        vehicle['status'] = "In " + str(ceil(dtime.total_seconds() / 60)) + " Minutes"

    return vehicle
    
    
