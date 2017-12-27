# from http://flask.pocoo.org/ tutorial
from flask import Flask, render_template
from datetime import datetime, timedelta
app = Flask(__name__)

from nextram import getTrams
from nextbus import getBuses

@app.route("/") # take note of this decorator syntax, it's a common pattern
def index():
    return render_template("index.html")

@app.route("/hvt")
def hvt():
    vehicles = sorted(getTrams("HVT") + getBuses("8x") + getBuses("19"), key=lambda k: k['eta'])

    now = datetime.today()
    for vehicle in vehicles:
        if vehicle['isArrived']:
            vehicle['status'] = "Arrived"
        else:
            dtime = vehicle['eta'] - now
            vehicle['status'] = "In " + str(int(dtime.total_seconds() / 60)) + " Minutes"
    
    return render_template("transit.html", title="Happy Valley", stopinfo="Tram Terminus/Sanatorium", vehicles=vehicles)

@app.route("/cwb")
def cwb():
    vehicles = sorted(getTrams("105"), key=lambda k: k['eta'])

    now = datetime.today()
    for vehicle in vehicles:
        if vehicle['isArrived']:
            vehicle['status'] = "Arrived"
        else:
            dtime = vehicle['eta'] - now
            vehicle['status'] = "In " + str(int(dtime.total_seconds() / 60)) + " Minutes"
    
    return render_template("transit.html", title="Causeway Bay", stopinfo="Times Square", vehicles=vehicles)

@app.route("/tinhau")
def tinhau():
    vehicles = sorted(getTrams("59E"), key=lambda k: k['eta'])

    now = datetime.today()
    for vehicle in vehicles:
        if vehicle['isArrived']:
            vehicle['status'] = "Arrived"
        else:
            dtime = vehicle['eta'] - now
            vehicle['status'] = "In " + str(int(dtime.total_seconds() / 60)) + " Minutes"
    
    return render_template("transit.html", title="Causeway Bay", stopinfo="Times Square", vehicles=vehicles)

if __name__ == "__main__":
    app.run()

