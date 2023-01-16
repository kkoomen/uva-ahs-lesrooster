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

# Tests

TODO

# Auteurs

Kim Koomen, eerstejaars bachelorstudent KI, 2023.
