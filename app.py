# -*- coding: utf-8 -*-
# Import required libraries
import pandas as pd
import numpy as np
import requests
import json
import dash
from dash.dependencies import Input, Output, State
from dash import callback_context, no_update
from dash.exceptions import PreventUpdate
from dash import dcc
from dash import html
from dash import dash_table as dt
import dash_bootstrap_components as dbc
import visdcc
import logging
import math
import functions as fn
import config

# config variables
port = config.PORT
host = config.HOST
#url_subpath = config.URL_SUBPATH

# logs section
class DashLoggerHandler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)
        self.queue = []

    def emit(self, record):
        msg = self.format(record)
        self.queue.append(msg)


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
dashLoggerHandler = DashLoggerHandler()
logger.addHandler(dashLoggerHandler)

# Setup the app
external_stylesheets=[dbc.themes.ZEPHYR]
app = dash.Dash(
    __name__, meta_tags=[
        {"name": "viewport", "content": "width=device-width"}],
    external_stylesheets=external_stylesheets,
    #url_base_pathname=url_subpath
)

app.title = "AurehalNetwork"
server = app.server

# PARAMS
COLORS = {'VALID': "#FFB300",  # Vivid Yellow
          'OLD':  "#817066",  # Medium Gray
          'INCOMING': "#A6BDD7",  # Very Light Blue
          'institution': "#007D34",  # Vivid Green
          'regroupinstitution': "#00538A",  # Strong Blue
          'regrouplaboratory': "#FF7A5C",  # Strong Yellowish Pink
          'laboratory': "#F6768E",  # Strong Purplish Pink
          'department': "#F13A13",  # Vivid Reddish Orange
          'researchteam': "#7F180D", }  # Strong Reddish Brown

# LAYOUT COMPONENTS
# navbar github right button
button_github = dbc.Button(
    "View Code on github",
    outline=True,
    color="primary",
    href="https://github.com/azur-scd/AurehalNetwork",
    target="_blanck",
    id="gh-link",
    style={"text-transform": "none"},
)
# Navbar
header = dbc.Row(
    [
        dbc.Col(
            [
                html.Div(html.Img(src=app.get_asset_url('logo_UCA_bibliotheque_ligne_couleurs.png'), style={
                    'height': '60px', 'width': '350px'})),
            ],
            md=3,
        ),
        dbc.Col(html.H3("Aurehal Network"), md=7),
        dbc.Col(button_github, md=2),
    ],
    align="center",
)
# component input aurehal id
input_struct_id = html.Div(
    [
        html.H5(dbc.Label("Entrer un identifiant Aurehal de structure")),
        dbc.Input(id="docid", type="text"),
        dbc.FormText("exemple : 302940"),
    ]
)
# component harvest direction : parent or child strcutures
select_harvest_direction = html.Div(
    [
        html.H5(dbc.Label("Direction")),
        dbc.Select(
            options=[
                {"label": "descendante (structures filles)", "value": "desc"},
                {"label": "ascendante (structures parentes)", "value": "asc"},
            ],
            value="desc",
            id="select-harvest-direction",
        ),
    ]
)
# component display in hierarchical way
radio_hierarchical_enabled = html.Div(
    [
        html.H5(dbc.Label("Graphique hiérarchique")),
        dbc.RadioItems(
            options=[
                {"label": "Non", "value": False},
                {"label": "Oui", "value": True},
            ],
            value=False,
            id="radio-hierarchical-enabled",
        ),
    ]
)
# component display direction of the hierarchy
select_hierarchical_direction = html.Div(
    [
        html.H5(dbc.Label("Direction du graphe")),
        dbc.Select(
            options=[
                {"label": "Du haut vers le bas", "value": "UD"},
                {"label": "Du bas vers le haut", "value": "DU"},
                {"label": "De la gauche vers la droite", "value": "LR"},
                {"label": "De la droite vers la gauche", "value": "RL"},
            ],
            value="UD",
            id="select-hierarchical-direction",
        ),
    ],
    style={"width": "50%"}
)
# component display nodes color
radio_nodes_color = html.Div(
    [
        html.H5(dbc.Label("Déterminer la couleur des noeuds en fonction")),
        dbc.RadioItems(
            options=[
                {"label": "du statut (VALID|OLD|INCOMING)",
                 "value": "valid_s"},
                {"label": "du type de structure", "value": "type_s"},
            ],
            value="valid_s",
            id="radio-nodes-color",
        ),
    ]
)
# component display nodes size
radio_nodes_size = html.Div(
    [
        html.H5(dbc.Label("Déterminer la taille des noeuds en fonction du nombre de publications liées aux structures")),
        dbc.RadioItems(
            options=[
                {"label": "non","value": "non"},
                {"label": "oui", "value": "oui"},
            ],
            value="non",
            id="radio-nodes-size",
        ),
    ]
)
# FILTERS COMPONENTS
# component filter node title (label_s param)
input_filter_node_title = html.Div(
    [
        html.H5(dbc.Label("Chercher une structure (libellé ou identifiant)")),
        dbc.Input(id="input-filter-node-title", type="text"),
    ]
)
# component filter valid_s param
checklist_valid_s_colors = html.Div(
    [
        html.H5(dbc.Label("Filter par le statut des structures")),
        dbc.Checklist(
            options=[
                {"label": "VALID", "value": "VALID"},
                {"label": "OLD", "value": "OLD"},
                {"label": "INCOMING", "value": "INCOMING"},
            ],
            value=["VALID", "OLD", "INCOMING"],
            id="checklist-valid-s-colors",
        ),
    ]
)
# component filter type_s param
checklist_type_s_colors = html.Div(
    [
        html.H5(dbc.Label("Filter par type de structure")),
        dbc.Checklist(
            options=[
                {"label": "regroupinstitution", "value": "regroupinstitution"},
                {"label": "institution", "value": "institution"},
                {"label": "regrouplaboratory", "value": "regrouplaboratory"},
                {"label": "laboratory", "value": "laboratory"},
                {"label": "department", "value": "department"},
                {"label": "researchteam", "value": "researchteam"},
            ],
            value=["regroupinstitution", "institution", "regrouplaboratory",
                   "laboratory", "department", "researchteam"],
            id="checklist-type-s-colors",
        ),
    ]
)

controls_layout = html.Div(
    [
        radio_hierarchical_enabled,
        select_hierarchical_direction,
        html.Hr(),
        radio_nodes_color,
        html.Hr(),
        radio_nodes_size,
    ]
)
controls_filtres = html.Div(
    [
        input_filter_node_title,
        html.Hr(),
        checklist_valid_s_colors,
        html.Hr(),
        checklist_type_s_colors
    ]
)
# componnet natwork legend
network_legend_valid_s = html.Span(
    [
        dbc.Badge("VALID", color="#FFB300", className="me-1"),
        dbc.Badge("OLD", color="#817066", className="me-1"),
        dbc.Badge("INCOMING", color="#A6BDD7", className="me-1"),
    ]
)
network_legend_type_s = html.Span(
    [
        dbc.Badge("institution", color="#007D34", className="me-1"),
        dbc.Badge("regroupinstitution", color="#00538A", className="me-1"),
        dbc.Badge("regrouplaboratory", color="#FF7A5C", className="me-1"),
        dbc.Badge("laboratory", color="#F6768E", className="me-1"),
        dbc.Badge("department", color="#F13A13", className="me-1"),
        dbc.Badge("researchteam", color="#7F180D", className="me-1"),
    ]
)
# CONSOLE COMPONENT
console = html.Div([
    #dcc.Interval(id='intervals', interval=1000, n_intervals=0),
    html.H1(id='div-out'),
    html.Iframe(id='console-out', srcDoc='',
                style={'width': '100%', 'height': 400})
])
# ALERT BAR (IF NO DATA) COMPONENT
alert_bar = html.Div([html.P(),dbc.Alert("Pas de données trouvées !", color="danger"),],id="alert-bar",style={'display': 'none'})
# LAYOUTS
app.layout = dbc.Container(
    fluid=True,
    children=[
        header,
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    width=3,
                    children=[
                        dbc.Card(
                            [dbc.CardHeader(html.H4("Contrôles")), dbc.CardBody(
                                controls_layout), ],
                            color="primary", outline=True
                        ),
                        html.P(""),
                        dbc.Card(
                            [dbc.CardHeader(html.H4("Filtres")),
                             dbc.CardBody(controls_filtres), ],
                            color="warning", outline=True
                        ),
                        html.P(""),
                        dbc.Card(
                            [dbc.CardHeader(children=[
                                dbc.Row(
                                            [
                                                dbc.Col(
                                                    [html.H4("Console")], md=4),
                                                dbc.Col([dbc.Button(
                                                    "Voir les logs des appels à l'API HAL", id="console-button", size="sm", n_clicks=0)], md=8)
                                            ],
                                            ),
                            ]
                            ),
                                dbc.CardBody(console), ],
                            color="dark", inverse=True
                        ),
                    ],
                ),
                dbc.Col(
                    width=9,
                    children=[
                        dbc.Card(
                            [
                                dbc.CardHeader(children=[
                                    dbc.Row([
                                        dbc.Col(
                                            [input_struct_id], md=4),
                                        dbc.Col(
                                            [select_harvest_direction], md=4),
                                        dbc.Col(
                                            [
                                                dbc.Button(
                                                    "Valider", id="submit-button", color="primary", className="me-1", n_clicks_timestamp='0')
                                            ],
                                            align="center",
                                            md=2),
                                    ],
                                        className="g-3"),
                                    dbc.Row([html.P("Attention patience : selon la requête le temps de moissonnage des réponses de l'API peut être plus ou moins long")]),
                                ],
                                    style={"backgroundColor": "#4d96ad"}),
                                dbc.CardBody(
                                    children=[
                                        dbc.Spinner(html.Div(id="loading",
                                                             children=[dcc.Store(id="edge-dict"),
                                                                       dcc.Store(id="node-dict")]
                                                             )
                                                    ),
                                        network_legend_valid_s,
                                        network_legend_type_s,
                                        alert_bar,
                                        html.Div(id="network")],
                                    style={"height": "80vh"},
                                )
                            ],
                            color="light", outline=True
                        ),
                        html.P(""),
                        dbc.Card(
                            [
                                dbc.CardHeader("Tableau des structures"),
                                dbc.CardBody(children=[html.Div(id="node-table")],
                                             style={"height": "100%"}),
                            ],
                            color="success", outline=True,
                        ),
                    ]
                ),
            ],
        ),
        html.Hr(),
         dbc.Row(
            [
                dbc.Col([html.Div(['Made with ', html.Img(
                    src="https://images.plot.ly/logo/new-branding/plotly-logomark.png", height="20px")])], width=4),
            ],
            justify="center",
        ),
        dbc.Row(
            [
                dbc.Col(
                       html.Div([
                           html.Div('Contact : '),
                           html.A('Géraldine Geoffroy', href='mailto:geraldine.geoffroy@univ-cotedazur.fr')
                       ])
                     , width=4),               
            ],
            justify="center",
        ),      
    ],
)

# SOME HELPERS FUNCTION
def update_node_size(radio_nodes_size,node):
    if radio_nodes_size == "non":
         size = 7
    else:
        if node['nb_publis'] != 0:
            size = round(math.log(int(node['nb_publis'])*5))
        else:
            size = 5
    return size

def filter_condition(input_filter_node_title,checklist_valid_s_colors, checklist_type_s_colors,node,title):
    condition = (node["valid_s"] in checklist_valid_s_colors) & (
                    node["type_s"] in checklist_type_s_colors)
    if input_filter_node_title is not None:
        condition = (node["valid_s"] in checklist_valid_s_colors) & (
                    node["type_s"] in checklist_type_s_colors) & (str(input_filter_node_title) in title)
    return condition


# CALLBACKS
@app.callback(Output('edge-dict', 'data'),
              Output('node-dict', 'data'),
              Output('node-table', 'children'),
              [Input('docid', 'value'),
              Input('select-harvest-direction', 'value'),
              Input("submit-button", "n_clicks")],
              prevent_initial_call=True)
def update_states(docid, select_harvest_direction, n_clicks):
    trig_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    if (trig_id == "docid") | (trig_id == "select-harvest-direction"):
        return dash.no_update
    elif trig_id == "submit-button":
        if select_harvest_direction == "desc":
            edge_df = pd.DataFrame(fn.get_child_struct(docid, None))
        elif select_harvest_direction == "asc":
            edge_df = pd.DataFrame(fn.get_parent_struct(docid, None))
        if not edge_df.empty:
            list_unique_docid = set(edge_df["from"].unique().tolist()+edge_df["to"].unique().tolist())
            node_df = fn.get_list_struct_infos(list_unique_docid)
            columns = [{"name": str(i), "id": str(i)} for i in node_df.columns]
            return edge_df.to_dict(orient='records'), node_df.to_dict(orient='records'), fn.render_datatable(columns, node_df.to_dict(orient='records'))
        else:
            return None, None, None
    else:
        return None, None, None

@app.callback(Output('network', 'children'),
              [Input("radio-nodes-color", "value"),
              Input("radio-nodes-size", "value"),
              Input("checklist-valid-s-colors", "value"),
              Input("checklist-type-s-colors", "value"),
              Input("radio-hierarchical-enabled", "value"),
              Input("select-hierarchical-direction", "value"),
              Input("input-filter-node-title", "value"),
              Input("edge-dict", "data"),
              Input("node-dict", "data")],
              prevent_initial_call=True
              )
def render_network(radio_nodes_color, radio_nodes_size, checklist_valid_s_colors, checklist_type_s_colors, radio_hierarchical_enabled, select_hierarchical_direction, input_filter_node_title, edge_dict, node_dict):
    edges = []
    nodes = []
    if (node_dict is not None) & (edge_dict is not None):
        OPTIONS = fn.render_network_options(
            hierarchical_enabled=radio_hierarchical_enabled, direction=select_hierarchical_direction)
        for row in edge_dict:
            edges.append({**row, **{'id': str(row['from']) + "__" + str(row['to']),  'color': {'color': '#97C2FC'}}})
        for node in node_dict:
            #node title for tooltip
            title = '{} (id:{}) ({} publis) ({})'.format(node['label_s'], node['id'],node['nb_publis'],node['valid_s'])
            if filter_condition(input_filter_node_title,checklist_valid_s_colors, checklist_type_s_colors,node,title):
                nodes.append({**node, **{'label': node['acronym_s'], 'shape': 'dot',
                             'size': update_node_size(radio_nodes_size,node), 'title': title, 'color': COLORS[node[radio_nodes_color]]}})
        graphdata = {'nodes': nodes, 'edges': edges}
        return visdcc.Network(id='graph', data=graphdata, options=OPTIONS)
    else:
        return None

@app.callback(
    Output('console-out', 'srcDoc'),
    [Input('console-button', 'n_clicks')])
def update_output(n_clicks):
    if n_clicks != 0:
        return ('\n'.join(dashLoggerHandler.queue)).replace('\n', '<BR>')

@app.callback(
    Output('alert-bar', 'style'),
    [Input('network', 'children')],
    prevent_initial_call=True)
def info_nodata(network):
    if network is None:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


if __name__ == "__main__":
    app.run_server(port=port, host=host)
