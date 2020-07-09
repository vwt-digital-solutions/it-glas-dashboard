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
from kpi_mapping import config

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(le=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
)


def get_body():
    page_content = html.Div(
        [
            dcc.Store
            (
                id='graph_clickdata', data=dict((k, [-1, -1]) for k in config.keys())
            ),
            html.Div(
                [
                    html.Div(  # Dropdowns en plaatjes
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
                                        ],
                                        className='half columns',
                                    ),
                                ],
                                className='container-display',
                            )
                        ],
                        className='pretty_container column',
                    ),
                ],
                className="container-display",
            ),
            html.Div(
                [get_graph_html(kpi) for kpi in config.keys()],
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


def get_graph_html(kpi_number):
    kpi = Kpi(kpi_number)
    return html.Div(  # Graph KPI1
                [
                    html.Div(
                        [
                            html.H3(kpi.title),
                        ],
                        className='pretty_container_title',
                        style={
                            'textAlign': 'center'
                        }
                    ),
                    html.Div(
                        [
                            dcc.Graph(id=kpi.graph_id)
                        ],
                    ),
                ],
                className='pretty_container column',
            )


class Kpi():
    def __init__(self, number):
        self.__dict__.update(config[number])


# Classes and general functions
class Graph():
    def __init__(self, kpi):
        self.groupby = kpi.subfase_column
        self.indices = kpi.indices
        self.width = kpi.width
        self.kleur_kpi = kpi.Kleur_KPI

    def create_bar(self, df, status, color, name):
        bar = df.loc[df[self.kleur_kpi] == status].groupby(self.groupby)[self.kleur_kpi].count()
        bar = bar.reindex(self.indices).fillna(0).copy()

        return go.Bar(
                    x=bar.values,
                    y=bar.index,
                    name=name,
                    orientation='h',
                    marker_color=color,
                    opacity=0.8,
                    width=self.width
        )

    def create_bar_chart_colors(self, df):

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
        rode_balk = self.create_bar(df, "Rood", 'red', 'Overdue')
        gele_balk = self.create_bar(df, "Geel", 'orange', 'Take a look')
        groene_balk = self.create_bar(df, "Groen", 'green', 'In time')

        return go.Figure(
            data=[
                groene_balk,
                gele_balk,
                rode_balk
            ],
            layout=layout,
        )


class Filters():
    def __init__(self, filter_businessline, filter_regiovwt, checklist_filter):

        self.filter_businessline = filter_businessline
        self.filter_regiovwt = filter_regiovwt
        self.checklist_filter = checklist_filter

    def apply_filters(self, df):
        df = df[df['BL'].isin(self.filter_businessline)]
        df = df[df['RegioVWT'].isin(self.filter_regiovwt)]
        if 'maandorders' in self.checklist_filter:
            df = df[df['MaandOrder'] != 'Ja']
        if 'intrekkingen' in self.checklist_filter:
            df = df[~df['Projectkenmerk'].isin(['INTR', 'Change', 'Create INTR', 'Change INTR'])]
        if 'on_hold' in self.checklist_filter:
            df = df[df['WF_Status'] != 'F_Intern_On_Hold']
        if 'archief' in self.checklist_filter:
            df = df[df['WF_Status'] != 'G_Archief']
        return df


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


# helper function filter dropdown
def get_df():
    df = pd.DataFrame(api.get('/Projects?project=FttB'))
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


def get_title(subfase, color):
    label = html.Label(
        '{} {} is geselecteerd'.format(subfase, color),
        style={'fontSize': 20, 'textAlign': 'center'}
    )
    return label


def filter_click(df, kpi_number, color, subfase):
    kpi = Kpi(kpi_number)
    df = df[df[kpi.Kleur_KPI] == color]
    df = df[df[kpi.subfase_column] == subfase]
    df = df[df['Hoofdstatus'] != 'Gereed']

    # get relevant columns
    columns = kpi.columns
    df = df[columns.keys()]
    df.rename(columns=columns, inplace=True)

    # sort values
    # Make generic
    df.sort_values(kpi.sort_column, inplace=True, ascending=False)

    return df


def prepare_data(filters, rename_wvb=True):

    # read all available data
    df = get_df()

    # Apply checkbox and dropdown filters
    df = filters.apply_filters(df)

    # rename Werkvoorbereiding naar WvB, lelijke fix voor KPI2
    if rename_wvb:
        mask = df['Hoofdstatus'] == 'Werkvoorbereiding'
        df.at[mask, 'Hoofdstatus'] = 'WvB'
    return df


# callback Graph overzicht
@app.callback(
    Output('graph_overzicht', 'figure'),
    [
        Input('filter_businessline', 'value'),
        Input('filter_regiovwt', 'value'),
        Input('checklist_filter', 'value'),
    ]
)
def return_graph_overzicht(*filter_list):

    filters = Filters(*filter_list)
    df = prepare_data(filters, rename_wvb=False)

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


def create_download_link(filters, kpi, color, subfase):
    businesslines = ','.join(filters.filter_businessline)
    regiovwt = ','.join(filters.filter_regiovwt)
    checklist = ','.join(filters.checklist_filter)
    return "/download_excel_{}?" \
           "businesslines={}&" \
           "regiovwt={}&" \
           "checklist={}&" \
           "color={}&subfase={}".format(kpi, businesslines, regiovwt, checklist, color, subfase)


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


def get_filename(color, subfase):
    date = dt.datetime.now().strftime('%y%m%d')
    filename = "Download_{}_{}_{}.xlsx".format(color, subfase, date)
    return filename


# Functions and callbacks for Excel download

def convert_to_excel(df):
    # Convert df to excel
    strIO = io.BytesIO()
    excel_writer = pd.ExcelWriter(strIO, engine="xlsxwriter")
    df.to_excel(excel_writer, sheet_name="sheet1", index=False)
    excel_writer.save()
    strIO.getvalue()
    strIO.seek(0)
    return strIO


def download_excel(kpi_number, args):

    filters = Filters(
                        args.get('businesslines').split(','),
                        args.get('regiovwt').split(','),
                        args.get('checklist').split(',')
                    )
    color = args.get('color')
    subfase = args.get('subfase')

    df = prepare_data(filters)
    df = filter_click(df, kpi_number, color, subfase)

    strIO = convert_to_excel(df)
    filename = get_filename(color, subfase)

    return send_file(strIO,
                     attachment_filename=filename,
                     as_attachment=True)


@app.server.route('/download_excel_kpi1')
def download_excel_table1():
    return download_excel('kpi1', flask.request.args)


@app.server.route('/download_excel_kpi2')
def download_excel_table2():
    return download_excel('kpi2', flask.request.args)


@app.server.route('/download_excel_kpi3')
def download_excel_table3():
    return download_excel('kpi3', flask.request.args)


# Functions and callbacks for graphs

def make_graph(kpi_number, filter_list):
    kpi = Kpi(kpi_number)
    filters = Filters(*filter_list)
    graph = Graph(kpi)
    df = prepare_data(filters)

    barchart = graph.create_bar_chart_colors(df)
    return barchart


# callback Graph KPI1
@app.callback(
    Output('graph_kpi1', 'figure'),
    [
        Input('filter_businessline', 'value'),
        Input('filter_regiovwt', 'value'),
        Input('checklist_filter', 'value'),
    ]
)
def return_graph_kpi1(*filter_list):
    barchart = make_graph('kpi1', filter_list)
    return barchart


# callback Graph KPI2
@app.callback(
    Output('graph_kpi2', 'figure'),
    [
        Input('filter_businessline', 'value'),
        Input('filter_regiovwt', 'value'),
        Input('checklist_filter', 'value'),
    ]
)
def return_graph_kpi2(*filter_list):
    barchart = make_graph('kpi2', filter_list)
    return barchart


# callback Graph KPI3
@app.callback(
    Output('graph_kpi3', 'figure'),
    [
        Input('filter_businessline', 'value'),
        Input('filter_regiovwt', 'value'),
        Input('checklist_filter', 'value'),
    ]
)
def return_graph_kpi3(*filter_list):
    barchart = make_graph('kpi3', filter_list)
    return barchart


# Functions and callbacks for tables
@app.callback(
    [
        Output('table_kpi', 'children'),
        Output('graph_clickdata', 'data'),
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
def make_table_on_click(clickdata_graph1, clickdata_graph2, clickdata_graph3,
                        filter_businessline, filter_regiovwt, checklist_filter, state):
    filters = Filters(filter_businessline, filter_regiovwt, checklist_filter)
    kpi_clickdata = {
                            'kpi1': clickdata_graph1,
                            'kpi2': clickdata_graph2,
                            'kpi3': clickdata_graph3,
                        }
    # Raises preventupdate if nothing has been clicked yet.
    current_clickdata = get_clickdata(kpi_clickdata)
    changed_kpi, clickdata_to_store = find_changed_data(current_clickdata, state)
    color = get_color(kpi_clickdata[changed_kpi])
    subfase = get_subfase(kpi_clickdata[changed_kpi])

    table = return_table_kpi(changed_kpi, filters, color, subfase)
    download_link = create_download_link(filters, changed_kpi, color, subfase)

    return [table, clickdata_to_store, download_link]


def return_table_kpi(kpi, filters, color, subfase):

    df = prepare_data(filters)
    df = filter_click(df, kpi, color, subfase)

    table = generate_table(df)
    title = get_title(subfase, color)
    return [title, table]
