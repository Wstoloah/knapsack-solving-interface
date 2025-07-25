import dash
from dash import dcc, html, Input, Output, State
from dash import dash_table
import pandas as pd
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate

from helpers import generate_items, run_optimization, prepare_download_data


class KnapsackApp:
    def __init__(self):
        self.app = dash.Dash(__name__, external_stylesheets=["custom.css"])
        self.setup_layout()
        self.setup_callbacks()

    def setup_layout(self):
        self.app.layout = html.Div([
            self.create_header(),
            self.create_configuration_panel(),
            dcc.Store(id='available_items_store'),
            dcc.Store(id='optimization_results_store'),
            self.create_main_content(),
            self.create_action_panel(),
            dcc.Download(id="download_data")
        ], className='app-container')

    def create_header(self):
        return html.Div([
            html.H1("🎒 Optimisation du problème de Sac à Dos", className='main-title'),
            html.P("Résolvez le problème classique du sac à dos en maximisant la valeur sous contrainte de capacité.", className='subtitle'),
            html.Hr(className='header-divider')
        ], className='header-section')

    def create_configuration_panel(self):
        return html.Div([
            html.H3("⚙️ Configuration", className='section-title'),
            html.Div([
                self.create_input_group("Nombre d'objets", 'num_items', 100, 1, 1000, "1-1000 objets"),
                self.create_input_group("Capacité maximale", 'max_capacity', 50, 1, 500, "Poids maximum"),
                self.create_input_group("Valeur maximale", 'max_value', 100, 1, 1000, "Par objet"),
                html.Div([
                    html.Label("Algorithme", className='config-label'),
                    dcc.Dropdown(
                        id='algorithm_select',
                        options=[
                            {'label': '🔍 Programmation Dynamique', 'value': 'dynamic'},
                            {'label': '🧬 Algorithme Génétique', 'value': 'genetic'},
                            {'label': '🎯 Glouton (Heuristique)', 'value': 'greedy'}
                        ],
                        value='dynamic',
                        className='config-dropdown'
                    ),
                ], className='config-group'),
            ], className='config-container'),

            html.Div([
                html.Button("🎲 Générer Objets Aléatoirement", id='generate_button', n_clicks=0, className='primary-button'),
                html.Button("🔄 Nouvelle Configuration", id='reset_button', n_clicks=0, className='secondary-button')
            ], className='button-group')
        ], className='configuration-panel')

    def create_input_group(self, label, input_id, default, min_val, max_val, help_text):
        return html.Div([
            html.Label(label, className='config-label'),
            dcc.Input(id=input_id, type='number', value=default, min=min_val, max=max_val, step=1, className='config-input'),
            html.Small(help_text, className='input-help')
        ], className='config-group')

    def create_main_content(self):
        return html.Div([
        # First row: two columns side by side
        html.Div([
            html.Div(id='available_items_container', className='items-column content-section'),
            html.Div(id='optimization_results_container', className='results-column content-section'),
        ], className='results-row'),

        # Second row: full width chart section
        html.Div(id='optimization_charts_container', className='content-section'),
    ], className='main-content')

    def create_action_panel(self):
        return html.Div([
            html.Button("🚀 Lancer l'Optimisation", id='optimize_button', n_clicks=0, className='success-button', style={'display': 'none'}),
            html.Button("📊 Afficher Statistiques", id='stats_button', n_clicks=0, className='info-button', style={'display': 'none'}),
            html.Button("⬇️ Télécharger Résultats", id='download_button', n_clicks=0, className='download-button', style={'display': 'none'})
        ], className='action-panel')

    def setup_callbacks(self):
        @self.app.callback(
            [Output('available_items_store', 'data'),
             Output('available_items_container', 'children'),
             Output('optimize_button', 'style')],
            Input('generate_button', 'n_clicks'),
            [State('num_items', 'value'),
             State('max_capacity', 'value'),
             State('max_value', 'value')],
            prevent_initial_call=True
        )
        def generate_and_display_items(n_clicks, num_items, max_capacity, max_value):
            if not n_clicks:
                raise PreventUpdate
            df = generate_items(num_items, max_capacity, max_value)
            data = df.to_dict('records')
            table = self.create_items_table(data, "available_items_table", "Objets Disponibles")
            return data, table, {'display': 'block', 'margin': '10px'}

        @self.app.callback(
            [Output('optimization_results_container', 'children'),
             Output('optimization_results_store', 'data'),
             Output('download_button', 'style'),
             Output('stats_button', 'style')],
            Input('optimize_button', 'n_clicks'),
            [State('available_items_store', 'data'),
             State('max_capacity', 'value'),
             State('algorithm_select', 'value')],
            prevent_initial_call=True
        )
        def run_optimization_callback(n_clicks, items_data, max_capacity, algorithm):
            if not n_clicks or not items_data:
                raise PreventUpdate
            results = run_optimization(items_data, max_capacity, algorithm)
            table = self.create_results_table(results)
            charts = self.create_optimization_charts(results, items_data, max_capacity)
            style = {'display': 'block', 'margin': '10px'}
            return table, results, style, style

        @self.app.callback(
            Output('download_data', 'data'),
            Input('download_button', 'n_clicks'),
            [State('available_items_store', 'data'),
             State('optimization_results_store', 'data'),
             State('max_capacity', 'value')],
            prevent_initial_call=True
        )
        def download_results(n_clicks, items, results, capacity):
            if not n_clicks:
                raise PreventUpdate
            return prepare_download_data(items, results, capacity)
        
        @self.app.callback(
            Output('optimization_charts_container', 'children'),
            Input('stats_button', 'n_clicks'),
            [State('optimization_results_store', 'data'),
            State('available_items_store', 'data'),
            State('max_capacity', 'value')],
            prevent_initial_call=True
        )
        def show_stats_callback(n_clicks, results, items_data, max_capacity):
            if n_clicks == 0 or not results:
                raise PreventUpdate
            return self.create_optimization_charts(results, items_data, max_capacity)

        @self.app.callback(
            [Output('available_items_store', 'data', allow_duplicate=True),
             Output('optimization_results_store', 'data', allow_duplicate=True),
             Output('available_items_container', 'children', allow_duplicate=True),
             Output('optimization_results_container', 'children', allow_duplicate=True),
             Output('optimization_charts_container', 'children', allow_duplicate=True)],
            Input('reset_button', 'n_clicks'),
            prevent_initial_call=True
        )
        def reset_app(n_clicks):
            if not n_clicks:
                raise PreventUpdate
            return None, None, "", "", ""

    def create_items_table(self, data, table_id, title):
        if not data:
            return html.Div("Aucun objet généré", className='no-data-message')

        df = pd.DataFrame(data)
        stats = html.Div([
            html.P(f"📊 {len(df)} objets | Poids total: {df['weight'].sum():.1f} | Valeur totale: {df['value'].sum():.1f}"),
            html.P(f"💰 Ratio moyen V/P: {(df['value'] / df['weight']).mean():.2f}")
        ], className='table-stats')

        table = dash_table.DataTable(
            id=table_id,
            data=data,
            columns=[
                {'name': 'ID', 'id': 'id'},
                {'name': 'Nom', 'id': 'name'},
                {'name': 'Poids', 'id': 'weight', 'type': 'numeric', 'format': {'specifier': '.1f'}},
                {'name': 'Valeur', 'id': 'value', 'type': 'numeric', 'format': {'specifier': '.1f'}},
                {'name': 'Ratio V/P', 'id': 'ratio', 'type': 'numeric', 'format': {'specifier': '.2f'}}
            ],
            editable=True,
            sort_action="native",
            filter_action="native",
            page_size=15,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'padding': '10px'},
            style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'},
            style_data_conditional=[
                {'if': {'column_id': 'ratio', 'filter_query': '{ratio} > 2'},
                 'backgroundColor': '#d4edda', 'color': 'black'}
            ]
        )

        optimization_button = None
        if table_id == "available_items_table":
            optimization_button = html.Div([
                html.Button(
                    "🚀 Lancer l'Optimisation",
                    id='optimize_button',
                    n_clicks=0,
                    className='success-button',
                    style={'display': 'none'}
                )
            ], className='action-panel')

        return html.Div([
            html.H3(f"📦 {title}", className='table-title'),
            stats,
            table,
            optimization_button if optimization_button else None,
        ], className='table-container')

    def create_results_table(self, results):
        """Crée le tableau des résultats d'optimisation"""
        if not results or 'selected_items' not in results:
            return html.Div("Aucun résultat disponible", className='no-data-message')

        selected_items = results['selected_items']
        summary = results.get('summary', {})

        # Résumé des résultats
        summary_component = html.Div([
            html.H3("🎯 Résultats de l'Optimisation", className='results-title'),
            html.Div([
                html.Div([
                    html.H4(f"{summary.get('total_value', 0):.1f}", className='metric-value'),
                    html.P("Valeur Totale", className='metric-label')
                ], className='metric-card'),
                html.Div([
                    html.H4(f"{summary.get('total_weight', 0):.1f}", className='metric-value'),
                    html.P("Poids Total", className='metric-label')
                ], className='metric-card'),
                html.Div([
                    html.H4(f"{len(selected_items)}", className='metric-value'),
                    html.P("Objets Sélectionnés", className='metric-label')
                ], className='metric-card'),
                html.Div([
                    html.H4(f"{summary.get('efficiency', 0):.1f}%", className='metric-value'),
                    html.P("Efficacité", className='metric-label')
                ], className='metric-card'),
            ], className='metrics-container'),
            html.Div([
                html.Button(
                    "⬇️ Télécharger Résultats",
                    id='download_button',
                    n_clicks=0,
                    className='download-button',
                    style={'display': 'none'}
                ),
                html.Button(
                    "📊 Afficher Statistiques",
                    id='stats_button',
                    n_clicks=0,
                    className='info-button',
                    style={'display': 'none', 'marginLeft': '10px'}
                )
            ], className='action-panel', style={'display': 'flex', 'gap': '10px'})
        ])

        # Tableau des objets sélectionnés
        selected_table = self.create_items_table(selected_items, "selected_items_table", "Objets Sélectionnés")

        return html.Div([selected_table, summary_component])

    def metric_card(self, label, value):
        return html.Div([
            html.H4(value, className='metric-value'),
            html.P(label, className='metric-label')
        ], className='metric-card')

    def create_optimization_charts(self, results, all_items, max_capacity):
        if not results:
            return html.Div()

        charts = []

        df_all = pd.DataFrame(all_items)
        df_selected = pd.DataFrame(results['selected_items'])

        fig_scatter = go.Figure()
        fig_scatter.add_trace(go.Scatter(
            x=df_all['weight'], y=df_all['value'],
            mode='markers', name='Non sélectionnés',
            marker=dict(color='lightgray', size=8),
            text=df_all['name'],
            hovertemplate='<b>%{text}</b><br>Poids: %{x}<br>Valeur: %{y}<extra></extra>'
        ))
        fig_scatter.add_trace(go.Scatter(
            x=df_selected['weight'], y=df_selected['value'],
            mode='markers', name='Sélectionnés',
            marker=dict(color="#28a745", size=12),
            text=df_selected['name'],
            hovertemplate='<b>%{text}</b><br>Poids: %{x}<br>Valeur: %{y}<extra></extra>'
        ))
        fig_scatter.update_layout(title="Distribution Valeur vs Poids", xaxis_title="Poids", yaxis_title="Valeur")

        charts.append(dcc.Graph(figure=fig_scatter))

        used_capacity = results.get('summary', {}).get('total_weight', 0)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=used_capacity,
            delta={'reference': max_capacity},
            gauge={
                'axis': {'range': [0, max_capacity]},
                'bar': {'color': "#28a745"},
                'steps': [
                    {'range': [0, max_capacity * 0.7], 'color': "lightgray"},
                    {'range': [max_capacity * 0.7, max_capacity], 'color': "orange"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'value': max_capacity
                }
            },
            title={'text': "Utilisation de la Capacité"}
        ))
        charts.append(dcc.Graph(figure=fig_gauge))

        return html.Div(charts, className='charts-container')

    def run_server(self, debug=True, port=8050):
        self.app.run_server(debug=debug, port=port)


if __name__ == '__main__':
    KnapsackApp().run_server(debug=True)
