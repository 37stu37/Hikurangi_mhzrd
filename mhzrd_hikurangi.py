import pandas as pd
import numpy as np
import os

def Earthquake():
    # select a source area to trigger an earthquake
    # sample the probability magnitude relationship log(N) = a-bMw
    # generate shaking from Openquake maps

def Landslide():
    # get the shaking at node location
    # get the landslide suscpetibility
    # sample from the area / volume relationship
    # get a volume and runout + target node

def Tsunami():
    # where is the source ?
    # calculate Ht for all target areas (Bij) using the Earthquake Mw Ht = 10^Mw-Bij
    # from the distance to shore value, calculate the Water depth Wd = (Ht*2) - (distance from shore in meters/400)


