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
- `./main.py --help`

Example usages:
- `./main.py -a randomizer -i 10`: runs `Randomizer` algorithm 10 times
- `./main.py -a randomizer -e csv`: runs `Randomizer` algorithm once and export the results to `csv`
- `./main.py -a randomizer -e ics -p`: runs `Randomizer` algorithm once, export the results to `ics` and plot the data with matplotlib.

# Proces logboek

Ik houd een persoonlijk proces logboek bij in deze repo waar ik mijn proces en
resultaten beschrijf na elke fase te hebben afgerond.

[Klik hier](./docs/README.md) om het te bekijken.

# Project structuur

```
.
├── main.py             # main file to run
├── data                # contains all data files
├── code                # the main codebase
│   ├── algorithms      # contains different algorithms
│   ├── entities        # contains all entity classes
│   └── utils           # utility and helper functions
├── out                 # any generated output file will be put here
└── docs                # contains the documented process of this project
```

# Tests

TODO

# Auteurs

Kim Koomen, eerstejaars bachelorstudent KI, 2023.
