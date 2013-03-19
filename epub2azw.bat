:: batch file with epub hyphens preprocessing
calibre-debug -e "%~dp0main.py" %1 "%~n1_temp.epub"
ebook-convert %1 "%~n1.azw3"  --change-justification justify
del "%~n1_temp.epub"
