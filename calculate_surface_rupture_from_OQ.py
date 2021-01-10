'''
calculate the surface rupture from OQ event based PSHA
'''

#%%
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

import matplotlib.pyplot as plt
plt.style.reload_library()
plt.style.use('science')
plt.style.use(['science','grid', 'no-latex'])
plt.rcParams.update({'font.size': 15})

p = Path(Path.cwd().parents[1] / 'BigData_more100MB/Hikurangi/OQ/OQ_Hikurangi_runs_outputs/runs_Strasser')

#%%
# load
ruptures = pd.read_csv(p / 'ruptures_139.csv')
#%%
# using Strasser 2010 ("Scaling of the Source Dimensions of Interface and Intraslab Subduction-zone Earthquakes with Moment Magnitude")
# ruptures['area'] = 10.0 ** (-2.87 + 0.82 * ruptures['mag']) # Wells and Coppersmith 1994
ruptures['area'] = 10**(-3.225 + 0.890 * ruptures['mag'])
ruptures['length'] = 10**(-2.350 + 0.562 * ruptures['mag'])
ruptures['width'] = 10**(-1.058 + 0.356 * ruptures['mag'])

#%%
# spatial parameters
lat = ruptures['centroid_lat'].values
lon = ruptures['centroid_lon'].values

#%%
Dx = ruptures['width'].values / 2 #np.array(ruptures['centroid_depth'] / np.arctan(ruptures['dip'])) # should be close to half the width
# crest depth of the floating ruptures
Dz = ruptures['centroid_depth'].values - (np.arctan(ruptures['dip']) * Dx) 
# remove negative values
Dz[Dz < 0] = 0 
# crest centroid positions
hypocenters = np.array([geopy.Point(y, x) for y,x in zip(lat, lon)])
# distance to crest in geopy
distances_to_fault_crest = np.array([geopy.distance.distance(kilometers=d) for d in Dx])
# bearing from hypocenter to crest centroid
# bearings = np.array(180 - (360 - ruptures['strike']))
bearings = np.full((283, ), 135)
# getting centroid crests by translating hypocenters
fault_crest_centroid = np.array([d.destination(point=p, bearing=s) for d,p,s in zip(distances_to_fault_crest,hypocenters,bearings)])

#%%
# extract new x,y location
crest_x = []
crest_y = []

for idx, value in enumerate(fault_crest_centroid):
    y = fault_crest_centroid[idx][0]
    x = fault_crest_centroid[idx][1]
    crest_x.append(x)
    crest_y.append(y)

crest_x = np.array(crest_x)
crest_y = np.array(crest_y)
crest_z = np.array(Dz)

#%%
src = rio.open(p.parents[1] / 'faultGeometry' / 'hik_res_0.1.tif')

fig = plt.figure(figsize=(12,6))
ax0 = fig.add_subplot(1, 1, 1)
ax0.scatter(lon,lat, c="red", marker='^')
ax0.scatter(crest_x, crest_y, c='blue')
# show(src, ax=ax0)
ctx.add_basemap(ax0, crs=4326)
# ax0.set_ylim(-40,-39)
# ax0.set_xlim(171, 180)
plt.tight_layout()
plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=None)
plt.show()

# fig = plt.figure(figsize=(12,6))
# ax1 = fig.add_subplot(1, 1, 1, projection='3d')
# ax1.scatter(ruptures['centroid_lon'], ruptures['centroid_lat'], -1*(ruptures['centroid_depth']), c='red', marker='^')
# ax1.scatter(crest_x, crest_y, -1*(crest_z), c='blue')
# ax1.set_xlabel('X')
# ax1.set_ylabel('Y')
# ax1.set_zlabel('Z')
# # rotate the axes and update
# ax1.view_init(30, 45)
# ax1.set_xlim(171, 180)

plt.tight_layout()
plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=None, hspace=None)
plt.show()
#%%
crest_df = pd.DataFrame({'lon': crest_x, 'lat': crest_y, 'depth': crest_z, 'mag':ruptures['mag']})
crest_df.to_csv(p / 'centroid_crest.csv')
# %%
ax = plt.subplot(111, projection='polar')
ax.set_theta_zero_location('N')
ax.set_theta_direction(-1)  # clockwise
ax.grid(True)
plt.show()
# %%
