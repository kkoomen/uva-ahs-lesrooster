# Lesrooster

Deze repository bevat een implementatie voor de
[Lectures & Lesrooster](https://ah.proglab.nl/cases/lectures-en-lesroosters)
case voor de UvA en het gedocumenteerde proces dat is bijgehouden tijdens dit
project.

# Installatie

- `git clone https://github.com/kkoomen/uva-ahs-lesrooster && cd uva-ahs-lesrooster`
- `python3 -m venv env`
- `./env/bin/activate`
- `pip3 install -r requirements.txt`

Gebruik maken van het programma kan op de volgende manieren:
- `./main.py -a random -i 10`: run `Randomizer` algoritmen 10 keer
- `./main.py -a random -e csv`: run `Randomizer` algoritmen één keer en
  exporteert het resultaat naar `csv`
- `./main.py -a random -e ics -p`: run `Randomizer` algoritmen één keer,
  exporteer het resultaat naar `ics` en plot de data met `matplotlib`

Voor alle mogelijke opties, zie `./main.py --help`

# Proces logboek

Ik houd een persoonlijk proces logboek bij in deze repo waar ik mijn proces en
resultaten beschrijf na elke fase te hebben afgerond.

[Klik hier](./docs/README.md) om het te bekijken.

# Project structuur

```
.
├── main.py             # hoofdbestand
├── data                # bevat alle (csv) data bestanden
├── code                # de codebase zelf
│   ├── algorithms      # bevat diverse algoritme implementaties
│   ├── entities        # bevat alle entiteiten
│   └── utils           # utility en helper functions
├── out                 # alle ics/csv exports komen hier terecht
└── docs                # bevat het gedocumenteerde proces van dit hele project
```

# Constraints

Hard constraints:

- In elk tijdslot mag elke zaal maximaal 1 keer geboekt worden
- Alleen de zaal met de grootste capaciteit mag geboekt worden van 17:00 - 19:00
- 3 of meer tussensloten per student is niet toegestaan
- (extra) Elk tijdslot mag per vak maar 1 activiteit type hebben (maximaal 1
  hoorcollege OF 1 of meer werkcolleges/practicums van dit vak)

Soft constraints (malus points):

- Elke activiteit ingeboekt in het 17:00 - 19:00 tijdslot geeft 5 maluspunten.
- 1 tussenslot tussen twee andere activiteiten per student geeft 1 maluspunt.
- 2 tussensloten tussen twee andere activiteiten per student geeft 3 maluspunten.
- Elk vak conflict per student per tijdslot geeft 1 maluspunt.
- Elke student die niet meer in een zaal past geeft 1 maluspunt.

# Tests

TODO

# Auteurs

Kim Koomen, eerstejaars bachelorstudent KI, 2023.
