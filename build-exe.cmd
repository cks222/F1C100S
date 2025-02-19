pip install -r requirements.txt
pip install pyinstaller
pyinstaller run_index.spec --clean
rmdir /S /Q build