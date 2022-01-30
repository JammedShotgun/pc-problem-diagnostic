.venv\diagnostic\Scripts\activate.bat && ^
python -m pip install -r requirements.txt && ^
set FLASK_APP=main.py && ^
python -m flask run --host=0.0.0.0