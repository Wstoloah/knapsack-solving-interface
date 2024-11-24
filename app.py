import dash
from dash import dcc, html, Input, Output, State
from dash import dash_table
from helpers import *

# Initialisation de l'application Dash
app = dash.Dash(__name__, external_stylesheets=["custom.css"])

# Mise en page de l'application
app.layout = html.Div([
    html.H1("Problème du sac à dos", style={'textAlign': 'center'}),
    html.Hr(style={'marginBottom': '20px', 'border': '1px solid #000000'}),

    # Inputs with padding
    html.Div([
        html.Div([
            html.Label("Nombre d'objets :", style={'marginRight': '10px', 'marginLeft': '20px'}),
            dcc.Input(id='num_items', type='number', value=100, min=1, max=1000, step=1),
            html.Label("Capacité maximale du sac à dos :", style={'marginRight': '10px', 'marginLeft': '10px'}),
            dcc.Input(id='max_capacity', type='number', value=50, min=1, max=500, step=1),
            html.Label("Valeur maximale d'un objet :", style={'marginRight': '10px', 'marginLeft': '10px'}),
            dcc.Input(id='max_value', type='number', value=100, min=1, max=100, step=1)
        ], style={'marginBottom': '20px', 'display': 'flex', 'alignItems': 'center'}),
    ]),

    # Buttons
    html.Button("Lister les objets disponibles", id='generate_button', n_clicks=0, style={'marginLeft': '20px'}),

    dcc.Store(id='available_items_store'),  # Stocker les objets disponibles

    # Containers for tables
    html.Div([
        html.Div(id='available_items_container', style={'width': '47%', 'marginRight': '3%', 'marginLeft': '20px'}),
        html.Div(id='optimization_results_container', style={'width': '47%'}),
    ], style={'display': 'flex', 'marginTop': '20px'}),

    # Buttons and download
    html.Div([
        html.Div(html.Button("Lancer l'optimisation", id='optimize_button', n_clicks=0, style={'display': 'none'}),
                 style={'width': '47%', 'marginRight': '3%', 'marginLeft': '20px'}),
        html.Div(html.Button("Télécharger les résultats", id='download_button', n_clicks=0, style={'display': 'none'}),
                 style={'width': '47%', 'marginRight': '3%', 'marginLeft': '20px'}),
        dcc.Download(id="download_data"),
    ], style={'display': 'flex', 'marginTop': '20px'}),
])

# Callback pour gérer les objets disponibles
@app.callback(
    Output('available_items_store', 'data', allow_duplicate=True),
    Input('generate_button', 'n_clicks'),
    State('num_items', 'value'),
    State('max_capacity', 'value'),
    State('max_value', 'value'),
    prevent_initial_call=True
)
def generate_items_callback(n_clicks, num_items, max_capacity, max_value):
    df = generate_items(num_items, max_capacity, max_value)
    return df.to_dict('records')


@app.callback(
    Output('available_items_store', 'data', allow_duplicate=True),
    Input('available_items_container', 'children'),
    State('available_items_store', 'data'),
    prevent_initial_call=True
)
def update_items_store_callback(children, current_data):
    return current_data


# Callback pour afficher les objets disponibles
@app.callback(
    [Output('available_items_container', 'children'),
     Output('optimize_button', 'style')],
    Input('available_items_store', 'data')
)
def display_available_items_callback(data):
    if data:
        table = dash_table.DataTable(
            id='available_items_table',
            data=data,
            columns=[{'name': col, 'id': col} for col in data[0].keys()],
            editable=True,
            style_table={'overflowX': 'auto'},
            page_size=10
        )
        return html.Div([html.H3("Objets disponibles :"), table]), {'display': 'block'}
    return None, {'display': 'none'}


# Lancer l'optimisation
@app.callback(
    [Output('optimization_results_container', 'children'),
     Output('download_button', 'style')],
    Input('optimize_button', 'n_clicks'),
    State('available_items_store', 'data'),
    State('max_capacity', 'value')
)
def run_optimization_callback(n_clicks, available_items_data, max_capacity):
    return run_optimization(n_clicks, available_items_data, max_capacity)


# Télécharger les résultats
@app.callback(
    Output('download_data', 'data'),
    Input('download_button', 'n_clicks'),
    State('available_items_store', 'data'),
    State('max_capacity', 'value')
)
def download_file_callback(n_clicks, available_items_data, max_capacity):
    return download_file(n_clicks, available_items_data, max_capacity)


if __name__ == '__main__':
    app.run_server(debug=True)
