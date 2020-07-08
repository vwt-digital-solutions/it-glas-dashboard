import os
import dash
import flask
import config
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from authentication.azure_auth import AzureOAuth
from google.cloud import secretmanager
from flask_sslify import SSLify
from flask_cors import CORS

server = flask.Flask(__name__)

if 'GAE_INSTANCE' in os.environ:
    SSLify(server, permanent=True)
    CORS(server, origins=config.ORIGINS)
else:
    CORS(server)

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    assets_folder='assets/',
    server=server
)

app.config.suppress_callback_exceptions = True
app.scripts.config.serve_locally = True
app.css.config.serve_locally = False


# get secret from secretmanager gcp
def get_secret(project_id, secret_id, version_id):

    client = secretmanager.SecretManagerServiceClient()

    name = client.secret_version_path(project_id, secret_id, version_id)
    response = client.access_secret_version(name)
    payload = response.payload.data.decode('UTF-8')

    return payload


# Azure AD authentication
if config.authentication:

    config.authentication['session_secret'] = get_secret(
        config.authentication['project_id'],
        config.authentication['secret_id'],
        config.authentication['version_id']
    )

    auth = AzureOAuth(
        app,
        config.authentication['client_id'],
        config.authentication['client_secret'],
        config.authentication['expected_issuer'],
        config.authentication['expected_audience'],
        config.authentication['jwks_url'],
        config.authentication['tenant'],
        config.authentication['session_secret'],
        config.authentication['role'],
        config.authentication['required_scopes']
    )


app.css.append_css(
    {"external_url": "https://codepen.io/chriddyp/pen/brPBPO.css"}
)

dcc._js_dist[0]['external_url'] = 'https://cdn.plot.ly/plotly-basic-latest.min.js'


random_string = 'k%EVceQ7sMsu*vK5rk*#DduT61#@PtnyPq0HYjQ0%G4GzHWyg70BGwgsT@CSH^6M'
