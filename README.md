## Anko - A Primitive Anki
Anko is a flashcard memorising app just like Anki, but creating a card deck is as easy as writing plain text file with indented lines.
![Anko Screen Shot][product-screenshot]

## Introductory Demo
[![Watch the video](product-demo-1-thumbnail)](https://github.com/user-attachments/assets/1413d26d-9f48-4ca7-88fd-f8ef1aeb5b42)

## Getting Started
### Prerequisites
You need to have python environment installed with venv
in Linux environment
```sh
python3 -m venv env1
. env1/bin/activate
pip3 install pandas numpy
```
or in Windows PowerShell
```powershell
python -m venv env1
. env1\Scripts\Activate.ps1
pip install pandas numpy
```

### Running the app
```sh
git clone https://github.com/mightyrabbit99/anku.git
cd anku
python src/main.pyw
```
### Building the app
For now I am using Makefile as a build script, to build the executable, it is as simple as running
```sh
make
```

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[product-screenshot]: res2/screenshot1.png
[product-demo-1-thumbnail]: res2/thumbnail1.png
