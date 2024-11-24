### README: Problème du Sac à Dos (Knapsack Problem Interface)

---

#### **Description**
Cette interface Dash permet de résoudre le problème du sac à dos en générant une liste d'objets aléatoires et en sélectionnant une combinaison optimale en fonction de leur poids, valeur, et de la capacité maximale du sac.

---

#### **Fonctionnalités**
1. **Génération d'objets aléatoires** :
   - Saisissez les paramètres d'entrée pour définir :
     - Nombre d'objets.
     - Capacité maximale du sac à dos.
     - Valeur maximale des objets.
   - Cliquez sur "Lister les objets disponibles" pour générer une liste d'objets.

2. **Affichage et modification des objets** :
   - Visualisez les objets générés sous forme de tableau interactif.
   - Modifiez directement les poids et les valeurs des objets si nécessaire.

3. **Optimisation du sac à dos** :
   - Cliquez sur "Lancer l'optimisation" pour sélectionner les objets offrant la valeur maximale sans dépasser la capacité.
   - Les résultats s'affichent dans un tableau séparé.

4. **Téléchargement des résultats** :
   - Téléchargez les objets sélectionnés sous forme de fichier Excel.

---

#### **Installation**
1. **Prérequis** :
   - Python 3.7 ou version ultérieure.
   - Pip pour la gestion des dépendances.

2. **Cloner le projet** :
   ```bash
   git clone <URL_DU_REPOTOIRE>
   cd <NOM_DU_PROJET>
   ```

3. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

4. **Installer GLPK** :
   - Téléchargez et installez le solveur GLPK nécessaire pour l'optimisation.
   - Ajoutez son chemin d'exécutable au `PATH` du système.

---

#### **Utilisation**
1. **Lancer le serveur** :
   ```bash
   python app.py
   ```

2. **Accéder à l'application** :
   - Ouvrez votre navigateur et accédez à `http://127.0.0.1:8050`.

3. **Étapes dans l'interface** :
   - Définissez les paramètres d'entrée : nombre d'objets, capacité maximale, valeur maximale.
   - Cliquez sur "Lister les objets disponibles".
   - Modifiez le tableau des objets si nécessaire.
   - Cliquez sur "Lancer l'optimisation".
   - Téléchargez les résultats si besoin.

---

#### **Structure des fichiers**
- `app.py` : Fichier principal contenant le code de l'interface Dash.
- `helpers.py` : Fichier contenant les fonctions pour :
  - Générer les objets aléatoires.
  - Résoudre le problème du sac à dos.
  - Gérer les téléchargements.
- `requirements.txt` : Liste des dépendances nécessaires.
- `custom.css` : Fichier optionnel pour la personnalisation des styles.

---

#### **Dépendances principales**
- [Dash](https://dash.plotly.com) : Framework pour la création d'interfaces web interactives.
- [Pyomo](http://www.pyomo.org/) : Bibliothèque Python pour l'optimisation mathématique.
- [Pandas](https://pandas.pydata.org/) : Analyse et manipulation de données.

---

#### **Exemple de fonctionnement**
1. Génération des objets :
   - Nombre d'objets : `100`
   - Capacité maximale : `50`
   - Valeur maximale : `100`

   Un tableau des objets s'affiche avec des colonnes `Item`, `Weight`, `Value`.

2. Optimisation :
   - Les objets sélectionnés respectant la contrainte de capacité sont affichés.

3. Téléchargement :
   - Le fichier Excel des résultats est téléchargé dans le répertoire spécifié.

---

#### **Problèmes courants**
1. **Erreur liée au solveur GLPK** :
   - Assurez-vous que GLPK est installé et accessible via le `PATH`.
2. **Interface inaccessible** :
   - Vérifiez que le serveur Dash est bien lancé et que le port 8050 n'est pas bloqué.

---

#### **Contributions**
Les contributions sont les bienvenues ! Créez une branche et soumettez une pull request.

---

#### **Auteur**
- **Nom** : Ouissal Boutouatou  
- **Contact** : [Votre email ou GitHub]  

---

Amusez-vous à résoudre des problèmes complexes avec cette interface ! 🚀
