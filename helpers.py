import pandas as pd
from pyomo.environ import *
import random
from dash import dash_table, html, dcc

# Fonction pour générer les objets disponibles
def generate_items(num_items, max_capacity, max_value):
    items = [(i + 1, random.randint(1, max_capacity), random.randint(1, max_value)) for i in range(num_items)]
    df = pd.DataFrame(items, columns=["Item", "Weight", "Value"])
    return df

# Fonction d'optimisation du problème du sac à dos
def run_knapsack_optimization(items_df, max_capacity):
    num_items = len(items_df)
    model = ConcreteModel()
    model.item_indexes = RangeSet(num_items)
    model.weight = Param(model.item_indexes, initialize={i + 1: items_df.iloc[i]["Weight"] for i in range(num_items)})
    model.value = Param(model.item_indexes, initialize={i + 1: items_df.iloc[i]["Value"] for i in range(num_items)})
    model.capacity = max_capacity
    model.x = Var(model.item_indexes, domain=Binary)
    model.objective = Objective(expr=sum(model.value[i] * model.x[i] for i in model.item_indexes), sense=maximize)

    def capacity_constraint_rule(model):
        return sum(model.weight[i] * model.x[i] for i in model.item_indexes) <= model.capacity

    model.constraint = Constraint(rule=capacity_constraint_rule)
    solver = SolverFactory('glpk', executable='setup/winglpk-4.65/glpk-4.65/w64/glpsol')
    solver.solve(model)

    chosen_items = [i for i in model.item_indexes if model.x[i].value == 1]
    results = [(items_df.iloc[i - 1]["Item"], items_df.iloc[i - 1]["Weight"], items_df.iloc[i - 1]["Value"]) for i in chosen_items]
    df = pd.DataFrame(results, columns=['Item', 'Weight', 'Value'])
    output_path = "outputs/chosen_items.xlsx"
    df.to_excel(output_path, index=False)
    return df, output_path

# Fonction pour afficher les objets disponibles
def display_available_items(n_clicks, num_items, max_capacity, max_value):
    if n_clicks > 0:
        df = generate_items(num_items, max_capacity, max_value)
        table = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': col, 'id': col} for col in df.columns],
            style_table={'overflowX': 'auto'},
            page_size=10,
            editable=True  # Permettre l'édition des données
        )
        return df.to_dict('records'), html.Div([html.H3("Objets disponibles :"), table]), {'display': 'block'}
    return None, None, {'display': 'none'}


# Fonction pour lancer l'optimisation
def run_optimization(n_clicks, available_items_data, max_capacity):
    if n_clicks > 0 and available_items_data:
        df_items = pd.DataFrame(available_items_data)
        results_df, _ = run_knapsack_optimization(df_items, max_capacity)
        results_table = dash_table.DataTable(
            data=results_df.to_dict('records'),
            columns=[{'name': col, 'id': col} for col in results_df.columns],
            style_table={'overflowX': 'auto'},
            page_size=10
        )
        return html.Div([html.H3("Objets sélectionnés :"), results_table]), {'display': 'block'}
    return None, {'display': 'none'}

# Fonction pour télécharger le fichier des résultats
def download_file(n_clicks, available_items_data, max_capacity):
    if n_clicks > 0 and available_items_data:
        df_items = pd.DataFrame(available_items_data)
        _, file_path = run_knapsack_optimization(df_items, max_capacity)
        return dcc.send_file(file_path)
    return None
