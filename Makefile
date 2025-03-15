SOURCE_FILE = main.pyw
EXE_NAME = generator v5.0
ICON = resources/icon1.png

all: clean build

.PHONY: build build_onefile clean
build:
	pyinstaller --name '$(EXE_NAME)' --add-data '$(ICON):resources' $(SOURCE_FILE)

build_onefile:
	pyinstaller --onefile --name '$(EXE_NAME)' --windowed --icon '$(ICON)' $(SOURCE_FILE)

clean:
	rm -rf dist *.spec
