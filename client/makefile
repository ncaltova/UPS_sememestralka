CMD=python3 -m PyInstaller
IMG="./img;img/"
FONT="./fonts;fonts/"
ICO="./img/logo.ico"
MAIN="./main.py"
FLAGS= --noconfirm --onefile --distpath ./ --hidden-import pygame --windowed --icon $(ICO) --name "MauMau" --clean --add-data $(IMG) --add-data $(FONT)
BUILD=$(CMD) $(FLAGS)  $(MAIN)
DIST=dist

all: build

build:
	pip3 install -r ./requirements.txt
	$(BUILD)

