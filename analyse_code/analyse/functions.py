import pandas as pd
import numpy as np
from google.cloud import firestore, storage
import datetime
import os


def get_data_from_gcpbucket(gpath, path_data):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = gpath
    fn_l = os.listdir(path_data)
    for fn in fn_l:
        os.remove(path_data + fn)
    client = storage.Client()
    bucket = client.get_bucket('vwt-d-gew1-it-glas-dashboard-datadump-stg')
    blobs = bucket.list_blobs()
    for blob in blobs:
        blob.download_to_filename(path_data + blob.name.split('/')[-1])
    fn_l = os.listdir(path_data)

    df_planning = pd.read_excel(path_data + fn_l[0], sheet_name='planning')
    df_transitielog = pd.read_excel(path_data + fn_l[0], sheet_name='transitielog')
    df_algemeen = pd.read_excel(path_data + fn_l[0], sheet_name='algemeen')
    df_vergunning = pd.read_excel(path_data + fn_l[0], sheet_name='vergunning')
    df_acties = pd.read_excel(path_data + fn_l[0], sheet_name='acties')

    os.remove(path_data + fn_l[0])

    return df_planning, df_transitielog, df_algemeen, df_vergunning, df_acties


def perform_data_calculations(df_vergunning, df_algemeen, df_planning, df_acties, df_transitielog):
    now = datetime.datetime.now()

    df_vergunning = df_vergunning[['WorkflowID', 'ProjectNummer', 'Vergunningsoort', 'Aangevraagd',
                                   'DatumAangevraagd', 'DatumOntvangen']]
    df_vergunning = df_vergunning.rename(columns={'WorkflowID': 'WF_nr', 'ProjectNummer': 'BAAN_nr',
                                                  'DatumAangevraagd': 'Datum_Vergunning_Aangevraagd',
                                                  'Aangevraagd': 'Vergunning_Aangevraagd',
                                                  'DatumOntvangen': 'Datum_Vergunning_Ontvangen'})
    vergunning_col = ['Datum_Vergunning_Aangevraagd', 'Datum_Vergunning_Ontvangen']
    df_vergunning[vergunning_col] = df_vergunning[vergunning_col].apply(pd.to_datetime, errors='coerce', format='%Y-%m-%d')

    df_algemeen = df_algemeen[['WorkflowID', 'ProjectNummer', 'AanvraagDatum', 'BL',
                               'Status', 'PMCCode', 'PMCOmschrijving', 'RegioVWT',
                               'MaandOrder', 'VergunningVereist', 'Projectkenmerk']]
    df_algemeen = df_algemeen.rename(columns={'WorkflowID': 'WF_nr', 'ProjectNummer': 'BAAN_nr', 'Status': 'WF_Status'})
    df_algemeen[['AanvraagDatum']] = df_algemeen[['AanvraagDatum']].apply(pd.to_datetime, errors='coerce', format='%Y-%m-%d')

    df_planning = df_planning[['Verversdatum', 'WF_nr', 'BAAN_nr', 'Projectnaam', 'Hoofdstatus',
                               'Substatus', 'Uitv_GS', 'Uitv_GE', 'Uitv_WS', 'Uitv_WE']]
    planning_col = ['Uitv_GS', 'Uitv_GE', 'Uitv_WS', 'Uitv_WE']
    df_planning[planning_col] = df_planning[planning_col].apply(pd.to_datetime, errors='coerce', format='%Y-%m-%d')

    df_acties = df_acties[['WFID', 'ProjectNummer', 'Aangemaakt', 'ActieType', 'StartDatum', 'EindDatum', 'OpleverDatum', 'Status']]
    df_acties = df_acties.rename(columns={'WFID': 'WF_nr', 'ProjectNummer': 'BAAN_nr', 'Aangemaakt': 'Datum_Actie_Aangemaakt',
                                          'StartDatum': 'Actie_StartDatum',
                                          'EindDatum': 'Actie_EindDatum', 'OpleverDatum': 'Actie_OpleverDatum',
                                          'Status': 'Actie_Status'})
    acties_col = ['Actie_StartDatum', 'Actie_EindDatum', 'Actie_OpleverDatum']
    df_acties[acties_col] = df_acties[acties_col].apply(pd.to_datetime, errors='coerce', format='%Y-%m-%d')

    df_transitielog = df_transitielog[['Projectnummer', 'VanStatus',
                                       'NaarStatus', 'WF_nr', 'createdDate']].rename(columns={'Projectnummer': 'BAAN_nr'})

    # Prepare df_vergunning_open
    df_vergunning_open = df_vergunning.loc[((df_vergunning.Datum_Vergunning_Aangevraagd.notnull()) &
                                           (df_vergunning.Datum_Vergunning_Ontvangen.isnull())), :]
    df_vergunning_open_agg = pd.DataFrame(df_vergunning_open.groupby(['WF_nr', 'BAAN_nr'])['Vergunningsoort'].apply(lambda x: ','.join(x)))
    df_vergunning_open = df_vergunning_open.merge(df_vergunning_open_agg, on=['WF_nr', 'BAAN_nr'], how='left')

    df_vergunning_open = df_vergunning_open.loc[df_vergunning_open.groupby(['WF_nr', 'BAAN_nr']).Datum_Vergunning_Aangevraagd.idxmin()]
    vergunning_aanv = 'Aantal_dagen_sinds_vergunning_aanvraag'
    df_vergunning_open[vergunning_aanv] = now - df_vergunning_open.Datum_Vergunning_Aangevraagd
    df_vergunning_open[vergunning_aanv] = (df_vergunning_open[vergunning_aanv].fillna(0) / np.timedelta64(1, 'D')).astype(int)

    df_vergunning_open = df_vergunning_open[['WF_nr', 'BAAN_nr', 'Vergunningsoort_x', 'Vergunning_Aangevraagd',
                                             'Datum_Vergunning_Aangevraagd', 'Datum_Vergunning_Ontvangen',
                                             'Aantal_dagen_sinds_vergunning_aanvraag']]
    df_vergunning_open = df_vergunning_open.rename(columns={'Vergunningsoort_x': 'Vergunningsoort'})
    df_vergunning_open['Openstaande_Vergunning_Aanvraag'] = np.where(df_vergunning_open.Vergunningsoort.notnull(), 1, None)

    # Prepare df_acties
    Acties_Interesse = ['Verwerken SISU', 'Uitvoeren SISU', 'Inplannen SISU', 'Inplannen SISU WOK', 'Aanvragen bodemonderzoek']
    df_open_acties = df_acties.loc[df_acties.ActieType.isin(Acties_Interesse), :]
    df_open_acties = df_open_acties.loc[((df_open_acties.Actie_EindDatum.isnull()) &
                                        (~df_open_acties.Actie_Status.isin(['Afgerond', 'Vervallen']))), :]

    # Prepare bodemonderzoek
    df_bodemonderzoek = df_acties.loc[df_acties.ActieType == 'Aanvragen bodemonderzoek', :]
    df_bodemonderzoek = df_bodemonderzoek.loc[df_bodemonderzoek.groupby(['WF_nr', 'BAAN_nr']).Datum_Actie_Aangemaakt.idxmax()]

    df_bodemonderzoek['Bodemonderzoek_Aangevraagd'] = np.where((df_bodemonderzoek.Actie_StartDatum.notnull()), '1', '0').astype('int')
    df_bodemonderzoek['Bodemonderzoek_Afgerond'] = np.where((df_bodemonderzoek.Actie_EindDatum.isnull()), '0', '1').astype('int')

    bo_aanv_col = ['WF_nr', 'BAAN_nr', 'Bodemonderzoek_Aangevraagd']
    bo_afr_col = ['WF_nr', 'BAAN_nr', 'Bodemonderzoek_Afgerond']
    df_bodemonderzoek_aanvraag = df_bodemonderzoek.groupby(bo_aanv_col)[bo_aanv_col].transform('max').drop_duplicates()
    df_bodemonderzoek_afronding = df_bodemonderzoek.groupby(bo_afr_col)[bo_afr_col].transform('max').drop_duplicates()

    # Prepare site surveys
    Acties_SISU = [
        'Verwerken SISU',
        'Uitvoeren SISU',
        'Inplannen SISU',
        'Inplannen SISU WOK',
    ]

    df_sisu = df_acties.loc[df_acties.ActieType.isin(Acties_SISU), :]
    df_sisu = df_sisu.loc[~(df_sisu.Actie_Status.isin(['Vervallen', 'D_Afgerond'])), :]
    df_sisu['Openstaande_SISU_Actie'] = np.where((df_sisu.Actie_EindDatum.isnull()), 1, 0)
    sisu_col = ['WF_nr', 'BAAN_nr', 'Openstaande_SISU_Actie']
    df_sisu_openstaand = df_sisu.groupby(sisu_col)[sisu_col].transform('max')

    # Perform merges
    df_planning = df_planning.merge(df_bodemonderzoek_aanvraag, on=['WF_nr', 'BAAN_nr'], how='left')
    df_planning = df_planning.merge(df_bodemonderzoek_afronding, on=['WF_nr', 'BAAN_nr'], how='left')
    df_planning = df_planning.merge(df_sisu_openstaand, on=['WF_nr', 'BAAN_nr'], how='left')
    df_planning = df_planning.merge(df_vergunning_open, on=['WF_nr', 'BAAN_nr'], how='left')

    # Prepare df_planning
    df_planning['TG_Datum_Gehaald'] = ''
    df_planning['TG_Datum_Gehaald'] = np.where((df_planning['Uitv_WE'] <= df_planning['Uitv_GE']), 'Ja', 'Nee')

    # Add Kleuren for KPI 2
    df_planning['Dagen_tot_planning'] = df_planning.Uitv_GE - now
    df_planning['Dagen_tot_planning'] = (df_planning['Dagen_tot_planning'].fillna(0) / np.timedelta64(1, 'D')).astype(int)

    df_planning['Kleur_KPI_2'] = np.where((~df_planning.Hoofdstatus.isin(['Gereed', 'As_Built', 'Intake'])), 'Rood', None)

    Geel_KPI_2 = (
        (df_planning.Hoofdstatus == 'Intake') & (df_planning.Dagen_tot_planning.between(50, 100)) |
        (df_planning.Hoofdstatus == 'LLD') & (df_planning.Dagen_tot_planning.between(40, 50)) |
        (df_planning.Hoofdstatus == 'Werkvoorbereiding') & (df_planning.Dagen_tot_planning.between(30, 40)) |
        (df_planning.Hoofdstatus == 'Uitvoering') & (df_planning.Dagen_tot_planning.between(20, 30))
    )

    Groen_KPI_2 = (
        (df_planning.Hoofdstatus == 'Intake') & (df_planning.Dagen_tot_planning > 50) |
        (df_planning.Hoofdstatus == 'LLD') & (df_planning.Dagen_tot_planning > 40) |
        (df_planning.Hoofdstatus == 'Werkvoorbereiding') & (df_planning.Dagen_tot_planning > 30) |
        (df_planning.Hoofdstatus == 'Uitvoering') & (df_planning.Dagen_tot_planning > 20)
    )

    df_planning.loc[Groen_KPI_2, 'Kleur_KPI_2'] = 'Groen'
    df_planning.loc[Geel_KPI_2, 'Kleur_KPI_2'] = 'Geel'

    # Prepare df_transitielog
    df_transitielog = df_transitielog[['BAAN_nr', 'VanStatus', 'NaarStatus', 'WF_nr', 'createdDate']]

    # Add As_Built stages for KPI 3
    As_Built_1 = [
        'Verzamelen revisie',
        'Controleren revisie',
    ]

    As_Built_2 = [
        'Inplannen As-Built',
        'Opstellen As-Built NL',
        'Opstellen As-Built India',
    ]

    As_Built_3 = [
        'Kwaliteitscontrole As-Built',
        'Controleren verkoopwaarde',
        'Accorderen extrawerk door klant',
    ]

    As_Built_4 = [
        'Indienen POD bij klant',
        'Accorderen POD door klant',
        'Opleveren project',
    ]

    df_transitielog.As_Built_Stage = ''

    df_transitielog.loc[df_transitielog.NaarStatus.isin(As_Built_1), 'As_Built_Stage'] = 'As_Built_1'
    df_transitielog.loc[df_transitielog.NaarStatus.isin(As_Built_2), 'As_Built_Stage'] = 'As_Built_2'
    df_transitielog.loc[df_transitielog.NaarStatus.isin(As_Built_3), 'As_Built_Stage'] = 'As_Built_3'
    df_transitielog.loc[df_transitielog.NaarStatus.isin(As_Built_4), 'As_Built_Stage'] = 'As_Built_4'

    # Add workflow number to df_transitielog
    WF_Mapping = {
        'intake': 10,
        'intake controle': 15,
        'inplannen hld': 20,
        'opstellen hld': 30,
        'manplanning concept': 40,
        'projectplanning': 50,
        'opstellen calculatie en werkbegroting': 60,
        'accorderen offerte door klant': 70,
        'inplannen lld': 80,
        'opstellen lld nl': 85,
        'opstellen lld india': 85,
        'kwaliteitscontrole lld': 90,
        'ontvangen werkmap engineering': 100,
        'manplanning definitief': 110,
        'samenstellen productiemap': 120,
        'uitvoering': 130,
        'verzamelen revisie': 140,
        'controleren revisie': 150,
        'inplannen as-built': 160,
        'opstellen as-built nl': 165,
        'opstellen as-built india': 165,
        'kwaliteitscontrole as-built': 170,
        'controleren verkoopwaarde': 180,
        'accorderen extrawerk door klant': 190,
        'indienen pod bij klant': 200,
        'accorderen pod door klant': 210,
        'opleveren project': 220,
        'gereed': 300,
        'project gereed': 300,
        'project gefactureerd': 1000
    }

    df_transitielog.VanStatus = df_transitielog.VanStatus.str.lower()
    df_transitielog.NaarStatus = df_transitielog.NaarStatus.str.lower()

    df_transitielog['Van_Status_Nummer'] = df_transitielog.VanStatus.map(WF_Mapping)
    df_transitielog['Naar_Status_Nummer'] = df_transitielog.NaarStatus.map(WF_Mapping)

    df_transitielog['Verschil_Status_Nummer'] = df_transitielog.Naar_Status_Nummer - df_transitielog.Van_Status_Nummer

    df_transitielog['Terug_in_WF'] = np.where((df_transitielog['Verschil_Status_Nummer'] < 0), 1, 0)
    df_transitielog['Terug_in_WF'] = df_transitielog.groupby(['WF_nr', 'BAAN_nr'])['Terug_in_WF'].transform('sum')

    # Add columns for TG dagen in fase to df_transitielog
    df_kpi3 = df_transitielog.sort_values(by=['WF_nr', 'createdDate', 'As_Built_Stage'])
    kpi3_col = 'Dagen_tot_volgende_As_Built_Stage'
    df_kpi3[kpi3_col] = df_kpi3.loc[df_kpi3.As_Built_Stage.notnull()].groupby(['WF_nr', 'BAAN_nr'])['createdDate'].diff()
    df_kpi3[kpi3_col] = (df_kpi3.Dagen_tot_volgende_As_Built_Stage / np.timedelta64(1, 'D')).fillna(0).astype(int)
    df_kpi3['Totaal_dagen_in_As_Built_Stage'] = df_kpi3.groupby(['WF_nr', 'BAAN_nr', 'As_Built_Stage'])[kpi3_col].transform('sum')
    df_kpi3 = df_kpi3.loc[(df_kpi3.groupby(['WF_nr', 'BAAN_nr']).createdDate.idxmax()), :]

    # Add kleur to df_transitielog
    df_kpi3['Kleur_KPI_3'] = 'Rood'

    Groen_KPI_3 = (
        (df_kpi3.As_Built_Stage == 'As_Built_1') & (df_kpi3.Totaal_dagen_in_As_Built_Stage < 5) |
        (df_kpi3.As_Built_Stage == 'As_Built_2') & (df_kpi3.Totaal_dagen_in_As_Built_Stage < 3) |
        (df_kpi3.As_Built_Stage == 'As_Built_3') & (df_kpi3.Totaal_dagen_in_As_Built_Stage < 3) |
        (df_kpi3.As_Built_Stage == 'As_Built_4') & (df_kpi3.Totaal_dagen_in_As_Built_Stage < 1)
    )

    Geel_KPI_3 = (
        (df_kpi3.As_Built_Stage == 'As_Built_1') & (df_kpi3.Totaal_dagen_in_As_Built_Stage.isin([6, 7])) |
        (df_kpi3.As_Built_Stage == 'As_Built_2') & (df_kpi3.Totaal_dagen_in_As_Built_Stage.isin([4, 5])) |
        (df_kpi3.As_Built_Stage == 'As_Built_3') & (df_kpi3.Totaal_dagen_in_As_Built_Stage.isin([4, 5])) |
        (df_kpi3.As_Built_Stage == 'As_Built_4') & (df_kpi3.Totaal_dagen_in_As_Built_Stage.isin([2, 3]))
    )

    df_kpi3.loc[Groen_KPI_3, 'Kleur_KPI_3'] = 'Groen'
    df_kpi3.loc[Geel_KPI_3, 'Kleur_KPI_3'] = 'Geel'

    df_totaal = df_planning.merge(df_kpi3, on=['WF_nr', 'BAAN_nr'], how='left')
    df_totaal = df_totaal.merge(df_algemeen, on=['WF_nr', 'BAAN_nr'], how='left')
    df_totaal = df_totaal.drop_duplicates()

    # Add kleur for KPI1
    df_kpi_1 = df_totaal[['WF_nr', 'BAAN_nr', 'Hoofdstatus', 'AanvraagDatum', 'Uitv_GE']].copy()
    df_kpi_1 = df_kpi_1.loc[df_kpi_1.Hoofdstatus == 'Intake', :]

    df_kpi_1['Dagen_Sinds_Project_Aanvraag'] = now - df_kpi_1.AanvraagDatum
    df_kpi_1['Dagen_Sinds_Project_Aanvraag'] = (df_kpi_1['Dagen_Sinds_Project_Aanvraag'].fillna(0) / np.timedelta64(1, 'D')).astype(int)

    df_kpi_1['Kleur_KPI_1'] = 'Rood'

    Groen_KPI_1 = (
        (df_kpi_1.Uitv_GE.notnull()) |
        (df_kpi_1.Dagen_Sinds_Project_Aanvraag < 10)
    )

    Geel_KPI_1 = (
        ((df_kpi_1.Dagen_Sinds_Project_Aanvraag > 10) & (df_kpi_1.Dagen_Sinds_Project_Aanvraag < 15))
    )

    df_kpi_1.loc[Groen_KPI_1, 'Kleur_KPI_1'] = 'Groen'
    df_kpi_1.loc[Geel_KPI_1, 'Kleur_KPI_1'] = 'Geel'

    df_totaal = df_totaal.merge(df_kpi_1[['WF_nr', 'BAAN_nr', 'Kleur_KPI_1']], on=['WF_nr', 'BAAN_nr'], how='left')
    df_totaal = df_totaal.loc[df_totaal.Hoofdstatus != 'Gereed', :]

    return df_totaal, df_kpi_1


def make_plots_dashboard(df_totaal, df_kpi_1):
    # Plot KPI 1
    red_bar = float(df_kpi_1.loc[df_kpi_1.Kleur_KPI_1 == 'Rood']['Kleur_KPI_1'].count())
    yellow_bar = float(df_kpi_1.loc[df_kpi_1.Kleur_KPI_1 == 'Geel']['Kleur_KPI_1'].count())
    green_bar = float(df_kpi_1.loc[df_kpi_1.Kleur_KPI_1 == 'Groen']['Kleur_KPI_1'].count())
    labels = ['Goed verloop', 'Onzeker verloop', 'Foutief verloop']
    bar0 = dict(x=labels,
                y=[green_bar] + [yellow_bar] + [red_bar],
                type='bar',
                marker=dict(color=['rgb(0, 200, 0)', 'rgb(200, 200, 0)', 'rgb(200, 0, 0)']),
                width=1,
                )
    fig = dict(data=[bar0],
               layout=dict(barmode='stack',
                           clickmode='event+select',
                           showlegend=False,
                           height=350,
                           orientation='h',
                           ))
    record = dict(id='graph_KPI1', figure=fig)
    firestore.Client().collection('Graphs').document(record['id']).set(record)

    # Plot KPI2
    df_werk = df_totaal.loc[((df_totaal.Uitv_WE.isnull()) & (df_totaal.Uitv_GE.notnull()) & (df_totaal.Hoofdstatus != 'Gereed')), :]
    red_bar = df_werk.loc[df_werk.Kleur_KPI_2 == 'Rood'].groupby('Hoofdstatus')['Kleur_KPI_2'].count()
    yellow_bar = df_werk.loc[df_werk.Kleur_KPI_2 == 'Geel'].groupby('Hoofdstatus')['Kleur_KPI_2'].count()
    green_bar = df_werk.loc[df_werk.Kleur_KPI_2 == 'Groen'].groupby('Hoofdstatus')['Kleur_KPI_2'].count()
    red_bar = red_bar.reindex(['LLD', 'Werkvoorbereiding', 'Uitvoering']).fillna(0).copy()
    yellow_bar = yellow_bar.reindex(['LLD', 'Werkvoorbereiding', 'Uitvoering']).fillna(0).copy()
    green_bar = green_bar.reindex(['LLD', 'Werkvoorbereiding', 'Uitvoering']).fillna(0).copy()
    labels = ['LLD', 'Werkvoorbereiding', 'Uitvoering']
    bar_green = dict(x=labels,
                     y=list(green_bar),
                     type='bar',
                     marker=dict(color=['rgb(0, 200, 0)']),
                     width=1,
                     )
    bar_yellow = dict(x=labels,
                      y=list(yellow_bar),
                      type='bar',
                      marker=dict(color=['rgb(200, 200, 0)']),
                      width=1,
                      )
    bar_red = dict(x=labels,
                   y=list(red_bar),
                   type='bar',
                   marker=dict(color=['rgb(200, 0, 0)']),
                   width=1,
                   )
    fig = dict(data=[bar_green, bar_yellow, bar_red],
               layout=dict(barmode='stack',
                           clickmode='event+select',
                           showlegend=False,
                           height=350,
                           ))
    record = dict(id='graph_KPI2', figure=fig)
    firestore.Client().collection('Graphs').document(record['id']).set(record)

    # Plot KPI3
    df_tg_tag = df_totaal.loc[df_totaal.Hoofdstatus != 'Gereed', :]
    rode_balk = df_tg_tag.loc[df_tg_tag.Kleur_KPI_3 == 'Rood'].groupby('As_Built_Stage')['Kleur_KPI_3'].count()
    gele_balk = df_tg_tag.loc[df_tg_tag.Kleur_KPI_3 == 'Geel'].groupby('As_Built_Stage')['Kleur_KPI_3'].count()
    groene_balk = df_tg_tag.loc[df_tg_tag.Kleur_KPI_3 == 'Groen'].groupby('As_Built_Stage')['Kleur_KPI_3'].count()
    rode_balk = rode_balk.reindex(['As_Built_1', 'As_Built_2', 'As_Built_3', 'As_Built_4']).fillna(0).copy()
    gele_balk = gele_balk.reindex(['As_Built_1', 'As_Built_2', 'As_Built_3', 'As_Built_4']).fillna(0).copy()
    groene_balk = groene_balk.reindex(['As_Built_1', 'As_Built_2', 'As_Built_3', 'As_Built_4']).fillna(0).copy()
    labels = ['As_Built_1', 'As_Built_2', 'As_Built_3', 'As_Built_4']
    bar_green = dict(x=labels,
                     y=list(groene_balk),
                     type='bar',
                     marker=dict(color=['rgb(0, 200, 0)']),
                     width=1,
                     )
    bar_yellow = dict(x=labels,
                      y=list(gele_balk),
                      type='bar',
                      marker=dict(color=['rgb(200, 200, 0)']),
                      width=1,
                      )
    bar_red = dict(x=labels,
                   y=list(rode_balk),
                   type='bar',
                   marker=dict(color=['rgb(200, 0, 0)']),
                   width=1,
                   )
    fig = dict(data=[bar_green, bar_yellow, bar_red],
               layout=dict(barmode='stack',
                           clickmode='event+select',
                           showlegend=False,
                           height=350,
                           ))
    record = dict(id='graph_KPI3', figure=fig)
    firestore.Client().collection('Graphs').document(record['id']).set(record)


def consume(df, col):
    df = df[col]
    df.replace({pd.NaT: np.nan}, inplace=True)
    records = df.to_dict('records')
    batch = firestore.Client().batch()
    for i, row in enumerate(records):
        record = row
        record['id'] = str(row['WF_nr'])
        record['project'] = 'FttB'
        batch.set(firestore.Client().collection('Projects').document(record['id']), record)
        if (i + 1) % 500 == 0:
            batch.commit()
