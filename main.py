import csv
from dataclasses import dataclass

from flask import Flask, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./data.sqlite3'
db = SQLAlchemy(app)


@dataclass
class Symptom(db.Model):
    __tablename__ = 'symptoms'
    id: int
    name: str

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


@dataclass
class Classification(db.Model):
    __tablename__ = 'classifications'
    id: int
    name: str
    identifier_name: str

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    identifier_name = db.Column(db.String)


@dataclass
class SymptomClassification(db.Model):
    __tablename__ = 'symptom_classifications'
    id: int
    symptom_id: int
    classification_id: int
    value: int

    id = db.Column(db.Integer, primary_key=True)
    symptom_id = db.Column(db.Integer, primary_key=True)
    classification_id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, primary_key=True)


db.create_all()

# def csv_init_populat():
with open('Simptom.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')

    line_count = 0
    symptoms = []

    for row in csv_reader:
        # testing.append(row)
        if line_count is not 0:
            print(row)

            monitor = 0
            ram = 0
            psu = 0
            proc = 0
            hdd = 0
            gpu = 0
            mboard = 0

            try:
                monitor = int(row[2])
            except:
                print('Monitor error')

            try:
                ram = int(row[3])
            except:
                print('ram error')

            try:
                psu = int(row[4])
            except:
                print('psu error')

            try:
                proc = int(row[5])
            except:
                print('proc error')

            try:
                hdd = int(row[6])
            except:
                print('hdd error')

            try:
                gpu = int(row[7])
            except:
                print('gpu error')

            try:
                mboard = int(row[8])
            except:
                print('Monitor error')

            dict_symptom = {
                'symptom': row[1],
                'monitor': monitor,
                'ram': ram,
                'psu': psu,
                'proc': proc,
                'hdd': hdd,
                'gpu': gpu,
                'mboard': mboard,
            }

            symptoms.append(dict_symptom)

        line_count += 1

    # Test search symptom
    for symptom in symptoms:
        found_symptom = Symptom.query.filter_by(
            name=symptom['symptom']).first()

        if found_symptom == None:
            print('Symptom not found. Adding...')
            db.session.add(Symptom(name=symptom['symptom']))
            db.session.commit()
        else:
            print('Symptom found', found_symptom)

    # Test search classification
    for classification_name in ['monitor', 'ram', 'psu', 'processor', 'hdd', 'gpu', 'mboard']:
        found_classification = Classification.query.filter_by(
            name=classification_name).first()

        if found_classification == None:
            print('Classification not found. Adding...')
            db.session.add(Classification(name=classification_name))
            db.session.commit()
        else:
            print('Classification found', found_classification)


# CSV init
# csv_init_populat()


@app.route('/')
def hello():
    return send_from_directory('frontend', path='index.html')


@app.route('/test-populate')
def test_populate():
    new_symptom = Symptom(name='TEst Symptom 1')
    db.session.add(new_symptom)
    db.session.commit()

    return jsonify(new_symptom)


@app.route('/symptoms')
def all_smptoms():
    return jsonify(Symptom.query.all())


@app.route('/classifications')
def all_classifications():
    return jsonify(Classification.query.all())
