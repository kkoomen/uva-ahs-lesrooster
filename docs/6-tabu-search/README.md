# 6. Tabu Search

Na het implementeren van de Greedy LSD heb ik de tabu search geïmplementeerd
naar aanleiding van meerdere wetenschappelijke artikelen die hebben aangetoond
dat Tabu Search goed werkt bij het inplannen van roosters, vooral bij het
inplannen van examens.

Bij tabu search wordt er voor elke iteratie een n-aantal neighbors gegenereerd
waarbij elke neighbor een kleine aanpassen heeft op basis van de beste mogelijke
oplossing. Elke neighbor moet een valide oplossing zijn, oftewel 0 violations en
dat maakt het dat het slomer wordt naar mate de maluspunten kleiner wordt. Om
het algoritme snel te houden heb ik er voor gekozen om precies één oplossing te
genereren.

# Tabu Search vs Hill Climber

Tot mijn verbazing doet de Hill Climber het over het algemeen veel beter dan de
tabu search.

Als er geen einde is, dan zou tabu search lager moeten uitkomen dan de hill
climber. Het feit dat hill climber het hier beter lijkt te doen is mogelijk
omdat er heel veel local optimums zijn in deze casus, waardoor de hill climber
het erg goed doet.

![tabu search versus hill climber results for 10k iterations](./stats.png)
