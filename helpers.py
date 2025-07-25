from datetime import datetime
import json
import os
import pandas as pd
from pyomo.environ import *
import random
from dash import dash_table, html, dcc

PATH = 'setup/winglpk-4.65/glpk-4.65/w64/glpsol.exe'
OUTPUT_PATH = 'outputs/'


def generate_items(num_items, max_capacity, max_value):
    """Génère des objets aléatoires pour le sac à dos"""
    items = []
    for i in range(num_items):
        weight = random.randint(1, max_capacity)
        value = random.randint(1, max_value)
        ratio = value / weight
        
        items.append({
            'id': i + 1,
            'name': f'Objet_{i+1}',
            'weight': round(weight, 1),
            'value': round(value, 1),
            'ratio': round(ratio, 2)
        })
    
    return pd.DataFrame(items)

def run_knapsack_optimization(items_df, max_capacity):
    """Optimisation exacte du sac à dos avec Pyomo et GLPK"""
    try:
        import os
        
        num_items = len(items_df)
        model = ConcreteModel()
        model.item_indexes = RangeSet(num_items)
        
        # Paramètres du modèle
        model.weight = Param(model.item_indexes, initialize={
            i + 1: items_df.iloc[i]["Weight"] for i in range(num_items)
        })
        model.value = Param(model.item_indexes, initialize={
            i + 1: items_df.iloc[i]["Value"] for i in range(num_items)
        })
        model.capacity = max_capacity
        
        # Variables de décision (binaires)
        model.x = Var(model.item_indexes, domain=Binary)
        
        # Fonction objectif (maximiser la valeur)
        model.objective = Objective(
            expr=sum(model.value[i] * model.x[i] for i in model.item_indexes), 
            sense=maximize
        )
        
        # Contrainte de capacité
        def capacity_constraint_rule(model):
            return sum(model.weight[i] * model.x[i] for i in model.item_indexes) <= model.capacity
        
        model.constraint = Constraint(rule=capacity_constraint_rule)
        
        # Résolution avec GLPK
        solver_path = PATH
        if os.path.exists(solver_path):
            solver = SolverFactory('glpk', executable=solver_path)
        else:
            # Essayer avec GLPK installé globalement
            solver = SolverFactory('glpk')
        
        results = solver.solve(model, tee=False)
        
        # Vérifier si la solution est optimale
        if results.solver.termination_condition.name != 'optimal':
            raise Exception(f"Pas de solution optimale trouvée: {results.solver.termination_condition}")
        
        # Extraire les objets choisis
        chosen_items = [i for i in model.item_indexes if model.x[i].value == 1]
        results_list = [
            (items_df.iloc[i - 1]["Item"], 
                items_df.iloc[i - 1]["Weight"], 
                items_df.iloc[i - 1]["Value"]) 
            for i in chosen_items
        ]
        
        results_df = pd.DataFrame(results_list, columns=['Item', 'Weight', 'Value'])
        
        # Optionnel: sauvegarder les résultats
        output_path = OUTPUT_PATH
        try:
            os.makedirs("outputs", exist_ok=True)
            results_df.to_excel(output_path, index=False)
        except:
            output_path = None  # Si impossible d'écrire le fichier
            
        return results_df, output_path
        
    except ImportError:
        raise Exception("Pyomo n'est pas installé. Utilisez: pip install pyomo")
    except Exception as e:
        raise Exception(f"Erreur dans l'optimisation exacte: {str(e)}")

def greedy_knapsack(df, max_capacity):
    """Algorithme glouton basé sur le ratio valeur/poids"""
    df_sorted = df.sort_values('ratio', ascending=False)
    
    selected_items = []
    total_weight = 0
    total_value = 0
    
    for _, item in df_sorted.iterrows():
        if total_weight + item['weight'] <= max_capacity:
            selected_items.append(item.to_dict())
            total_weight += item['weight']
            total_value += item['value']
    
    return selected_items, total_weight, total_value

def genetic_knapsack(df, max_capacity, population_size=50, generations=100):
    """Algorithme génétique pour le sac à dos"""
    import random
    import numpy as np
    
    items = df.to_dict('records')
    n_items = len(items)
    
    def create_individual():
        """Crée un individu aléatoire"""
        return [random.randint(0, 1) for _ in range(n_items)]
    
    def fitness(individual):
        """Calcule la fitness d'un individu"""
        total_weight = sum(items[i]['weight'] * individual[i] for i in range(n_items))
        total_value = sum(items[i]['value'] * individual[i] for i in range(n_items))
        
        # Pénalité si dépasse la capacité
        if total_weight > max_capacity:
            return 0
        return total_value
    
    def crossover(parent1, parent2):
        """Croisement en un point"""
        point = random.randint(1, n_items - 1)
        child1 = parent1[:point] + parent2[point:]
        child2 = parent2[:point] + parent1[point:]
        return child1, child2
    
    def mutate(individual, mutation_rate=0.1):
        """Mutation binaire"""
        for i in range(len(individual)):
            if random.random() < mutation_rate:
                individual[i] = 1 - individual[i]
        return individual
    
    # Initialisation de la population
    population = [create_individual() for _ in range(population_size)]
    
    # Évolution
    for generation in range(generations):
        # Évaluation
        fitness_scores = [(fitness(ind), ind) for ind in population]
        fitness_scores.sort(reverse=True)
        
        # Sélection des meilleurs
        elite_size = population_size // 4
        new_population = [ind for _, ind in fitness_scores[:elite_size]]
        
        # Reproduction
        while len(new_population) < population_size:
            # Sélection par tournoi
            tournament_size = 3
            parent1 = max(random.sample(fitness_scores[:population_size//2], tournament_size))[1]
            parent2 = max(random.sample(fitness_scores[:population_size//2], tournament_size))[1]
            
            child1, child2 = crossover(parent1, parent2)
            new_population.extend([mutate(child1), mutate(child2)])
        
        population = new_population[:population_size]
    
    # Meilleure solution
    best_fitness = max(fitness(ind) for ind in population)
    best_individual = max(population, key=fitness)
    
    # Convertir en format de sortie
    selected_items = []
    total_weight = 0
    total_value = 0
    
    for i, selected in enumerate(best_individual):
        if selected:
            selected_items.append(items[i])
            total_weight += items[i]['weight']
            total_value += items[i]['value']
    
    return selected_items, total_weight, total_value

def run_optimization(items_data, max_capacity, algorithm):
    """Exécute l'algorithme d'optimisation choisi"""
    df = pd.DataFrame(items_data)
    
    df_adapted = df.rename(columns={
        'name': 'Item',
        'weight': 'Weight', 
        'value': 'Value'
    })
    
    if algorithm == 'dynamic':
        # Utilisation de l'optimisation avec pyomo/glpk
        try:
            results_df, _ = run_knapsack_optimization(df_adapted, max_capacity)
            selected_items = []
            
            # Convertir les résultats en format attendu
            for _, row in results_df.iterrows():
                # Retrouver l'item original avec ses données complètes
                original_item = df[df['name'] == row['Item']].iloc[0]
                selected_items.append({
                    'id': original_item['id'],
                    'name': original_item['name'],
                    'weight': original_item['weight'],
                    'value': original_item['value'],
                    'ratio': original_item['ratio']
                })
            
            total_weight = results_df['Weight'].sum()
            total_value = results_df['Value'].sum()
            
        except Exception as e:
            print(f"Erreur avec l'optimisation exacte: {e}")
            # Fallback vers algorithme glouton
            algorithm = 'greedy'
            selected_items, total_weight, total_value = greedy_knapsack(df, max_capacity)
    
    elif algorithm == 'genetic':
        selected_items, total_weight, total_value = genetic_knapsack(df, max_capacity)
    
    else:  # algorithm == 'greedy'
        selected_items, total_weight, total_value = greedy_knapsack(df, max_capacity)
    
    efficiency = (total_weight / max_capacity) * 100 if max_capacity > 0 else 0
    
    return {
        'selected_items': selected_items,
        'summary': {
            'total_value': round(total_value, 2),
            'total_weight': round(total_weight, 2),
            'efficiency': round(efficiency, 2),
            'algorithm': algorithm,
            'capacity_used': f"{total_weight:.1f}/{max_capacity}",
            'num_selected': len(selected_items)
        }
    }

def prepare_download_data(items_data, results_data, max_capacity):
    """Prépare les données pour le téléchargement"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Créer un rapport complet
    report = {
        'configuration': {
            'max_capacity': max_capacity,
            'total_items': len(items_data) if items_data else 0,
            'timestamp': timestamp
        },
        'all_items': items_data,
        'optimization_results': results_data
    }
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    # Construire le chemin complet du fichier JSON
    filename = f"knapsack_results_{timestamp}.json"
    full_path = os.path.join(os.path.dirname(OUTPUT_PATH), filename)

    # Sauvegarder le fichier JSON
    with open(full_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Retourner un dict avec le contenu et le chemin du fichier pour téléchargement
    return dict(
        content=json.dumps(report, indent=2, ensure_ascii=False),
        filename=filename
    )
