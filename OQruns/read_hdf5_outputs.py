#%%
import h5py
from pathlib import Path
import os
import numpy as np
import pandas as pd

# %%
p = Path(r"C:\Users\alexd\oqdata")
p_out = Path(r"F:\Dropbox\Work\BigData_more100MB\Hikurangi\OQ\OQ_Hikurangi_runs_outputs")
# %%
# %%
filename = "calc_133.hdf5"
f = h5py.File(p / filename, "r")
print("Keys: %s" % f.keys())
#%%
events_arr = np.array(f['events'])
ruptures_arr = np.array(f['ruptures'])
ruptures_geometries_arr = np.array(f['rupgeoms'])
# %%
# create ruptures df from 
ruptures_df = pd.DataFrame.from_records(data=list(ruptures_arr), columns =['id','serial','srcidx','grp_id','code','n_occ','mag','rake','occurrence_rate','minlon','minlat','maxlon','maxlat','hypo','gidx1','gidx2','sx','sy'])
# %%
ruptures_df.to_csv(p_out / f'ruptures_geometries_from_{filename}.csv')
# %%
