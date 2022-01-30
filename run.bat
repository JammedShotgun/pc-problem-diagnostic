.venv\diagnostic\Scripts\activate.bat && ^
py -3 -m pip install -r requirements.txt && ^
set FLASK_APP=main.py && ^
py -3 -m flask run --host=0.0.0.0
