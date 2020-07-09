kpi1 = {
                'title':            'KPI 1: Intake - TG datum afgegeven',
                'graph_id':         'graph_kpi1',
                'subfase_column':   'Hoofdstatus',
                'sort_column':      'Dagen tot TG',
                'columns':          {
                                        'BAAN_nr': 'Project nummer',
                                        'Projectnaam': 'Project naam',
                                        'Substatus': 'Substatus',
                                        'Uitv_GS': 'Uitvoering geplande start',
                                        'Uitv_GE': 'TG Datum',
                                        'Dagen_tot_planning': 'Dagen tot TG',
                                        'Bodemonderzoek_Afgerond': 'Bodemonderzoek afgerond',
                                        'Openstaande_SISU_Actie': 'Openstaande actie',
                                        'Openstaande_Vergunning_Aanvraag': 'Openstaande vergunning aanvraag',
                                        'Vergunningsoort': 'Vergunning soort',
                                        'Aantal_dagen_sinds_vergunning_aanvraag': 'Dagen openstaande vergunning aanvraag',
                                        'Terug_in_WF': 'Nr. bounces',
                                    },
                'Kleur_KPI':    'Kleur_KPI_1',
                'indices':      ['Intake'],
                'width':            0.12
            }

kpi2 = {
                'title':            'KPI 2: LLD - TG datum',
                'graph_id':         'graph_kpi2',
                'subfase_column':   'Hoofdstatus',
                'sort_column':      'Dagen tot TG',
                'columns':          {
                                        'BAAN_nr': 'Project nummer',
                                        'Projectnaam': 'Project naam',
                                        'Substatus': 'Substatus',
                                        'Uitv_GS': 'Uitvoering geplande start',
                                        'Uitv_GE': 'TG Datum',
                                        'Dagen_tot_planning': 'Dagen tot TG',
                                        'Bodemonderzoek_Afgerond': 'Bodemonderzoek afgerond',
                                        'Openstaande_SISU_Actie': 'Openstaande actie',
                                        'Openstaande_Vergunning_Aanvraag': 'Openstaande vergunning aanvraag',
                                        'Vergunningsoort': 'Vergunning soort',
                                        'Aantal_dagen_sinds_vergunning_aanvraag': 'Dagen openstaande vergunning aanvraag',
                                        'Terug_in_WF': 'Nr. bounces',
                                        'Hoofdstatus': 'Hoofdstatus',
                                    },
                'Kleur_KPI':        'Kleur_KPI_2',
                'indices':          ['Uitvoering', 'WvB', 'LLD'],
                'width':            0.35
            }
kpi3 = {
                'title':            'KPI 3: TG - TG_TAG (20 days)',
                'graph_id':         'graph_kpi3',
                'subfase_column':   'As_Built_Stage',
                'sort_column':      'Dagen in As Built',
                'columns':          {
                                        'BAAN_nr': 'Project nummer',
                                        'Projectnaam': 'Project naam',
                                        'Substatus': 'Substatus',
                                        'Totaal_dagen_in_As_Built_Stage': 'Dagen in As Built',
                                        'Bodemonderzoek_Afgerond': 'Bodemonderzoek afgerond',
                                        'Openstaande_SISU_Actie': 'Openstaande actie',
                                        'Openstaande_Vergunning_Aanvraag': 'Openstaande vergunning aanvraag',
                                        'Vergunningsoort': 'Vergunning soort',
                                        'Terug_in_WF': 'Nr. bounces',
                                        'Kleur_KPI_3': 'Kleur_KPI_3',
                                        'WF_Status': 'WF_Status',
                                        'MaandOrder': 'MaandOrder',
                                        'RegioVWT': 'RegioVWT',
                                        'As_Built_Stage': 'As_Built_Stage'
                                    },
                'Kleur_KPI':        'Kleur_KPI_3',
                'indices':          ['As_Built_4', 'As_Built_3', 'As_Built_2', 'As_Built_1'],
                'width':            0.5
            }

config = {
            'kpi1': kpi1,
            'kpi2': kpi2,
            'kpi3': kpi3
        }
