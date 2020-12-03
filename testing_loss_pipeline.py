'''
sample multi-hazard loss thourgh pipeline approach
'''

import os
from pathlib import Path
import pandas as pd
import numpy as np
from tqdm import tqdm
from scipy import special

import matplotlib.pyplot as plt
plt.style.reload_library()
plt.style.use('science')
plt.style.use(['science','grid', 'no-latex'])
plt.rcParams.update({'font.size': 15})


# pipeline

## damage ratios -------------------------------------
#%%
mu, sigma, sigma_uncertainty, sampling_size =1.2909968, 0.1688, 0.05, 100
RV = np.linspace(0.01,1e6,100) # asset value
PGAs = np.random.uniform(0.01, 5, size=100)
WDepths = np.random.uniform(0.01, 10, size=100)

# Earthquake timber house
Dr_PGA = 0.5*(special.erfc((-(np.log(PGAs)-mu)/(sigma*np.sqrt(2)))))
Dr_PGA_uncertainty = np.array([np.random.normal(loc=x, scale=sigma_uncertainty, size=sampling_size) for x in Dr_PGA])
# Tsunami timber house
mu, sigma=0.281424, 0.78294657
Dr_Wdepth =  0.5*(special.erfc((-(np.log(WDepths)-mu)/(sigma*np.sqrt(2)))))
Dr_Wdepth_uncertainty = np.array([np.random.normal(loc=x, scale=sigma_uncertainty, size=sampling_size) for x in Dr_Wdepth])
# error bars (assuming non symetry)
residual_PGA_dr = np.vstack(((Dr_PGA-Dr_PGA_uncertainty.min(axis=1)), (Dr_PGA_uncertainty.max(axis=1) - Dr_PGA)))
residual_Wdepth_dr = np.vstack(((Dr_Wdepth-Dr_Wdepth_uncertainty.min(axis=1)), (Dr_Wdepth_uncertainty.max(axis=1) - Dr_Wdepth)))

#%%
fig, axes = plt.subplots(nrows=1,ncols=2, figsize=(8,5))
axes[0].errorbar(PGAs, Dr_PGA, residual_PGA_dr, fmt='.r',label='PGA damage ratio', errorevery=1)
axes[1].errorbar(WDepths, Dr_Wdepth, residual_Wdepth_dr, fmt='.b', label='Water depths damage ratio', errorevery=1)
axes[0].legend()
axes[1].legend()
plt.tight_layout()
plt.show()
plt.close()

#%%
# Alex reduction in Replacement Value
## losses from EQ (need to add dimension to RV to handle uncertainties)
RV_eq = RV[:,None] * Dr_PGA_uncertainty
RV_eq_ts = (RV[:,None] - RV_eq) * Dr_Wdepth_uncertainty # cascade

# error bars (assuming non symetry)
residual_RV_eq = np.vstack(((RV_eq.mean(axis=1)-RV_eq.min(axis=1)), (RV_eq.max(axis=1)-RV_eq.mean(axis=1))))
residual_RV_eq_ts = np.vstack(((RV_eq_ts.mean(axis=1)-RV_eq_ts.min(axis=1)), (RV_eq_ts.max(axis=1)-RV_eq_ts.mean(axis=1))))

#%%
fig, axes = plt.subplots(nrows=1,ncols=2, figsize=(9,5))
axes[0].errorbar(PGAs, RV_eq.mean(axis=1), residual_RV_eq, fmt='.r',label='losses Earthquake', errorevery=1)
axes[1].errorbar(WDepths, RV_eq.mean(axis=1), residual_RV_eq_ts, fmt='.b', label='losses Earthquake and Tsunamis', errorevery=1)
axes[0].set_xlabel('PGA (g)')
axes[1].set_xlabel('Water Depth (m)')
axes[0].legend()
axes[1].legend()
axes[0].set_ylabel('Losses')
plt.legend()
plt.tight_layout()
plt.show()
plt.close()

#%%
fig, axes = plt.subplots(nrows=1,ncols=1, figsize=(9,5))
axes.hist(np.flatten(RV_eq), alpha=0.5, color="r", label='losses Earthquake')
axes.hist(RV_eq_ts.mean(axis=1), alpha=0.5, color="b", label='losses Earthquake and Tsunamis')
axes.set_xlabel('Losses')
axes.set_ylabel('Count')
plt.legend()
plt.show()
plt.close()


# Jose reduction in Damage ratios
## Dr from Earthquake
Dr_combined_capped = np.where(Dr_PGA_uncertainty > Dr_Wdepth_uncertainty, Dr_PGA_uncertainty, Dr_Wdepth_uncertainty-Dr_PGA_uncertainty) # use mask value as min Dr2 = max Dr1 np.where ?

plt.hist(Dr_combined_capped)
plt.show()
