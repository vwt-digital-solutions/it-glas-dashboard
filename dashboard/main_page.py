# Import required libraries
import pandas as pd
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import plotly.graph_objs as go
import dash_table
import api
from dash.dependencies import Input, Output, State
from elements import table_styles
from elements import site_colors
from app import app
from dash.exceptions import PreventUpdate
import flask
from flask import send_file
import io
import datetime as dt

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(le=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
)


# Layout of the app
def get_body():
    page_content = html.Div(
        [
            dcc.Store
            (
                id='graph_clickdata', data={'graph1': [-1, -1],
                                            'graph2': [-1, -1],
                                            'graph3': [-1, -1]
                                            }
            ),
            dcc.Store
            (
                id='current_shown_graph', data=None
            ),
            dcc.Store
            (
                id='businessline', data=None
            ),
            dcc.Store
            (
                id='regiovwt', data=None
            ),
            dcc.Store
            (
                id='checklist', data=None
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Div(  # Filter businessline
                                [
                                    html.Img(
                                        src=app.get_asset_url("ODH_logo_original.png"),
                                        id="odh-image",
                                        style={
                                            "height": "100px",
                                            "width": "auto",
                                            "margin-bottom": "25px",
                                        },
                                    ),
                                    dbc.Label('Businessline'),
                                    dcc.Dropdown(
                                        id='filter_businessline',
                                        options=[
                                            {'label': 'BL: Glas KPN', 'value': 'BL Glas KPN'},
                                            {'label': 'BL: Infratechniek', 'value': 'Infratechniek'}
                                        ],
                                        value=['BL Glas KPN', 'Infratechniek'],
                                        multi=True,
                                    ),
                                    html.Br(),
                                    dbc.Label('Regio VWT'),
                                    dcc.Dropdown(
                                        id='filter_regiovwt',
                                        options=[
                                            {'label': 'Infra ZuidOost', 'value': 'Infra ZuidOost'},
                                            {'label': 'Infra ZuidWest', 'value': 'Infra ZuidWest'},
                                            {'label': 'Infra NoordWest', 'value': 'Infra NoordWest'}
                                        ],
                                        value=['Infra ZuidOost', 'Infra ZuidWest', 'Infra NoordWest'],
                                        multi=True,
                                        style={
                                            'font-size': '2005'
                                        }
                                    ),
                                    html.Br(),
                                    html.Br(),
                                    html.Br(),

                                    dbc.Checklist(
                                        id='checklist_filter',
                                        options=[
                                            {
                                                'label': 'Intrekkingen niet meenemen',
                                                'value': 'intrekkingen'
                                            },
                                            {
                                                'label': 'Maandorders niet meenemen',
                                                'value': 'maandorders'
                                            },
                                            {
                                                'label': 'Intern on hold niet meenemen',
                                                'value': 'on_hold'
                                            },
                                            {
                                                'label': 'Gearchiveerd niet meenemen',
                                                'value': 'archief'
                                            }
                                        ],
                                        value=['intrekkingen', 'maandorders', 'on_hold'],
                                    )

                                ],
                                className='pretty_container column'
                            ),
                        ],
                        className='container-display'
                    ),
                    html.Div(  # Overzicht totaal aantal projecten
                        [
                            html.Div(
                                [
                                    html.H3('Overzicht totaal aantal projecten'),
                                ],
                                className='flex-row',
                                style={
                                    'textAlign': 'center'
                                }
                            ),
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            dcc.Graph(id='graph_overzicht'),
                                            html.Button('Algemene uitleg dashboard'),
                                        ],
                                        className='half columns',
                                    ),
                                ],
                                className='container-display',
                                style={
                                    'height': 500,
                                    'width': 1000,
                                },
                            )
                        ],
                        className='pretty_container column',
                    ),
                        ],
                className="container-display",
                    ),

            html.Div(  # Horizontaal KPI overzicht
                [
                    html.Div(  # Graph KPI1
                        [
                                html.Div(
                                    [
                                        html.H3('KPI 1: Intake - TG datum afgegeven'),
                                    ],
                                    className='pretty_container_title',
                                    style={
                                        'textAlign': 'center'
                                    }
                                ),
                                html.Div(
                                    [
                                        dcc.Graph(id='graph_kpi1')
                                    ],
                                ),
                        ],
                        className='pretty_container column',
                    ),
                    html.Div(  # Graph KPI2
                        [
                            html.Div(
                                [
                                    html.H3('KPI 2: LLD - TG datum'),
                                ],
                                className='pretty_container_title',
                                style={
                                    'textAlign': 'center'
                                }
                            ),
                            html.Div(
                                [
                                    dcc.Graph(id='graph_kpi2')
                                ],
                            ),
                        ],
                        className='pretty_container column',
                    ),
                    html.Div(  # Graph KPI3
                        [
                            html.Div(
                                    [
                                        html.H4('KPI 3: TG - TG_TAG (20 days)'),
                                    ],
                                    className='pretty_container_title',
                                    style={
                                        'textAlign': 'center'
                                    }
                                ),
                            html.Div(
                                [
                                    dcc.Graph(id='graph_kpi3')
                                ],
                            ),
                        ],
                        className='pretty_container column',
                    ),
                ],
                className='container-display',
            ),

            html.Div(  # Tabel
                [
                    html.Div(
                        [
                            html.H3('Geselecteerde projecten'),
                        ],
                        className='flex-row',
                        style={
                            'textAlign': 'center'
                        }
                    ),
                    html.Div(
                        [
                            html.Div(
                                id='table_kpi',
                                className='twelve columns',
                                style={'align': 'center'},
                            ),
                        ],
                        className='container-display',
                    ),
                    html.Button(
                        html.A(
                            'download excel (selected projects)',
                            id='download-link1_h',
                            href="""/download_excel1_b
                                  ?filters=['empty']""",
                            style={"text-decoration": "none"}
                        ),
                        id='download_button'
                    ),
                ],
                className='pretty_container column',
            ),
        ],
        className=''
    )
    return page_content


# helper functions barchart
def create_bar_chart_colors(df, _groupby, _indexes, kleur_kpi, width):

    df_totaal = df.copy()

    layout = go.Layout(
        bargap=0.01,
        bargroupgap=0.0,
        paper_bgcolor='rgb(0,0,0,0)',
        plot_bgcolor='rgb(0,0,0,0)',
        showlegend=False,
        barmode='stack',
        titlefont={
            'size': 20,
        },
        font={
            'size': 13,
        },
        xaxis={
            'showgrid': False,
            'zeroline': False,
            'side': 'top',
            'title': 'Aantal projecten',
        },
        title={
            'text': 'Doorloop projecten t.a.v. planning (ideale doorloop)',
            'y': 0.98,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )

    df = df_totaal.loc[df_totaal.Hoofdstatus != 'Gereed', :]
    rode_balk = df.loc[df[kleur_kpi] == 'Rood'].groupby(_groupby)[kleur_kpi].count()
    gele_balk = df.loc[df[kleur_kpi] == 'Geel'].groupby(_groupby)[kleur_kpi].count()
    groene_balk = df.loc[df[kleur_kpi] == 'Groen'].groupby(_groupby)[kleur_kpi].count()

    rode_balk = rode_balk.reindex(_indexes).fillna(0).copy()
    gele_balk = gele_balk.reindex(_indexes).fillna(0).copy()
    groene_balk = groene_balk.reindex(_indexes).fillna(0).copy()

    return go.Figure(
        data=[
            go.Bar(
                x=groene_balk.values,
                y=groene_balk.index,
                name='In time',
                orientation='h',
                marker_color='green',
                opacity=0.8,
                width=width
            ),
            go.Bar(
                x=gele_balk.values,
                y=gele_balk.index,
                name='Take a look',
                orientation='h',
                marker_color='orange',
                opacity=0.8,
                width=width
            ),
            go.Bar(
                x=rode_balk.values,
                y=rode_balk.index,
                name='Overdue',
                orientation='h',
                marker_color='red',
                opacity=0.8,
                width=width
            )
        ],
        layout=layout,
    )


# helper function table
def generate_table(df):
    tabel = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict("rows"),
        style_table={
            'overflowX': 'auto',
            'overflowY': 'auto',
            'height': 450,
        },
        fixed_rows={
            'headers': True,
        },
        fixed_columns={
            'headers': True, 'data': 1
        },
        style_cell_conditional=create_conditional_style(df),
        style_header=table_styles['header'],
        style_cell=table_styles['cell']['action'],
        style_filter=table_styles['filter'],
        css=[{"selector": '.dash-spreadsheet .row', "rule": 'flex-wrap: nowrap;'},
             {"selector": '.dash-spreadsheet.dash-freeze-left', "rule": 'max-width: none !important;'}]
    )
    return tabel


# helper function filter dropdown ß
def get_df():
    # docs = firestore.Client().collection('Projects').where('project', '==', 'FttB').stream()
    # records = []
    # for doc in docs:
    #     records += [doc.to_dict()]
    # df = pd.DataFrame(records)
    df = pd.DataFrame(api.get('/Projects?project=FttB'))
    return df


def apply_filters(df, filter_businessline, filter_regiovwt, checklist_filter):

    df = df[df['BL'].isin(filter_businessline)]
    df = df[df['RegioVWT'].isin(filter_regiovwt)]
    if 'maandorders' in checklist_filter:
        df = df[df['MaandOrder'] != 'Ja']
    if 'intrekkingen' in checklist_filter:
        df = df[~df['Projectkenmerk'].isin(['INTR', 'Change', 'Create INTR', 'Change INTR'])]
    if 'on_hold' in checklist_filter:
        df = df[df['WF_Status'] != 'F_Intern_On_Hold']
    if 'archief' in checklist_filter:
        df = df[df['WF_Status'] != 'G_Archief']

    return df


# helper function table header width
def create_conditional_style(df):
    style = []
    for col in df.columns:
        name_length = len(col)
        pixel = 50 + round(name_length*7)
        pixel = str(pixel) + "px"
        style.append({'if': {'column_id': col}, 'minWidth': pixel})
    return style


# callback Graph overzicht
@app.callback(
    Output('graph_overzicht', 'figure'),
    [
        Input('filter_businessline', 'value'),
        Input('filter_regiovwt', 'value'),
        Input('checklist_filter', 'value'),
    ]
)
def return_graph_overzicht(filter_businessline, filter_regiovwt, checklist_filter):

    # read df
    df = get_df()

    # apply filters
    df = apply_filters(df, filter_businessline, filter_regiovwt, checklist_filter)

    # if no data is available then:
    if df.empty:
        return []

    # make bar chart
    layout = go.Layout(
        bargap=0.00,
        bargroupgap=0.0,
        paper_bgcolor='rgb(0,0,0,0)',
        plot_bgcolor='rgb(0,0,0,0)',
        showlegend=False,
        # barmode='group',
        titlefont={
            'size': 20,
        },
        font={
            'size': 13,
        },
        xaxis={
            'showgrid': False,
            'zeroline': False,
            # 'side': 'bottom',
            'title': 'Aantal projecten',
        },
        title={
            'text': 'Overzicht hoofdfases Workflow',
            'y': 0.98,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )

    df = df.loc[df.Hoofdstatus != 'Gereed', :]
    balk = df.groupby('Hoofdstatus')['Hoofdstatus'].count()
    balk = balk.reindex(['Intake', 'LLD', 'Werkvoorbereiding', 'Uitvoering', 'As_Built']).fillna(0).copy()

    return go.Figure(
        data=[
            go.Bar(
                x=balk.index,
                y=balk.values,
                name='Overzicht',
                orientation='v',
                marker_color=site_colors['indigo'],
                opacity=0.7,
                width=0.5
            ),
        ],
        layout=layout,
    )

# # businessline
# # regiovwt
# # checklist
# @app.callback(
#     [
#         Output('businessline', 'data')
#     ],
#     [
#         Input('filter_businessline', 'value'),
#     ]
# )
# def store_businessline(filter_businessline):
#     return filter_businessline

# @app.callback(
#     [
#         Output('regiovwt', 'data')
#     ],
#     [
#         Input('filter_regiovwt', 'value'),
#     ]
# )
# def store_businessline(filter_regiovwt):
#     return filter_regiovwt

# @app.callback(
#     [
#         Output('checklist', 'data')
#     ],
#     [
#         Input('checklist', 'value'),
#     ]
# )
# def store_businessline(checklist_filter):
#     return checklist_filter


# callback Graph KPI1
@app.callback(
    Output('graph_kpi1', 'figure'),
    [
        Input('filter_businessline', 'value'),
        Input('filter_regiovwt', 'value'),
        Input('checklist_filter', 'value'),
    ]
)
def return_graph_kpi1(filter_businessline, filter_regiovwt, checklist_filter):

    # read df
    df = get_df()

    # apply filters
    df = apply_filters(df, filter_businessline, filter_regiovwt, checklist_filter)

    # if no data is available then:
    if df.empty:
        return []

    # make bar chart
    _groupby = 'Hoofdstatus'
    _indexes = ['Intake']
    kleur_kpi = 'Kleur_KPI_1'
    barchart = create_bar_chart_colors(df, _groupby=_groupby, _indexes=_indexes, kleur_kpi=kleur_kpi, width=0.12)

    return barchart


def get_clickdata(graphs_clickdata):
    graph_clicks = {}
    clicked = False
    for graph, data in graphs_clickdata.items():
        if data is not None:
            graph_clicks[graph] = [
                                    data['points'][0]['curveNumber'],
                                    data['points'][0]['pointNumber']
                                  ]
            clicked = True
        else:
            graph_clicks[graph] = [-1, -1]
    if not clicked:
        raise PreventUpdate
    return graph_clicks


def find_changed_data(current_clickdata, stored_clickdata):
    clickdata_to_store = {}
    changed = False
    for graph, data in current_clickdata.items():
        if not data == stored_clickdata[graph]:
            changed_graph = graph
            changed = True
        clickdata_to_store[graph] = data

    if not changed:
        raise PreventUpdate
    return changed_graph, clickdata_to_store


def get_table(graph, filter_businessline, filter_regiovwt, checklist_filter, click):
    if graph == 'graph1':
        return return_table_kpi1(filter_businessline, filter_regiovwt, checklist_filter, click)
    if graph == 'graph2':
        return return_table_kpi2(filter_businessline, filter_regiovwt, checklist_filter, click)
    if graph == 'graph3':
        return return_table_kpi3(filter_businessline, filter_regiovwt, checklist_filter, click)

# Callback Tables


def create_download_link(filter_businessline, filter_regiovwt, checklist_filter, changed_graph, color, subfase):
    businesslines = ','.join(filter_businessline)
    regiovwt = ','.join(filter_regiovwt)
    checklist = ','.join(checklist_filter)
    return f""" /download_excel_{changed_graph}?businesslines={businesslines}&
                regiovwt={regiovwt}&checklist={checklist}&color={color}&subfase={subfase} """


@app.callback(
    [
        Output('table_kpi', 'children'),
        Output('graph_clickdata', 'data'),
        Output('current_shown_graph', 'data'),
        Output('download-link1_h', 'href')
    ],
    [
        Input('graph_kpi1', 'clickData'),
        Input('graph_kpi2', 'clickData'),
        Input('graph_kpi3', 'clickData'),
        Input('filter_businessline', 'value'),
        Input('filter_regiovwt', 'value'),
        Input('checklist_filter', 'value'),
    ],
    [
        State('graph_clickdata', 'data')
    ]
)
def make_table_on_click(clickdata_graph1, clickdata_graph2, clickdata_graph3, filter_businessline, filter_regiovwt,
                        checklist_filter, state):
    graphs_clickdata = {
                            'graph1': clickdata_graph1,
                            'graph2': clickdata_graph2,
                            'graph3': clickdata_graph3,
                        }
    print('creating graph')
    current_clickdata = get_clickdata(graphs_clickdata)  # Raises preventupdate if nothing has been clicked yet.
    changed_graph, clickdata_to_store = find_changed_data(current_clickdata, state)
    print(f'found that graph {changed_graph} has changed')
    changed_graph_data = graphs_clickdata[changed_graph]
    print('Creating table')
    table = make_table(changed_graph, filter_businessline, filter_regiovwt, checklist_filter, changed_graph_data)
    print('finished creating table')
    print("Getting color and subfase")
    color = get_color(graphs_clickdata[changed_graph])
    subfase = get_subfase(graphs_clickdata[changed_graph])
    print(f'color: {color}, subfase: {subfase}')
    download_link = create_download_link(filter_businessline, filter_regiovwt, checklist_filter, changed_graph, color, subfase)
    print(f'download link: {download_link}')
    return [table, clickdata_to_store, changed_graph, download_link]


def get_color(click):
    color_dict = {
        0: 'Groen',
        1: 'Geel',
        2: 'Rood'
    }

    color = click['points'][0]['curveNumber']
    color = color_dict[color]
    return color


def get_subfase(click):
    subfase = click['points'][0]['y']
    return subfase


def make_table(changed_graph, filter_businessline, filter_regiovwt, checklist_filter, graph_data):
    table = get_table(changed_graph,
                      filter_businessline,
                      filter_regiovwt,
                      checklist_filter,
                      graph_data)
    return table


def get_filename(color, subfase):
    date = dt.datetime.now().strftime('%y%m%d')
    filename = f"Download_{color}_{subfase}_{date}.xlsx"
    print(f'filename: {filename}')
    return filename


@app.server.route('/download_excel_graph1')
def download_excel_table1():
    businessline = flask.request.args.get('businesslines').split(',')
    print(businessline)
    regiovwt = flask.request.args.get('regiovwt').split(',')
    checklist = flask.request.args.get('checklist').split(',')
    color = flask.request.args.get('color')
    subfase = flask.request.args.get('subfase')

    columns = {
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
    }

    # read data
    df = get_df()
    # apply fitlers
    df = apply_filters(df, businessline, regiovwt, checklist)

    # apply click
    df = df[df['Kleur_KPI_1'] == color]
    df = df[df['Hoofdstatus'] == subfase]
    df = df[df['Hoofdstatus'] != 'Gereed']

    # get relevant columns
    df = df[columns.keys()]
    df.rename(columns=columns, inplace=True)

    # sort values
    df.sort_values('Dagen tot TG', inplace=True)

    # Convert df to excel
    strIO = io.BytesIO()
    excel_writer = pd.ExcelWriter(strIO, engine="xlsxwriter")
    df.to_excel(excel_writer, sheet_name="sheet1", index=False)
    excel_writer.save()
    strIO.getvalue()
    strIO.seek(0)

    # Name download file

    filename = get_filename(color, subfase)
    print(filename)
    return send_file(strIO,
                     attachment_filename=filename,
                     as_attachment=True)


@app.server.route('/download_excel_graph2')
def download_excel_table2():
    businessline = flask.request.args.get('businesslines').split(',')
    print(businessline)
    regiovwt = flask.request.args.get('regiovwt').split(',')
    checklist = flask.request.args.get('checklist').split(',')
    color = flask.request.args.get('color')
    subfase = flask.request.args.get('subfase')

    columns = {
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
        }

    # read data
    df = get_df()
    # apply fitlers
    df = apply_filters(df, businessline, regiovwt, checklist)

    # rename Werkvoorbereiding naar WvB
    mask = df['Hoofdstatus'] == 'Werkvoorbereiding'
    df.at[mask, 'Hoofdstatus'] = 'WvB'

    # apply click
    df = df[df['Kleur_KPI_2'] == color]
    df = df[df['Hoofdstatus'] == subfase]
    df = df[df['Hoofdstatus'] != 'Gereed']

    # get relevant columns
    df = df[columns.keys()]
    df.rename(columns=columns, inplace=True)

    # sort values
    df.sort_values('Dagen tot TG', inplace=True)

    # Convert df to excel
    strIO = io.BytesIO()
    excel_writer = pd.ExcelWriter(strIO, engine="xlsxwriter")
    df.to_excel(excel_writer, sheet_name="sheet1", index=False)
    excel_writer.save()
    strIO.getvalue()
    strIO.seek(0)

    # Name download file

    filename = get_filename(color, subfase)
    print(filename)
    return send_file(strIO,
                     attachment_filename=filename,
                     as_attachment=True)


@app.server.route('/download_excel_graph3')
def download_excel_table3():
    businessline = flask.request.args.get('businesslines').split(',')
    print(businessline)
    regiovwt = flask.request.args.get('regiovwt').split(',')
    checklist = flask.request.args.get('checklist').split(',')
    color = flask.request.args.get('color')
    subfase = flask.request.args.get('subfase')

    columns = {
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
    }

    # read data
    df = get_df()
    # apply fitlers
    df = apply_filters(df, businessline, regiovwt, checklist)

    # apply click
    df = df[df['Kleur_KPI_3'] == color]
    df = df[df['As_Built_Stage'] == subfase]
    df = df[df['Hoofdstatus'] != 'Gereed']

    # get relevant columns
    df = df[columns.keys()]
    df.rename(columns=columns, inplace=True)

    # sort values
    df.sort_values('Dagen in As Built', inplace=True, ascending=False)

    # Convert df to excel
    strIO = io.BytesIO()
    excel_writer = pd.ExcelWriter(strIO, engine="xlsxwriter")
    df.to_excel(excel_writer, sheet_name="sheet1", index=False)
    excel_writer.save()
    strIO.getvalue()
    strIO.seek(0)

    # Name download file

    filename = get_filename(color, subfase)
    print(filename)
    return send_file(strIO,
                     attachment_filename=filename,
                     as_attachment=True)


# callbak Table KPI1
# @app.callback(
#     [
#         Output('table_kpi1', 'children'),
#         Output('graph_visible', 'data')
#     ],
#     [
#         Input('filter_businessline', 'value'),
#         Input('filter_regiovwt', 'value'),
#         Input('checklist_filter', 'value'),
#         Input('graph_kpi1', 'clickData')
#     ]
# )
def return_table_kpi1(filter_businessline, filter_regiovwt, checklist_filter, click):

    color_dict = {
        0: 'Groen',
        1: 'Geel',
        2: 'Rood'
    }

    columns = {
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
    }

    if click is None:
        color = 'Groen'
        subfase = 'Intake'
    else:
        color = click['points'][0]['curveNumber']
        color = color_dict[color]
        subfase = click['points'][0]['y']

    # read data
    df = get_df()
    # apply fitlers
    df = apply_filters(df, filter_businessline, filter_regiovwt, checklist_filter)

    # apply click
    df = df[df['Kleur_KPI_1'] == color]
    df = df[df['Hoofdstatus'] == subfase]
    df = df[df['Hoofdstatus'] != 'Gereed']

    # get relevant columns
    df = df[columns.keys()]
    df.rename(columns=columns, inplace=True)

    # sort values
    df.sort_values('Dagen tot TG', inplace=True)

    # if no data is available then:
    if df.empty:
        titel = html.Label(
            'Er zijn geen projecten schikbaar',
            style={'fontSize': 20, 'textAlign': 'center'}
        )
        return [titel]

    # generate tabel
    tabel = generate_table(df)
    # generate title
    titel = html.Label(
        '{} {} is geselecteerd'.format(subfase, color),
        id='title_kpi1',
        style={'fontSize': 20, 'textAlign': 'center'}
    )

    return [titel, tabel]


# callback Graph KPI2
@app.callback(
    Output('graph_kpi2', 'figure'),
    [
        Input('filter_businessline', 'value'),
        Input('filter_regiovwt', 'value'),
        Input('checklist_filter', 'value'),
    ]
)
def return_graph_kpi2(filter_businessline, filter_regiovwt, checklist_filter):

    # read df
    df = get_df()
    # apply filters
    df = apply_filters(df, filter_businessline, filter_regiovwt, checklist_filter)

    # rename Werkvoorbereiding naar WvB
    mask = df['Hoofdstatus'] == 'Werkvoorbereiding'
    df.at[mask, 'Hoofdstatus'] = 'WvB'

    # make bar chart
    _groupby = 'Hoofdstatus'
    _indexes = ['Uitvoering', 'WvB', 'LLD']
    kleur_kpi = 'Kleur_KPI_2'
    barchart = create_bar_chart_colors(df, _groupby=_groupby, _indexes=_indexes, kleur_kpi=kleur_kpi, width=0.35)

    return barchart


# # callbak Table KPI2
# @app.callback(
#     Output('table_kpi2', 'children'),
#     [
#         Input('filter_businessline', 'value'),
#         Input('filter_regiovwt', 'value'),
#         Input('checklist_filter', 'value'),
#         Input('graph_kpi2', 'clickData')
#     ]
# )
def return_table_kpi2(filter_businessline, filter_regiovwt, checklist_filter, click):

    color_dict = {
        0: 'Groen',
        1: 'Geel',
        2: 'Rood'
    }

    columns = {
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
        }

    if click is None:
        color = 'Groen'
        subfase = 'Uitvoering'
    else:
        color = click['points'][0]['curveNumber']
        color = color_dict[color]
        subfase = click['points'][0]['y']

    # read data
    df = get_df()
    # apply fitlers
    df = apply_filters(df, filter_businessline, filter_regiovwt, checklist_filter)

    # rename Werkvoorbereiding naar WvB
    mask = df['Hoofdstatus'] == 'Werkvoorbereiding'
    df.at[mask, 'Hoofdstatus'] = 'WvB'

    # apply click
    df = df[df['Kleur_KPI_2'] == color]
    df = df[df['Hoofdstatus'] == subfase]
    df = df[df['Hoofdstatus'] != 'Gereed']

    # get relevant columns
    df = df[columns.keys()]
    df.rename(columns=columns, inplace=True)

    # sort values
    df.sort_values('Dagen tot TG', inplace=True)

    # generate tabel
    tabel = generate_table(df)
    # generate title
    titel = html.Label(
        '{} {} is geselecteerd'.format(subfase, color),
        style={'fontSize': 20, 'textAlign': 'center'}
    )

    return [titel, tabel]


# callback Graph KPI3
@app.callback(
    Output('graph_kpi3', 'figure'),
    [
        Input('filter_businessline', 'value'),
        Input('filter_regiovwt', 'value'),
        Input('checklist_filter', 'value'),
    ]
)
def return_graph_kpi3(filter_businessline, filter_regiovwt, checklist_filter):

    # read df
    df = get_df()
    # apply filters
    df = apply_filters(df, filter_businessline, filter_regiovwt, checklist_filter)

    # make bar chart
    _groupby = 'As_Built_Stage'
    _indexes = ['As_Built_4', 'As_Built_3', 'As_Built_2', 'As_Built_1']
    kleur_kpi = 'Kleur_KPI_3'
    barchart = create_bar_chart_colors(df, _groupby=_groupby, _indexes=_indexes, kleur_kpi=kleur_kpi, width=0.5)

    return barchart


# callbak Table KPI3
# @app.callback(
#     Output('table_kpi3', 'children'),
#     [
#         Input('filter_businessline', 'value'),
#         Input('filter_regiovwt', 'value'),
#         Input('checklist_filter', 'value'),
#         Input('graph_kpi3', 'clickData')
#     ]
# )
def return_table_kpi3(filter_businessline, filter_regiovwt, checklist_filter, click):

    color_dict = {
        0: 'Groen',
        1: 'Geel',
        2: 'Rood'
    }

    columns = {
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
    }

    if click is None:
        color = 'Groen'
        subfase = 'As_Built_1'
    else:
        color = click['points'][0]['curveNumber']
        color = color_dict[color]
        subfase = click['points'][0]['y']

    # read data
    df = get_df()
    # apply fitlers
    df = apply_filters(df, filter_businessline, filter_regiovwt, checklist_filter)

    # apply click
    df = df[df['Kleur_KPI_3'] == color]
    df = df[df['As_Built_Stage'] == subfase]
    df = df[df['Hoofdstatus'] != 'Gereed']

    # get relevant columns
    df = df[columns.keys()]
    df.rename(columns=columns, inplace=True)

    # sort values
    df.sort_values('Dagen in As Built', inplace=True, ascending=False)

    # generate tabel
    tabel = generate_table(df)
    # generate title
    titel = html.Label(
        '{} {} is geselecteerd'.format(subfase, color),
        style={'fontSize': 20, 'textAlign': 'center'}
    )
    return [titel, tabel]
