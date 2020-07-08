import os
import config_analyse
from analyse.functions import get_data_from_gcpbucket, perform_data_calculations
from analyse.functions import make_plots_dashboard, consume


def analyse():
    # Get data from state collection Projects
    df_planning, df_transitielog, df_algemeen, df_vergunning, df_acties = get_data_from_gcpbucket(None, os.getcwd() + '/../data/')

    # Analysis
    df_totaal, df_kpi_1 = perform_data_calculations(df_vergunning, df_algemeen, df_planning, df_acties, df_transitielog)

    # to fill collection Graphs
    make_plots_dashboard(df_totaal, df_kpi_1)
    consume(df_totaal, config_analyse.col)
