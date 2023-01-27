# Lesrooster

![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/kkoomen/uva-ahs-lesrooster/test.yml?label=tests)

Deze repository bevat een implementatie voor de
[Lectures & Lesrooster](https://ah.proglab.nl/cases/lectures-en-lesroosters)
case voor de UvA en het gedocumenteerde proces dat is bijgehouden tijdens dit
project.

# Table of Contents

- [Lesrooster](#lesrooster)
- [Table of Contents](#table-of-contents)
- [Proces logboek](#proces-logboek)
- [Project eisen](#project-eisen)
- [Installatie](#installatie)
- [Gebruik](#gebruik)
    + [Voorbeelden](#voorbeelden)
- [Project structuur](#project-structuur)
- [Constraints](#constraints)
- [Tests](#tests)
- [Auteurs](#auteurs)

# Proces logboek

Ik houd een persoonlijk proces logboek bij in deze repo waar ik mijn proces en
resultaten beschrijf na elke fase te hebben afgerond.

[Klik hier](./docs/README.md) om het te bekijken.

# Project eisen

Dit project vereist Python 3.9 of hoger.

# Installatie

- `git clone https://github.com/kkoomen/uva-ahs-lesrooster && cd uva-ahs-lesrooster`
- `python3 -m venv env`
- `source ./env/bin/activate`
- `pip3 install -r requirements.txt`

# Gebruik

De algemene structuur is: `./main.py -a <algorithm> [OPTIONS]`

Waarbij `<algorithm>` één van de volgende waardes kan zijn:

- `random`
- `greedy`
- `random-greedy`
- `greedy-lsd`
- `hillclimber`
- `tabu-search`

`OPTIONS` kan zowel globale als algoritme specifieke opties kan bevatten.

- globale opties voor elk algoritme:
  - `-l, --log-level debug|info|warning|error|critical`
  - `-q, --quiet` toon geen stdout
  - `-e, --export ics|csv|json` exporteert timetable naar `ics`, `csv` of `json` formaat
  - `-i, --iterations <number>` aantal iteraties dat het algoritme moet runnen
  - `-s, --plot-stats` plot statistieken nadat het algoritme klaar is
  - `--plot-heatmap` plot de timetable heatmap
- `random` algoritme opties:
  - `--random-walk` doe een random walk en plot de resultaten (moet in combinatie met `-i <number>`)

Voor alle mogelijke opties, zie `./main.py --help`

### Voorbeelden

Random algoritme:
- `./main.py -a random -i 10`
- `./main.py -a random --random-walk -i 1000 --show-heatmap`
- `./main.py -a random -e csv`
- `./main.py -a random -e ics --show-heatmap`

Greedy algoritme:
- `./main.py -a greedy`
- `./main.py -a random-greedy -s`
- `./main.py -a greedy --show-heatmap`
- `./main.py -a greedy -e ics --show-heatmap`

Visualisaties:
- `./main.py --visualization course-conflicts`: Visualiseer de course vak conflicten met graph coloring
- `./main.py --visualization hillclimber -i <iterations>`: Pas hill climber toe op verschillende algoritme en plot het resultaat
- `./main.py --visualization hillclimber-vs-tabu -i <iterations>`: Vergelijk hill climber en tabu search met elkaar

# Project structuur

```
.
├── main.py             # hoofdbestand
├── data                # bevat alle (csv) data bestanden
├── code                # de codebase zelf
│   ├── visualizations  # bevat visualisaties voor het genereren van statistieken
│   ├── algorithms      # bevat diverse algoritme implementaties
│   ├── entities        # bevat alle entiteiten
│   └── utils           # utility en helper functions
├── out                 # alle ics/csv/json exports komen hier terecht
├── docs                # bevat het gedocumenteerde proces van dit hele project
└── test                # bevat unit tests
```

# Constraints

Hard constraints:

- In elk tijdslot mag elke zaal maximaal 1 keer geboekt worden
- Alleen de zaal met de grootste capaciteit mag geboekt worden van 17:00 - 19:00
- 3 of meer tussensloten per student is niet toegestaan

Soft constraints (maluspunten):

- Elke activiteit ingeboekt in het 17:00 - 19:00 tijdslot geeft 5 maluspunten
- 1 tussenslot tussen twee andere activiteiten per student geeft 1 maluspunt
- 2 tussensloten tussen twee andere activiteiten per student geeft 3 maluspunten
- Elk vak conflict per student per tijdslot geeft 1 maluspunt
- Elke student die niet meer in een zaal past geeft 1 maluspunt
- Elk dubbel ingeplande activiteit per tijdslot voor elk vak geeft 1 maluspunt (extra)

# Tests

- `coverage run -m pytest`: run alle tests
- `coverage report`: toon code coverage (kan alleen nadat je `coverage run` hebt uitgevoerd)

Alle entities en utils hebben tests waar nodig:

```
Name                         Stmts   Miss  Cover
------------------------------------------------
code/entities/course.py         45      0   100%
code/entities/event.py          38      0   100%
code/entities/room.py           15      0   100%
code/entities/student.py        10      0   100%
code/entities/timeslot.py       90      0   100%
code/entities/timetable.py     283      0   100%
code/utils/constants.py          5      0   100%
code/utils/data.py              49      0   100%
code/utils/enums.py              6      0   100%
code/utils/helpers.py           53      0   100%
------------------------------------------------
TOTAL                          594      0   100%
```

# Auteurs

Kim Koomen, eerstejaars bachelorstudent KI, 2023.
