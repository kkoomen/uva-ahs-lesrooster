# 2. Baseline
Ik had al random timetable gegenereerd in de representation versie, maar in de
baseline versie ga ik dit omzetten naar een Randomizer class waarbij de data
gelinkt is met elkaar op basis van de opdracht.

De onderstaande lijst toont de activiteiten die ik tijdens de **baseline** fase
respectievelijk heb gedaan:
- Randomizer class maken
- constraints bedenken
- datastructuur aangepast, want ik merkte dat het niet werkte op lange termijn
  (nieuwe structuur staat mij toe om code meer gescheiden te houden en om
  makkelijker constraints te checken)
- studenten toewijzen aan de course waar ze staan ingeschreven
- de werkcolleges en practica verdelen obv de capaciteit (probeer aantallen
  gelijk te maken, want dan is er nog ruimte om studenten over te plaatsen)
- de activiteiten inplannen in een zaal die groot genoeg is in capaciteit voor
  de activiteit
- event swapping logica implementeren
- tussensloten minimaliseren logica implementeren
- ICS export

Nadat ik het aantal studenten heb opgesplitst op basis van de werkcollege en
practicum capaciteit moest het 129 tijdsloten verdelen binnen 145 beschikbare
tijdsloten. Zonder groepen kon de Randomizer elke keer een oplossing genereren
met minder dan 10 retries, nu kost het al 44 retries gemiddeld over 100
gegenereerde oplossingen.

Vervolgens heb ik ook nog de activiteiten ingepland in een zaal waar de
capaciteit groot genoeg is voor die activiteit. Nadat ik dit had geïmplementeerd
kwam de Randomizer soms in een oneindige loop terecht met nog een aantal
evenementen die het niet kon inplannen binnen een bepaalde aantal iteraties. Dit
liep op tot wel 100.000+ iteraties en nog steeds ging het fout. Dit komt omdat
bij het aanpassen van een violated event worden de studenten niet verwisseld
naar mogelijk andere events indien mogelijk. Tenslotte hebben werkcolleges en
practicums de mogelijkheid om meerdere groepen te hebben o.b.v. het aantal
inschrijvingen en de capaciteit per werkgroep of practicum.

Ik had eerst studenten omgewisseld binnen de violated events, maar dit gaf geen
oplossing, want misschien heeft 1 vak 3 groepen aan werkcolleges, maar als er
maar 1 groep gemarkeerd wordt als violated, dan verwissel ik het alleen met
zichzelf. Ik moet dus de studenten wisselen binnen alle drie de werkcolleges.
Helaas was het wisselen van studenten binnen het aantal events van een
activiteit type (hc, wc of pr) ook niet voldoende. Ook hier gaf het vrijwel
dezelfde resultaten als dat ik niet de studenten zou omwisselen.

Vervolgens heb ik geprobeerd om elke violation (event) om te wisselen met een
random ander event dat geen violation is. Dit werkte plotseling verbazingwekkend
goed. Heel af en toe raakte het in een infinite loop, dus ik heb een extra check
toegevoegd dat de randomizer stopt na 2000 retries.

Resultaat van 5000 iteraties:
- Min. retries: 20
- Max. retries: 2000
- Avg. retries: 162
- Solutions: 4974/5000

Het omwisselen van events was zeker een stap in de goede richting.

Ik heb het omwisselen van events getest met én zonder het wisselen van
studenten. Helaas heeft het wisselen van studenten geen effect binnen 5000
iteraties, dus ik heb uiteindelijk alleen gebruik gemaakt van het omwisselen van
events.

Uiteindelijk heb ik nog rekening gehouden met tussensloten. Als er 1 of 2
tussensloten zitten tussen twee vakken, dan geeft dit puur maluspunten. Als er 3
(of meer) tussensloten zitten tussen twee vakken, dan worden beide vakken
gemarkeerd als violations.  Dit is hetgeen dat het aantal acties doet vergroten
en het aantal oplossingen drastisch naar beneden haalt. Na dit geïmplementeerd
te hebben zijn er nog maar gemiddeld 3/10 succesvolle oplossingen, maar als er
een oplossing uitkomt, dan is het wel een zeer goede oplossing ;)

Hieronder nog een screenshot van een oplossing in de baseline versie. In de
afbeelding is te zien dat tijdsloten meer naar boven worden gehaald en dat er
niks meer in het laatste tijdslot van 17:00 - 19:00 zit.

![heatmap](./heatmap.png)

Uiteindelijk heb ik geïmplementeerd dat ik de timetable naar `ics` bestanden kan
exporteren. Er wordt een `ics` bestand met alle events weggeschreven en ook nog
per vak een `ics` (voor debugging erg handig!)

Hieronder heb ik wat screenshots van hoe de `ics` bestanden er in Apple Calendar
uitzien.

Hier heb ik 3 `ics` bestanden van 3 verschillende vakken geïmporteerd.

![ics partial](./ics-partial.png)

en hieronder nog een screenshot van alle 29 vakken en hun planningen samen,
gewoon omdat het kan.

![ics full](./ics-full.png)
