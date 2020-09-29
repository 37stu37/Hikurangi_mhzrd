# %% codecell
from pathlib import Path
import os
from datetime import date
import re
import glob
from tqdm.notebook import tqdm
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import box
import dask.dataframe as dd
import matplotlib.pyplot as plt

pd.options.mode.chained_assignment = None

from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"

# %% codecell
dataFolder = Path('/Users/alex/Dropbox/Work/GNS/SSIF/6 Flagship_Hikurangi/PilotStudy2020_2021/Exposure/Exposure Development/HB Liquefaction_2016/building & people')
os.listdir(dataFolder)

# %% codecell
exposure = pd.read_csv(dataFolder / 'HB_BLDG_POP_final.csv')
exposure.info()

footprint = gpd.read_file(dataFolder / 'lds-nz-building-outlines-SHP' / 'nz-building-outlines.shp')
footprint.info()

# %% codecell
fig = plt.figure(figsize=(10,30))
# fig.subplots_adjust(hspace=2, wspace=2)

for c,num in zip(exposure.columns, range(1,28)):

    ax = fig.add_subplot(14,2,num)
    exposure[c].plot(kind="hist", ax=ax)
    ax.set_title(c)

plt.tight_layout()
plt.show();
# %% codecell
# plot as map
import contextily as ctx

fig = plt.figure(figsize=(10,30))

gdf = gpd.GeoDataFrame(exposure,
                       geometry=gpd.points_from_xy(exposure.NZMGE,
                                                   exposure.NZMGN))
footprintShape = gpd.GeoDataFrame(footprint)

gdf = gdf.set_crs(epsg=27200)
footprintShape = footprintShape.set_crs(epsg=27200)


ax = fig.add_subplot(1,1,1)
gdf.plot("CONST_TYPE", ax=ax)
ctx.add_basemap(crs=27200, ax=ax)

plt.show()


# %% codecell
from IPython.display import Image
print("Riskscape keys for exposure")
Image("/Users/alex/Dropbox/Screenshots/Screen Shot 2020-09-09 at 12.27.36 PM.png")
# %% codecell
# classify exposure type
conditions = [
    exposure.CONST_TYPE == 1, exposure.CONST_TYPE == 2,
    exposure.CONST_TYPE == 3, exposure.CONST_TYPE == 4,
    exposure.CONST_TYPE == 5, exposure.CONST_TYPE == 6,
    exposure.CONST_TYPE == 7, exposure.CONST_TYPE == 8,
    exposure.CONST_TYPE == 9, exposure.CONST_TYPE == 10,
    exposure.CONST_TYPE == 11, exposure.CONST_TYPE == 12
]
results = [
    "Reinforced Concrete Shear Wall",
    "Reinforced Concrete Moment Resisting Frame", "Steel Braced Frame",
    "Steel Moment Resisting Frame", "Light Timber", " Tilt Up Panel",
    " Light Industrial", " Advanced Design", "Brick Masonry",
    "Concrete Masonry", " Unknown Residential", "Unknown Commercial"
]

exposure['construction type'] = np.select(conditions,results)
# %% codecell
import seaborn as sns

ax = sns.countplot(exposure["construction type"])
ax.tick_params('x', labelrotation=90)
# %% codecell
# year of construction for timber only
timber = exposure[exposure["construction type"]=="Light Timber"]
ax = sns.distplot(timber["YEAR_CONST"])
# %% codecell
# plot replacement cost aggregated by building construction type

group = exposure.groupby(["construction type"]).sum()
group

ax = sns.barplot(x=group.index, y=group["REPLACMENT"])
ax.set_title("sum replacement cost")
ax.tick_params('x', labelrotation=90)
# %% codecell
from bokeh.plotting import figure, output_file, show
from bokeh.tile_providers import CARTODBPOSITRON, get_provider

tile_provider = get_provider(OSM)

# range bounds supplied in web mercator coordinates
p = figure(x_range=(-2000000, 6000000), y_range=(-1000000, 7000000),
           x_axis_type="mercator", y_axis_type="mercator")

show(p)
# %% codecell
