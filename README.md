# PSNES Language Game Manager

A Python utility that changes the language of a PSNES installation and manages game installation/removal.

## Features

* Language selection.
* Automatic `gamelist.xml` installation.
* Automatic font replacement (`default.ttf`).
* Game manager with image preview.
* Install and remove games.
* Configurable source and destination directories.
* PyInstaller compatible.

## Requirements

* Python 3.10+
* Pillow

Install dependencies:

```bash
pip install pillow
```

Run:

```bash
python LanguageInstaller.py
```
Create .exe:

```py -m PyInstaller --clean --onefile --windowed --icon=icono.ico --add-data "Languages;Languages" --add-data "font;font" --add-data "icono.ico;." LanguageInstaller.py ```




## Note

The `games/` directory is not included in this repository because it may contain copyrighted ROMs and media files.
