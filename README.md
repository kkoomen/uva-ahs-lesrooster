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

# Gebruik

De algemene structuur is: `./main.py -a <algorithm> [OPTIONS]`

Waarbij `algorithm` één van de volgende waardes kan zijn:

- `random`
- `greedy`
- `random-greedy`
- `hillclimber`

`OPTIONS` kan zowel globale als algoritme specifieke opties kan bevatten.

- globale opties voor elk algoritme:
  - `-l, --log-level debug|info|warning|error|critical`
  - `-q, --quiet` toon geen stdout
  - `-e, --export ics|csv` exporteert timetable naar `ics` of `csv` formaat
  - `--iterations` aantal iteraties dat het algoritme moet runnen
  - `--plot-heatmap` plot de timetable heatmap
  - `--plot-stats` plot statistieken nadat het algoritme klaar is
- `random` algoritme opties:
  - `--random-walk` doe een random walk en plot de resultaten

Voor alle mogelijke opties, zie `./main.py --help`

### Voorbeelden

Random algoritme: <br/>
- `./main.py -a random -i 10`
- `./main.py -a random --random-walk -i 1000 --show-heatmap`
- `./main.py -a random -e csv`
- `./main.py -a random -e ics --show-heatmap`

Greedy algoritme: <br/>
- `./main.py -a greedy`
- `./main.py -a random-greedy --plot-stats`
- `./main.py -a greedy --show-heatmap`
- `./main.py -a greedy -e ics --show-heatmap`

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
