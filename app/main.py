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
    routes.append(asyncio.ensure_future(getBuses("8x", 2552)))
    routes.append(asyncio.ensure_future(getBuses("19", 2552)))
    loop.run_until_complete(asyncio.gather(*routes))
    loop.stop()

    # Compile and sort route into by vehicle ETA
    vehicles = []
    for route in routes:
        vehicles.extend(route.result())

    vehicles = sorted(vehicles, key=lambda k: k['eta'])

    for vehicle in vehicles:
        vehicle = getVehicleStatus(vehicle, datetime.today())
    
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

    vehicles = sorted(vehicles, key=lambda k: k['eta'])

    for vehicle in vehicles:
        vehicle = getVehicleStatus(vehicle, datetime.today())

    return render_template("transit.html", title="Causeway Bay", stopinfo="Times Square", vehicles=vehicles)

@app.route("/transit/tinhau")
def tinhau():
    # Generate new async loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Get various route info
    routes = []
    routes.append(asyncio.ensure_future(getTrams("40W")))
    routes.append(asyncio.ensure_future(getBuses("8x", 1214)))
    routes.append(asyncio.ensure_future(getBuses("19", 1214)))
    loop.run_until_complete(asyncio.gather(*routes))
    loop.stop()

    # Compile and sort route into by vehicle ETA
    vehicles = []
    for route in routes:
        vehicles.extend(route.result())

    vehicles = sorted(vehicles, key=lambda k: k['eta'])

    for vehicle in vehicles:
        vehicle = getVehicleStatus(vehicle, datetime.today())
    
    return render_template("transit.html", title="Tin Hau", stopinfo="Tin Hau", vehicles=vehicles)

if __name__ == "__main__":
    app.run()

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
    
    
