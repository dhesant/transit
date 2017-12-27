#!/usr/bin/python3.6
from nextram import getTrams
from nextbus import getBuses

def getTransitHVT():
    tram = getTrams("HVT")
    bus8x = getBuses("8x")
    bus19 = getBuses("19")
    
    transit = []
    
    transit = sorted(tram + bus8x + bus19, key=lambda k: k['eta'])

    return transit

#print(getTransitHVT())
