% TP5 : PERT & Ordonnancement
% Arthur Bit-Monnot ; Anaïs Lau
  

# Un problème PERT

## Solution de base

### Contraintes/1

`Contraintes(?Vars)` permet de poser les contraintes du problème de Pert défini dans le sujet de TP. Les variables du CSP sont représentées par chacune des tâches à accomplir.
Les contraintes sont posées comme suit :

 - Masonry n'ayant pas de tâches précédentes peut commencer n'importe quand (avec un temps positif) d'où `Masonry #>= 0`.
 - Le respect de la précédence est garanti par les contraintes du type `Carpentry #>= Masonry +7` qui assurent qu'une tâche s'effectue après la tâche qui la précède.

 
Pour optimiser le problème, nous avons ajouté à notre CSP une variable `MinFin`. Cette variable va nous permettre de minimiser la date de fin, et donc d'obtenir la solution optimale. 

```prolog
% Définit le CSP
% Pose les contraintes
contraintes(Vars) :-
  Vars = [Masonry, Carpentry, Roofing, Plumbing, Facade, Windows,
          Garden, Ceiling, Painting, Moving, Fin],
  % Contraintes de précédence entre les tâches
  Masonry #>= 0,
  Carpentry #>= Masonry +7,
  Roofing #>= Carpentry+5,
  Plumbing #>= Masonry+7,
  Facade #>= Plumbing+8,
  Facade #>= Roofing+1,
  Windows #>= Roofing+1,
  Garden #>= Plumbing+8,
  Garden #>= Roofing+1,
  Ceiling #>= Masonry+7,
  Painting #>= Ceiling+4,
  Moving #>= Windows+3,
  Moving #>= Garden+2,
  Moving #>= Facade+2,
  Moving #>= Painting+2,
  Fin #= Moving+1-1,
  % Recherche de la solution optimale
  % Minimisation de la variable Fin
  mindomain(Fin, MinFin),
  Fin #= MinFin.
```

### Main/1

`Main(?X)` permet de poser le problème, d'afficher les variables du problème et renvoie la solution optimale.

```prolog
% Résout le problème de PERT
% Renvoie pour chaque var un intervalle de temps correspondant à 
%   la date de début de la tâche
main(Vars) :-
  contraintes_disjonction(Vars), % Pose les contraintes
  Vars = [Masonry, Carpentry, Roofing, Plumbing, Facade, Windows,
          Garden, Ceiling, Painting, Moving, Fin],
  writeln(Vars). % Affiche la solution
```

### Résolution du problème

L'exécution du main nous renvoie diverses informations telles que le coût optimal, les tâches critiques et les intervalles exécution des tâches non critiques.
En effet, on aperçoit que certaines variables ont un intervalle unique ; ce sont les tâches critiques. Cela signifie que, pour atteindre la solution optimale, il est impératif que la tâche commence à la date donnée (par exemple, 0 pour la première variable).

Les autres tâches (celles qui ne sont pas critiques) peuvent démarrer à n'importe quelle date appartenant à l'intervalle renvoyé sans dégrader la solution optimale.

```
?- main(X).
[0, _843{[7, 8]}, _986{[12, 13]}, 7, 15, _1522{[13, 14]}, 
 15, _1813{[7..11]}, _1950{[11..15]}, 17, 17]
----> Cout optimal  17
```

Les tâches critiques sont Masonry, Plumbing, Façade, Garden, Moving et Fin.

![Dates de début des différentes taches](res/pert.csv)


## Prise en compte des contraintes disjonctives

### Disjonction

Le prédicat contraintes_disjonction/1 ne diffèrent pas énormément du prédicat contraintes/1 décrit précédemment. Nous avons seulement ajouté les contraintes de disjonction sur les tâches Carpentry, Ceiling et Roofing. Ces contraintes ont été posées grâce au prédicat disjunction/4 qui fait en sorte que les deux tâches passées en paramètre s'exécute l'une après l'autre.

```prolog
% Définit le CSP
% Pose les contraintes   
contraintes_disjonction(Vars, Flags) :-
  % Variables du problème
  Vars = [Masonry, Carpentry, Roofing, Plumbing, Facade, Windows,
          Garden, Ceiling, Painting, Moving, Fin], 
  Fin :: 17..25,
  % Contraintes de précédence
  Masonry #>= 0,
  Carpentry #>= Masonry +7,
  Roofing #>= Carpentry+5,
  Plumbing #>= Masonry+7,
  Facade #>= Plumbing+8,
  Facade #>= Roofing+1,
  Windows #>= Roofing+1,
  Garden #>= Plumbing+8,
  Garden #>= Roofing+1,
  Ceiling #>= Masonry+7,
  Painting #>= Ceiling+4,
  Moving #>= Windows+3,
  Moving #>= Garden+2,
  Moving #>= Facade+2,
  Moving #>= Painting+2,
  Fin #= Moving+1-1,
  % Contraintes de disjonction
  disjunction(Carpentry,5,Ceiling,4,F1),
  disjunction(Carpentry,5,Roofing,1,F2),
  disjunction(Ceiling,4,Roofing,1,F3),
  Flags = [F1, F2, F3].
```

### `Solve_disjonction/1`

`Solve_disjonction/1` permet de résoudre le problème de PERT de manière optimale. Il renvoie un intervalle de temps pour les tâches non critiques.

La méthode ici est de résoudre le problème sur une première instance par un branch and bound. Les tâches sont donc ordonnées et les flags correspondant de la contraintes dijunctives sont positionnés également à 1 ou 2.

Dans un deuxième temps, on pose les contraintes sur une nouvelle liste. Mais cette fois, les flags (troisième argument de `disjunctive/3`) instanciés lors de la résolution précédente sont réutilisés. On obtient donc le même ordonnancement que pour la liste précédente, mais les tâches garde leur degré de liberté.

```prolog
% Résout le problème de PERT avec disjonctions
% Renvoie pour chaque var un intervalle de temps correspondant 
%  à la date de début de la tâche
solve_disjonction(X) :-
  Vars = [Masonry, Carpentry, Roofing, Plumbing, Facade, Windows,
          Garden, Ceiling, Painting, Moving, Fin],
  contraintes_disjonction(VarsTmp, Flags), % Pose les contraintes
  find_min(VarsTmp),
  contraintes_disjonction(Vars, Flags),  % Même ordre
  mindomain(Fin, MinFin), 
  Fin #= MinFin,
  write(Vars),nl,
  writeln(MinFin).

% Effectue un branche and bound cherchant à minimiser Fin
find_min(Vars) :-
  Vars = [Masonry, Carpentry, Roofing, Plumbing, Facade, Windows,
          Garden, Ceiling, Painting, Moving, Fin],
  minimize(labeling(Vars),Fin).
```



### Résolution du problème 

L'ajout des contraintes a effectivement retardé la fin du projet. La solution optimale n'est plus 17 mais 19.
Le chemin critique a également changé. Les tâches critiques sont maintenant : Masonry, Carpentry, Roofing, Ceiling, Painting, Moving et Fin.
On remarque que les tâches Carpentry, Ceiling, Roofing qui ne peuvent se chevaucher dans le temps font maintenant partie du chemin critique.

```
Found a solution with cost 19
[0, 7, 12, _4193{[7..9]}, _4330{[15..17]}, _4562{[13..16]}, 
      _4699{[15..17]}, 13, 17, 19, 19]
19
```



# Problèmes d'ordonnancement d'atelier de type JobShop


## Main

Notre problème comporte autant de variables que de tâches pour le problème de Jobshop donné. Nous y avons ajouté une dernière variable correspondant au makespan, c'est-à-dire la valeur à optimiser lors de la résolution d'un problème de Jobshop.

Pour ce problème, nous avons dû définir deux types de contraintes :

 - celles relatives à l'ordre d'exécution des tâches, notamment pour le respect de la précédence
 - celles relatives à la répartition des tâches sur les machines grâce au prédicat `disjunctive/3`
 
```prolog
% Résout le problème de JobShop
% Renvoie le makespan
main(Vars) :-
  % Listes des taches de types J(num job, num tache)
  Vars = [J11,J12,J21,J22,J23,J31,J32,J33,Makespan],
  J11 #>= 0,
  J21 #>= 0,
  J31 #>= 0,
  % Contraintes de précédences
  J12 #>= J11 + 5,
  J22 #>= J21 + 3,
  J23 #>= J22 + 5,
  J32 #>= J31 + 4,
  J33 #>= J32 + 2,
  Makespan #>= J12 + 2,
  Makespan #>= J23 + 4,
  Makespan #>= J33 + 6,
  % Disjonction au niveau des machines
  disjunctive([J11, J21, J32], [5, 3, 2], F1),   % M1
  disjunctive([J12, J23, J33], [2, 4, 6], F2),   % M2
  disjunctive([J31, J22], [4, 5], F3),           % M3
  Vars :: 0..24, % Vars:: 0..2*H avec H=12
  minimize(labeling(Vars), Makespan),
  writeln(Vars).
```

## Résolution du problème

Lors de l'exécution de notre programme, nous avons calculé un makespan de 18 avec la répartition des tâches suivantes :

```
?- main(X).
Found a solution with cost 18
[6, 12, 0, 4, 14, 0, 4, 6, 18]
```

![Solution trouvée au problème de jobshop](res/jobshop.png)

Remarque : Chaque valeur de la liste retournée représente la date de début de la tâche correspondante. 




# Extension : Programme de résolution de jobshop générique

## Lecture du problème

Pour le parsage des instances JobShop, nous nous sommes basés sur la code mis à notre disposition et avons légèrement modifié la lecture pour construire une liste de Jobs, contenant une liste de taches.

Chaque tache est stockée dans un tableau de dimension 3 contentant `[]( Date de début, Ressource, Durée )`.
Une instance jobshop à deux jobs et deux machines peut ainsi être représentées de la manière suivante : 

```prolog
[
  [ []( [{0..10}], 1, 13 ),  []( [{0..10}], 2, 12 )   ],
  [ []( [{0..10}], 2, 16 ),  []( [{0..10}], 1, 11 )   ]
]
```


Lecture et construction de l'instance (seule la partie modifiée est présentée):

```prolog
   (for(_I,1,Nb_Jobs), foreach(Job, Jobs), param(Nb_Ressources, Stream)
   do
      (for(_J,1,Nb_Ressources), foreach(Task, Job), param(Stream)
      do
         read_token(Stream, Ressource_IJ, integer),
         read_token(Stream, DurationIJ, integer),
         write([Ressource_IJ, DurationIJ]),
         Task = [](_, Ressource_IJ, DurationIJ)
      ),
      nl
   ),
```


## Pose des contraintes job

Dans un problème de JobShop, les taches d'un même job doivent être exécutées dans l'ordre. Cette contrainte est posée par le prédicat `contraintes_jobs/1`.

Ce prédicat construit une liste de taches pour chaque job et y applique la contraintes globale `disjunctive/3`. On force ensuite l'ordre en forçant tous les flags à `1`.

```prolog
% Pose les contraintes du job : toutes les taches d'un même
% job doivent être réalisées dans l'ordre
contraintes_jobs(Jobs) :-

  (foreach(Job, Jobs) do
    (foreach(Task, Job), foreach(Start, StartDates), foreach(Duree, Durees) do
      Start is Task[1],
      Duree is Task[3]
    ),
    
    term_variables(StartDates, Vars),
    Vars :: 0..5000,
    
    fd:disjunctive(StartDates, Durees, Flags),
    (foreach(Flag, Flags) do
       Flag #= 1
    )
  ).
```

## Définition du domaine

On définit le domaine des variables comme étant deux fois le makespan du problème relâché (sans les contraintes machine). De cette manière, le domaine va de `0` au double de la durée du job le plus long.

Le prédicat `set_max_domain/2` définit ainsi le domaine de toutes les variables du problème. Il doit être appelé après la pose des contraintes job et avant la pose des contraintes ressources.

```prolog
% Le domaine des variables est 2*H où H est la
%   plus grande date de fin dans le problème relaché
%   (pas de disjonction pour les ressources)
set_max_domain(Grid, Makespan) :-
  (foreach(Job, Grid), param(Makespan) do 
      last(Tache, Job),
      DateDebut is Tache[1],
      Duree is Tache[3],
      Makespan #>= DateDebut + Duree
  ),
  mindomain(Makespan, MinMakespan),
  Makespan #<= 2*MinMakespan,
  
  term_variables(Grid, Vars),
  Vars :: 0..MinMakespan*2.
```

## Pose des contraintes ressources

Les contraintes ressources sont posées en utilisant un `disjunctive/3` sur toutes les taches partageant une ressources.

Pour cela, le prédicat `append_tasks_of_ressource(Tasks, NumRessource, Old, New)` produit une liste de taches partageant la même ressource `NumRessource`.

Note : les flags sont disponibles en paramètre de `contraintes_ressources` pour pouvoir travailler dessus par la suite.

```prolog
% Pose une disjonction sur toutes les taches partageant une ressource
contraintes_ressources(Grid, NbRessources, AllFlags) :-
  all_tasks(Grid, Tasks),
  
  (for(NumRessource, 0, NbRessources-1), 
   foreach(FlagsForI, AllFlags), param(Tasks) 
  do
    
    append_tasks_of_ressource(Tasks, NumRessource, [], TasksOnRessourceI),
    
    (foreach(Task, TasksOnRessourceI), foreach(Start, StartDates), 
                                       foreach(Duree, Durees) 
    do
      Start is Task[1],
      Duree is Task[3]
    ),
    
    disjunctive(StartDates, Durees, FlagsForI)
  ).
  
% Extrait toutes les taches d'une grille et les place dans une liste
%   c'est en réalité juste un flatten de profondeur 1
all_tasks(Grid, AllTasks) :-
  flatten(1, Grid, AllTasks).

  
% Filtre tous les éléments d'un liste ayant pour ressource Ressource.
% Ces éléments sont placés dans la liste New
append_tasks_of_ressource([Tache | Rest], Ressource, Old, New) :-
  TRessource is Tache[2],
  TRessource = Ressource,
  append_tasks_of_ressource(Rest, Ressource, [Tache | Old], New).
   
append_tasks_of_ressource([Tache | Rest], Ressource, Old, New) :-
  append_tasks_of_ressource(Rest, Ressource, Old, New).
  
append_tasks_of_ressource([], _, Old, Old).
```

## Résolution

La résolution d'un problème de jobshop suit donc les étapes suivantes : 

 - chargement de l'instance
 - pose des contraintes jobs 
 - définition du domaine des variables
 - pose des contraintes ressources
 - résolution : ici deux méthodes ont été testée

```prolog
main(InstanceName, Grid, Makespan) :-
  get_problem_data(InstanceName, Grid, NbJobs, NbRessources),
  contraintes_jobs(Grid),
  set_max_domain(Grid, Makespan),
  contraintes_ressources(Grid, NbRessources, Flags),
  writeln(Grid),
  solveByFlags(Flags, Makespan),
%  solveByDates(Grid, Makespan),
  show(Grid).
```

### Résolution par les dates

Un première approche est de travailler directement sur les dates de début des taches. On utilise pour cela une approche gloutonne qui instancie en premier les variables ayant la plus petite borne inférieure de domaine. On utilise pour cela le prédicat `deletemin/3`.

```prolog
% Essaye de résoudre une instance JobShop en instanciant les dates
% de début de taches. 
% Les dates sont instanciées en commençant par celles avec le plus petit domaine.
% Timeout : 2 minutes
solveByDates(Grid, Makespan) :-
  term_variables(Grid, Vars), !,
  minimize(labelmin(Vars), Vars, Vars, Makespan, -100000, 100000, 0, 120),
  mindomain(Makespan, Min),
  Makespan = Min.

% Instancie toutes les variables en commençant par celle 
%  avec le plus petit mindomain
labelmin([]).
labelmin(Vars) :-
  deletemin(Var, Vars, Rest),
  indomain(Var),
  labelmin(Rest).
```



### Résolution par les flags

Notre autre approche a été de travailler sur les flags qui positionnent les taches les une par rapport aux autres.

Ces variables sont intéressantes car elles ont un domaine réduit (avant ou après) tout en représentant le même nombre de solution. L'instanciation de ces flags aura pour effet de forcer le placement d'une tache avant une autre. Ceci actualisera son domaine et influera donc le makespan calculé.

```prolog
% Essaye de résoudre une instance en JobShop en positionant les
%  taches les unes par rapport au autres.
% Ceci est fait en instanciant les flags de disjunctive
solveByFlags(Flags, Makespan) :-
  term_variables(Flags, Vars), !,
  minimize(labeling(Vars), Vars, Vars, Makespan, -100000, 100000, 0, 120),
  mindomain(Makespan, Min),
  Makespan = Min.
```

Note : après la résolution, on force le makespan à sa valeur minimale pour obtenir les domaines de liberté des taches.

## Résultats

### Résultats par instanciation des dates

```prolog
?- main(ft06, G, M).
G = [[[](24, 2, 1), [](25, 0, 3), ... ]]
M = 70
There are 12 delayed goals.
Yes (119.76s cpu, solution 1, maybe more)
Found a solution with cost 70
```

La méthode gloutonne trouve très rapidement une bonne solution mais a ensuite énormément de difficultés à l'améliorer.

Sur l'instance FT06, une solution relativement bonne de 70 est trouvée dans la première seconde. Eclipse continue ensuite à chercher jusqu'au timeout (2 minutes).

### Résultats par instanciation des flags

La résolution par les flags trouve au contraire une solution initialement moins bonne mais est ensuite capable de l'améliorer rapidement.

```
?- main(ft06, G, M).
G = [[[](_956{[5..7]}, 2, 1), [](_939{[6..11]}, 0, 3), ... ]
M = 55
There are 31 delayed goals.
Yes (5.53s cpu, solution 1, maybe more)

Found a solution with cost 94
Found a solution with cost 87
Found a solution with cost 83
Found a solution with cost 81
Found a solution with cost 78
Found a solution with cost 77
Found a solution with cost 73
Found a solution with cost 70
Found a solution with cost 68
Found a solution with cost 67
Found a solution with cost 66
Found a solution with cost 65
Found a solution with cost 64
Found a solution with cost 62
Found a solution with cost 61
Found a solution with cost 60
Found a solution with cost 59
Found a solution with cost 58
Found a solution with cost 57
Found a solution with cost 56
Found a solution with cost 55
```

Ici, la solution optimale de l'instance FT06 est trouvée en 5 secondes.

### Point à améliorer

Bien que notre méthode produise des résultats satisfaisant sur des très petites instances, il reste difficile et très lent d'améliorer sa solution initiale sur de grosses instances.

Il faudrait pour cela pour effectuer une recherche plus guidée. Une solution à cela serait de mettre permuter en priorité deux taches consécutives sur le chemin critique.
En effet la date de fin d'une instance est contrainte par les taches n'ayant aucun degré de liberté. C'est donc en les échangeant entre elles qu'on pourrait améliorer une solution existante.

Cette solution n'a pas été implémentée car elle nécessitait une priorité dynamique entre les variables (le chemin critique change quasiment à chaque solution). De plus, elle aurait nécessité des structures plus complexes pour faire la correspondance entre les flags et les taches, trouver lesquelles sont consécutives ...

