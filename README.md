# BiteTrack

## Apie projektą

**BiteTrack** – tai maisto vartojimo sekimo programa, leidžianti vartotojui įvesti informaciją apie suvalgytą maistą tekstu arba balsu. Programa naudoja dirbtinį intelektą, kad iš vartotojo pateikto aprašymo atpažintų patiekalus, sutvarkytų galimas rašybos klaidas ir pateiktų struktūrizuotą rezultatą.

Projektas sukurtas naudojant **Python** ir **Kivy**, o balso atpažinimui bei maisto analizavimui naudojamos **Groq API** paslaugos.

## Pagrindinės funkcijos

* **Balso įrašymas** – galima įrašyti vartotojo balsą per mikrofoną.
* **Kalbos pavertimas tekstu** – garso įrašas transkribuojamas naudojant `whisper-large-v3-turbo` modelį.
* **Maisto atpažinimas su DI** – tekstas analizuojamas naudojant `llama-3.3-70b-versatile` modelį.
* **Patiekalų išskyrimas** – iš vartotojo aprašymo atpažįstami maisto produktai ir patiekalai.
* **Lietuvių kalbos palaikymas** – sistema pritaikyta lietuviškiems maisto aprašymams.
* **Kalbos pasirinkimas** – palaikomos lietuvių ir anglų kalbos.
* **Automatinis įrašymo valdymas** – įrašymas nutraukiamas aptikus ilgesnę tylą arba pasiekus maksimalų įrašymo laiką.
* **Duomenų bazė** – programos duomenys saugomi SQLite duomenų bazėje.

## Kaip tai veikia?

1. Vartotojas aprašo, ką valgė, tekstu arba balsu.
2. Jei naudojamas balsas, programa įrašo garsą ir paverčia jį tekstu.
3. Gautas tekstas perduodamas dirbtinio intelekto modeliui.
4. Modelis ištaiso galimas rašybos ir žodžių galūnių klaidas.
5. Iš teksto atrenkami maisto produktai ir sudaromi patiekalai.
6. Vartotojui pateikiamas aptiktų patiekalų sąrašas.

### Pavyzdys

**Įvestis:**

> Šiandien vakare valgiau kebabą su česnakiniu padažu, o ryte valgiau cepelinus su kiauliena.

**Rezultatas:**

```text
Aptikti patiekalai:
- Patiekalas: Kebabas su česnakiniu padažu
- Patiekalas: Cepelinai su kiauliena
```

## Naudojamos technologijos

* **Python** – pagrindinė programavimo kalba.
* **Kivy** – grafinės vartotojo sąsajos kūrimui.
* **Groq API** – dirbtinio intelekto ir kalbos atpažinimo paslaugoms.
* **Llama 3.3 70B** – maisto ir patiekalų analizei.
* **Whisper Large V3 Turbo** – balso pavertimui tekstu.
* **NumPy** – garso duomenų apdorojimui.
* **SoundDevice** – garso įrašymui iš mikrofono.
* **python-dotenv** – API rakto nuskaitymui iš aplinkos kintamųjų.
* **SQLite** – lokaliems duomenims saugoti.
* **pytest** – automatiniams testams.
* **pytest-cov** – kodo padengimo analizei.

## Diegimas

### 1. Repozitorijos klonavimas

```bash
git clone https://github.com/NNTKLOne/BiteTrack.git
cd BiteTrack
```

### 2. Virtualios aplinkos sukūrimas

```bash
python -m venv .venv
```

**Windows:**

```bash
.venv\Scripts\activate
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

### 3. Priklausomybių įdiegimas

```bash
pip install -r requirements.txt
```

## API rakto nustatymas

Projektas naudoja `Groq API`, todėl reikalingas API raktas.

Projekto pagrindiniame kataloge sukurkite `.env` failą:

```env
API_KEY=jūsų_groq_api_raktas
```

Programa šį raktą naudoja prisijungimui prie Groq API maisto analizės ir balso transkribavimo funkcijoms.

> Svarbu: nekelkite `.env` failo ir savo API rakto į viešą repozitoriją.

## Balso įrašymo apribojimai

Balso įrašymo modulyje nustatyti šie apribojimai:

* minimali įrašo trukmė – 3 sekundės;
* maksimali įrašo trukmė – 30 sekundžių;
* maksimalus garso failo dydis – 6 MB;
* įrašymas gali būti automatiškai sustabdytas aptikus maždaug 2 sekundžių tylą.

## Projekto struktūra

```text
BiteTrack/
├── .github/
│   └── workflows/          # GitHub Actions darbo eigos
├── database/               # Duomenų bazės logika
├── test/                   # Testai
├── ui/                     # Grafinė vartotojo sąsaja
├── LLM.py                  # Maisto analizė naudojant DI
├── TranslationManager.py   # Vertimų valdymas
├── translations.py         # Vertimų duomenys
├── voiceToText.py          # Balso pavertimas tekstu
├── data.db                 # Programos duomenų bazė
├── identifier.sqlite       # SQLite duomenų bazė
└── requirements.txt        # Projekto priklausomybės
```

## Testavimas

Testams naudojamas `pytest`, o kodo padengimo analizei – `pytest-cov`.

Testų paleidimas:

```bash
pytest
```

Kodo padengimo patikrinimas:

```bash
pytest --cov
```

## Komanda

Prie projekto prisidėjo:

* **Vilius Ničiperovičius**
* **volvine**
* **Augustas Česnavičius**
