# Frenchstone
An Hearthstone simulator
Version 0.0.1

<h2>Etapes</h2>

1. Création des classes, structures, et fonctions permettant de simuler une partie basique (passer son tour, jouer une carte, attaquer) jusqu'à sa fin + création du GitHub
2. Ajout des différentes mécaniques de jeu (bouclier divin, provocation etc...), et intégration dans le simulateur
3. Implémentation des cartes en elle-même + intégration dans le simulateur
4. Création d'une BDD de notre simulateur qui joue contre lui-même
5. Création d'un modèle machine learning d'apprentissage par renforcement 
6. Rincer et répéter la partie "jeu"  + "entraînement"
7. Profit ??

<h2>Règles du jeu</h2>
<h3>But du jeu</h3>
<p>Réduire la vie du héros de votre adversaire à zéro pour gagner la partie. La victoire se décide par tirage au sort si la vie des deux héros atteint zéro dans la même attaque.</p>

<h3>Principes du jeu</h3>
<p>Après avoir choisi une des 9 classes jouables du jeu, les joueurs utilisent un deck de 30 cartes. Il peut être composé de deux exemplaires d'une carte simple. En revanche, il contient une seule unité de carte légendaire. Le deck peut contenir plusieurs cartes légendaires pour autant qu'elles soient différentes. Il doit être composé à la fois de cartes identiques à toutes les classes et de cartes spécifiques à la classe choisie.</p>
<p>Au premier tour, les joueurs reçoivent 4 cartes. Ils peuvent modifier certaines d'entre-elles afin d'éviter d'avoir de grosses cartes impossibles à jouer en début de partie.</p>
<p>Un tirage au sort définit le joueur qui débutera la partie.</p>
<p>La ressource utilisée dans le jeu est le cristal de mana. Il est représenté sur les cartes par la gemme bleue qui se trouve en haut à gauche de la carte. Il est utilisé pour invoquer les serviteurs, les sorts et utiliser le pouvoir des héros ainsi que l'équipement.</p>
<p>Vous débutez la partie avec un point de cristal de mana. A chaque tour, vous recevez un point de mana supplémentaire. Le maximum de cristaux de mana collecté dans le jeu est de 10.</p>
<p>Chaque héros dispose d'une compétence propre qui lui coûte 2 cristaux de mana.</p>
<p>Le héros peut utiliser sa compétence à chaque tour.</p>
<p>Le héros s'accompagne de serviteurs dans la bataille grâce à des cartes serviteurs. Ceux-ci restent sur le champ de bataille et combattent pour le héros. Ils arrivent endormis sur le plateau de jeu et commencent à combattre au tour suivant. Le serviteur endormi et ne pouvant combattre est représenté par un "z" sur le plateau de jeu.</p>
<p>Le serviteur attaque l'adversaire à concurrence du nombre indiqué sur la gemme jaune flanquée d'une épée en bas à gauche de la carte.</p>
<p>La vie d'une carte est représentée par la gemme rouge en bas à droite.</p>
<p>Le serviteur peut avoir une compétence particulière. Elle est alors représentée par une icône brillante.</p>
<p> Le serviteur peut avoir un sous-type (bête, dragon, murloc, pirate, démon) qui l'influence.</p>
<p>Le serviteur dispose d'une compétence fréquente et non fréquente. La première n'est pas définie sur la carte comme Provocation (Taunt), Cri de bataille (Battlecry),.... Elle est donc à connaître. La seconde est celle spécifiée sur la carte.</p>
<p>Les cartes de sort n'ont pas de valeur d'attaque ou de vie. Elles sont jouées une seule fois et ensuite, elles sont perdues.</p>
<p>Les cartes d'arme/équipement ont une valeur d'attaque et de vie. Le héros utilise des cristaux de mana pour pouvoir porter cet équipement.</p>
<p>Quand le héros porte un équipement, la carte de celui-ci perd un point de durabilité à chaque fois que le héros frappe.</p>
<p>Il existe une différence entre les cartes portant une gemme en leur centre et les autres. Ces dernières sont des cartes basiques. Les autres sont des cartes plus précieuses. La couleur de la gemme indique la rareté de la carte.</p>
<p>Le fond de la carte de sort détermine la classe à laquelle elle appartient. Ainsi : pourpre est pour le Démoniste, le bleu-vert pour le Mage, le bleu pour le Chaman, le noir pour le Voleur, le brun foncé pour le Guerrier, le brun clair pour le Druide, le blanc pour le Prêtre, le vert pour le Chasseur et le rose pour le Paladin. Le fond de couleur gris indique que la carte n'est dédiée à aucune classe.</p>

<h3>Facilités sur le plateau de jeu</h3>
<p>Un bouton s'allume sur le plateau de jeu pour indiquer qu'il n'y a plus d'actions possibles.</p>
<p>Un journal de combat renseigne les actions qui viennent d'avoir lieu.</p>
<p>Les points de cristaux de mana de votre adversaire sont visibles sur le plateau de jeu non pas avec une barre de cristaux de mana mais juste le nombre.</p>