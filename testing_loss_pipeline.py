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
RV = np.linspace(0.01,1e6,sampling_size) # asset value
PGAs = np.random.uniform(0.01, 5, size=sampling_size)
WDepths = np.random.uniform(0.01, 10, size=sampling_size)

# Earthquake timber house
Dr_PGA = 0.5*(special.erfc((-(np.log(PGAs)-mu)/(sigma*np.sqrt(2)))))
Dr_PGA_uncertainty = np.array([np.random.normal(loc=x, scale=sigma_uncertainty, size=sampling_size) for x in Dr_PGA])
# Tsunami timber house
mu, sigma=0.281424, 0.78294657
Dr_Wdepth =  0.5*(special.erfc((-(np.log(WDepths)-mu)/(sigma*np.sqrt(2)))))
Dr_Wdepth_uncertainty = np.array([np.random.normal(loc=x, scale=sigma_uncertainty, size=sampling_size) for x in Dr_Wdepth])
# error bars (assuming non symetry)
residual_PGA_dr = Dr_PGA_uncertainty.max(axis=1) -  Dr_PGA_uncertainty.mean(axis=1)
residual_Wdepth_dr = Dr_Wdepth_uncertainty.max(axis=1) -  Dr_Wdepth_uncertainty.mean(axis=1)
# residual_PGA_dr = np.vstack(((Dr_PGA-Dr_PGA_uncertainty.min(axis=1)), (Dr_PGA_uncertainty.max(axis=1) - Dr_PGA)))
# residual_Wdepth_dr = np.vstack(((Dr_Wdepth-Dr_Wdepth_uncertainty.min(axis=1)), (Dr_Wdepth_uncertainty.max(axis=1) - Dr_Wdepth)))

#%%
# Alex reduction in Replacement Value
## losses from EQ (need to add dimension to RV to handle uncertainties)
RV_eq = RV[:,None] * Dr_PGA_uncertainty
RV_eq_ts = (RV[:,None] - RV_eq) * Dr_Wdepth_uncertainty # cascade
# Jose's combined Dr
Dr_combined_capped = np.where(Dr_PGA_uncertainty > Dr_Wdepth_uncertainty, Dr_PGA_uncertainty, Dr_Wdepth_uncertainty-Dr_PGA_uncertainty)
residual_Dr_combined = Dr_combined_capped.max(axis=1) - Dr_combined_capped.mean(axis=1)
RV_combined = RV[:,None] * Dr_combined_capped
# Max value - Christina
Dr_combined_max = np.where(Dr_PGA_uncertainty > Dr_Wdepth_uncertainty, Dr_PGA_uncertainty, Dr_Wdepth_uncertainty)
residual_Dr_max = Dr_combined_max.max(axis=1) - Dr_combined_max.mean(axis=1)
RV_max = RV[:,None] * Dr_combined_max

#%%
# Dr plot
fig, axes = plt.subplots(nrows=3,ncols=3, figsize=(14,8))
axes[0,0].errorbar(PGAs, Dr_PGA_uncertainty.mean(axis=1), residual_PGA_dr, fmt='.r',label='PGA damage ratio', errorevery=1)
axes[0,1].errorbar(WDepths, Dr_Wdepth_uncertainty.mean(axis=1), residual_Wdepth_dr, fmt='.b', label='Water depths damage ratio', errorevery=1)
axes[0,2].hist(np.concatenate((Dr_PGA_uncertainty, Dr_Wdepth_uncertainty)).flatten(), color='black', label='Combined damage ratio - capped')
axes[1,0].errorbar(PGAs, Dr_PGA_uncertainty.mean(axis=1), residual_PGA_dr, fmt='.r',label='PGA damage ratio', errorevery=1)
axes[1,1].errorbar(WDepths, Dr_combined_capped.mean(axis=1), residual_Dr_combined, fmt='.g', label='Combined damage ratio - capped', errorevery=1)
axes[1,2].hist(Dr_combined_capped.flatten(), color='black', label='Combined damage ratio - capped')
axes[2,0].errorbar(PGAs, Dr_PGA_uncertainty.mean(axis=1), residual_PGA_dr, fmt='.r',label='PGA damage ratio', errorevery=1)
axes[2,1].errorbar(WDepths, Dr_combined_max.mean(axis=1), residual_Dr_max, fmt='.g', label='Combined damage ratio - max', errorevery=1)
axes[2,2].hist(Dr_combined_max.flatten(), color='black', label='Combined damage ratio - max')
axes[0,0].legend(framealpha=1, frameon=True, loc='upper left')
axes[0,1].legend(framealpha=1, frameon=True, loc='lower right')
axes[1,0].legend(framealpha=1, frameon=True, loc='upper left')
axes[1,1].legend(framealpha=1, frameon=True, loc='lower right')
axes[2,0].legend(framealpha=1, frameon=True, loc='upper left')
axes[2,1].legend(framealpha=1, frameon=True, loc='lower right')

plt.tight_layout()
plt.show()
plt.close()

#%%
# Losses plot
fig, axes = plt.subplots(nrows=1,ncols=1, figsize=(9,5))
axes.hist(RV_eq.flatten(), alpha=0.3, color="r", label='losses Earthquake')
axes.hist(RV_eq_ts.flatten(), alpha=0.3, color="b", label='losses Earthquake and Tsunamis - loss pipeline')
# axes.hist(RV_combined.flatten(), alpha=0.3, color="g", label='losses Earthquake and Tsunamis - Dr combined')
# axes.hist(RV_max.flatten(), alpha=0.3, color="y", label='losses Earthquake and Tsunamis - Dr max')
axes.set_xlabel('Losses')
axes.set_ylabel('Count')
plt.legend()
plt.show()
plt.close()


#%%
# Jose reduction in Damage ratios
## Dr from Earthquake
Dr_combined_capped = np.where(Dr_PGA_uncertainty > Dr_Wdepth_uncertainty, Dr_PGA_uncertainty, Dr_Wdepth_uncertainty-Dr_PGA_uncertainty) # use mask value as min Dr2 = max Dr1 np.where ?

plt.hist(Dr_combined_capped)
plt.show()
