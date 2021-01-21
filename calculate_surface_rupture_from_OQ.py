'''
calculate the surface rupture from OQ event based PSHA
'''
#%%
from pathlib import Path
import pandas as pd
import numpy as np

# import rasterio as rio
# from rasterio.plot import plotting_extent
# from rasterio.plot import show
import matplotlib.pyplot as plt
plt.style.reload_library()
plt.style.use('science')
plt.style.use(['science','grid', 'no-latex'])
plt.rcParams.update({'font.size': 15})

p = Path(Path.cwd().parents[1] / 'BigData_more100MB/Hikurangi/OQ/OQ_Hikurangi_runs_outputs/runs_Strasser')
ruptures_file = p / 'ruptures_148.csv'
#%%
# load
ruptures = pd.read_csv(ruptures_file, skiprows=1)
#%%
# using Strasser 2010 ("Scaling of the Source Dimensions of Interface and Intraslab Subduction-zone Earthquakes with Moment Magnitude")
# ruptures['area'] = 10.0 ** (-2.87 + 0.82 * ruptures['mag']) # Wells and Coppersmith 1994
ruptures['area'] = 10**(-3.225 + 0.890 * ruptures['mag'])
ruptures['length'] = 10**(-2.350 + 0.562 * ruptures['mag'])
ruptures['width'] = 10**(-1.058 + 0.356 * ruptures['mag'])
ruptures['rake'] = 90
# calcuate the seismic moment
ruptures['Mo'] = 10**(1.5*(ruptures['mag']) + 10.7) # N/m
# calculate fault displacement
# rigidity in kbar and Depth in km based on Bilek 1999 correlation with 1kbar = 1e8 Pa; 1kbar = 1e8 N/m2
# Mo = rigidity (Pa) * Area (m2) * slip (m) (https://www.ucl.ac.uk/EarthSci/people/sammonds/6%20Seismic%20moment.pdf)
ruptures['rigidity'] = 35.961*np.exp(0.0858*ruptures['centroid_depth'])
ruptures['fault_displacement'] = ruptures['Mo'] / ((ruptures['area']*1e6) * (ruptures['rigidity']*1e8))

#%%
ruptures['MD'] = 10**((ruptures['mag'] - 6.69) / 0.74)
#%%
ruptures.to_csv(p / f'{ruptures_file.stem}_dims.csv')

#%%
# Plot
hik_raster = rio.open(p.parents[1] / 'faultGeometry' / 'hik_res_0.1.tif')

fig, axis = plt.subplots(2, figsize=(15, 10), sharex=True)

axis.scatter(ruptures.centroid_lon, rup)
gdf_ruptures.plot(ax=axis[0], column='mag', marker='^',
                  cmap='YlOrRd', legend=True, alpha=0.5, edgecolors='black', markersize=50)

gdf_crest.plot(ax=axis[1], column='mag', c=None, cmap='YlOrRd', legend=True,
               alpha=0.5, edgecolors='black', markersize=50)

# add basemaps
# ctx.add_basemap(axis[0], crs=4326)
# ctx.add_basemap(axis[1], crs=4326)

# add raster hikurangi margin
show(src, ax=axis[0])

# Defining custom 'xlim' and 'ylim' values.
custom_xlim = (171, 180)
# custom_ylim = (-40, -39)

# Setting the values for all axes.
plt.setp(axis[0], xlim=custom_xlim) #, ylim=custom_ylim)
plt.setp(axis[1], xlim=custom_xlim) #, ylim=custom_ylim)

# titles for subplots
axis[0].title.set_text('Hypocenters')
axis[1].title.set_text('Rupture crests')
plt.tight_layout()
plt.show()
# %%
