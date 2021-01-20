'''
calculate the surface rupture from OQ event based PSHA
'''
#%%
from geopy.point import Point
from rasterio.plot import show
import contextily as ctx
import os
from pathlib import Path
import pandas as pd
import numpy as np
from tqdm import tqdm
import geopy
import geopy.distance
import rasterio as rio
from rasterio.plot import plotting_extent
from rasterio.plot import show
import geopandas as gpd

import matplotlib.pyplot as plt
plt.style.reload_library()
plt.style.use('science')
plt.style.use(['science','grid', 'no-latex'])
plt.rcParams.update({'font.size': 15})

p = Path(Path.cwd().parents[1] / 'BigData_more100MB/Hikurangi/OQ/OQ_Hikurangi_runs_outputs/runs_Strasser')

#%%
# load
ruptures = pd.read_csv(p / 'ruptures_142.csv')
#%%
# using Strasser 2010 ("Scaling of the Source Dimensions of Interface and Intraslab Subduction-zone Earthquakes with Moment Magnitude")
# ruptures['area'] = 10.0 ** (-2.87 + 0.82 * ruptures['mag']) # Wells and Coppersmith 1994
ruptures['area'] = 10**(-3.225 + 0.890 * ruptures['mag'])
ruptures['length'] = 10**(-2.350 + 0.562 * ruptures['mag'])
ruptures['width'] = 10**(-1.058 + 0.356 * ruptures['mag'])
# calcuate the seismic moment
ruptures['Mo'] = 10**(1.5*(ruptures['mag']) + 10.7)
# calculate fault displacement 
# rigidity in kbar and Depth in km based on Bilek 1999 correlation with 1kbar = 1e8 Pa
# Mo = rigidity (Pa) * Area (m2) * slip (m)
ruptures['rigidity'] = 35.961*np.exp(0.0858*ruptures['centroid_depth'])
ruptures['fault_displacement'] = ruptures['Mo'] / ((ruptures['area']*1e6) * (ruptures['rigidity']*1e8))

#%%
ruptures.to_csv(p / 'ruptures_142_w_dims.csv')

#%%