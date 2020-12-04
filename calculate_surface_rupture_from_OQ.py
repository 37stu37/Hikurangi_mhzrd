'''
calculate the surface rupture from OQ event based PSHA
'''

#%%
import os
from pathlib import Path
import pandas as pd
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
plt.style.reload_library()
plt.style.use('science')
plt.style.use(['science','grid', 'no-latex'])
plt.rcParams.update({'font.size': 15})


p = Path(r"/Users/alex/Dropbox/Work/BigData_more100MB/Hikurangi/OQ/HikSubduction_Data_biljana/for_Marco")

#%%
# load
ruptures = pd.read_csv(p / 'ruptures_133.csv')
geometries = pd.read_csv(p / 'ruptures_geometries_from_calc_133.hdf5.csv')
