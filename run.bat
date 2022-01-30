.venv\diagnostic\Scripts\activate.bat && ^
.venv\diagnostic\Scripts\python.exe -m pip install -r requirements.txt && ^
set FLASK_APP=main.py && ^
.venv\diagnostic\Scripts\python.exe -m flask run --host=0.0.0.0
