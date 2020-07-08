# Import required libraries
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from app import app
import main_page


# navigation bar
def get_navbar(url_page):

    children = [
        dbc.NavItem(dbc.NavLink('Totaal overzicht', href='#')),
    ]

    return dbc.NavbarSimple(
        children=children,
        brand='VWT Infratechniek FTTB',
        sticky='top',
        dark=True,
        color='grey',
        style={
            'top': 0,
            'left': 0,
            'position': 'fixed',
            'width': '100%',
            'font-size': '120%'
        }
    )


app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    html.Div(id='page-content')
])


# CALBACKS
@app.callback(
    Output('page-content', 'children'),
    [
        Input('url', 'pathname')
    ]
)
def display_page(pathname):
    # startpagina
    if pathname == '/':
        return [get_navbar('/main_page'), main_page.get_body()]
    if pathname == '/main_page':
        return [get_navbar(pathname), main_page.get_body()]

    return [get_navbar(pathname), html.P('''deze pagina bestaat niet, druk op vorige
                   of een van de paginas in het menu hierboven''')]


if __name__ == "__main__":
    app.run_server(debug=True)
