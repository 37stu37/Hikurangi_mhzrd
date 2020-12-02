"""
prepare data for students
"""

import os
from pathlib import Path
import psutil
import pandas as pd
import numpy as np
import geopandas as gpd
import pandas_bokeh
pandas_bokeh.output_notebook()
pd.set_option('plotting.backend', 'pandas_bokeh')
