# %% Initialize
import os
import time
import config_analyse as config
from analyse.functions import get_data_from_gcpbucket, perform_data_calculations
from analyse.functions import consume

# %% Set environment variables and permissions and data path
keys = os.listdir(config.path_jsons)
for fn in keys:
    if '-d-' in fn:
        gpath_d = config.path_jsons + fn
    if '-p-' in fn:
        gpath_p = config.path_jsons + fn

# %% Get data from state collection Projects
t_start = time.time()
df_planning, df_transitielog, df_algemeen, df_vergunning, df_acties = get_data_from_gcpbucket(gpath_d, config.path_data)
print('get data: ' + str((time.time() - t_start) / 60) + ' min')

# %% Analysis of data
t_start = time.time()
df_totaal, df_kpi_1 = perform_data_calculations(df_vergunning, df_algemeen, df_planning, df_acties, df_transitielog)
print('do analyses: ' + str((time.time() - t_start) / 60) + ' min')

# %% to fill collection Graphs
t_start = time.time()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gpath_d
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gpath_p
consume(df_totaal, config.col)
print('write to Graph collection: ' + str((time.time() - t_start) / 60) + ' min')
