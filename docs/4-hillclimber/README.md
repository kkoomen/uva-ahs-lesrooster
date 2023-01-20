# 4. Hill climber

In deze fase heb ik een hill climber geïmplementeerd die alleen maar even goede
of betere oplossingen accepteert. Dit algoritme gaat door tot dat het aantal
opgegeven iteraties bereikt is, of als er na 200 iteraties geen strict betere
oplossing is gevonden.

:exclamation: Het moet hier *strict* beter zijn omdat het anders in een
oneindige loop terecht komt waarbij het even goede states kan krijgen, maar
nooit een betere.

In de baseline fase heb ik een random walk gemaakt die aantoont hoe de malus
score wordt beïnvloedt door het omwisselen van twee random activiteiten of door
het verwisselen van studenten binnen een vak.

Hieronder nog een keer de grafiek van de random walk als opfrisser:

![random walk with 10k iterations](../2-baseline/random-walk-plot.png)

Zoals te zien is heeft het verwisselen wel wat effect, maar niet veel na een
bepaald aantal iteraties. Het omwisselen van twee activiteiten heeft meer nut
naar mate het aantal iteraties groter wordt. Ik heb dus bedacht om in de hill
climber het volgende te doen:
- 40% kans om een activiteit naar een random ander tijdslot te doen (in mogelijk een andere zaal)
- 40% kans om twee activiteiten om te wisselen
- 20% kans om studenten te verwisselen

Bij hill climber beginnen we met "een oplossing". Ik heb zowel de randomizer als
het greedy algoritme gebruikt algoritme voor mijn initiële oplossing. Omdat mijn
greedy een betere oplossing geeft (met minder aantal maluspunten) heb ik ervoor
gekozen om de hill climber toe te passen op een greedy oplossing om zo een nóg
betere oplossing te genereren.

Hieronder is te zien hoe de hill climber te werk gaat met zowel de randomizer
als het greedy algoritme. Naar mate het aantal iteraties toe neemt, wordt de som
van violations en maluspunten minder en minder voor beide versies.

![hill climber based using greedy solution](./hillclimber-greedy.png)

![hill climber based using randomizer solution](./hillclimber-randomizer.png)

De greedy versie begon met een malus score van 118 en eindigde met 35 en de
randomizer versie begon met 1274 en eindigde met 51 waarbij beide versies
uiteindelijk het local optimum hadden bereikt.
