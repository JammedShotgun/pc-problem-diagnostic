import csv
from dataclasses import dataclass

from flask import Flask, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask import request
from flask_cors import CORS
import json
import pprint

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
    symptom_id = db.Column(db.Integer)
    classification_id = db.Column(db.Integer)
    value = db.Column(db.Integer)


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
    for classification_name in ['monitor', 'ram', 'psu', 'proc', 'hdd', 'gpu', 'mboard']:
        found_classification = Classification.query.filter_by(
            name=classification_name).first()

        if found_classification == None:
            print('Classification not found. Adding...')
            db.session.add(Classification(name=classification_name))
            db.session.commit()
        else:
            print('Classification found', found_classification)

    # Search for each classification ID for SymptomClassification
    for classification_name in ['monitor', 'ram', 'psu', 'proc', 'hdd', 'gpu', 'mboard']:
        found_classification = Classification.query.filter_by(
            name=classification_name).first()

        if found_classification is not None:
            for symptom in symptoms:
                found_symptom = Symptom.query.filter_by(
                    name=symptom['symptom']).first()

                if found_symptom is not None:
                    found_symptom_classifications = SymptomClassification.query.filter_by(
                        classification_id=found_classification.id, symptom_id=found_symptom.id).first()

                    if found_symptom_classifications is not None:
                        print('Found symptom classification for',
                              classification_name, found_classification.id, found_symptom_classifications)
                    else:
                        print('Symptom classifiaction not found. Creating... ')
                        db.session.add(SymptomClassification(
                            symptom_id=found_symptom.id, classification_id=found_classification.id, value=symptom[classification_name]))
                        db.session.commit()

                else:
                    print('Symptom', symptom['symptom'], 'not found')

        else:
            print('Classification not found.', classification_name)


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


@app.route('/calculate-tfidf')
def calculate_tfidf():
    args_str = request.args.get('args')
    args_json = []

    try:
        arr_of_problems = json.loads(args_str)

        for problem in arr_of_problems:
            args_json.append(problem.split(' '))

    except:
        print('Error loading JSON')

    pprint.pprint(args_json)

    return jsonify({
        'input': args_json,
        'output': 'WIP'
    })


@app.route('/symptom-classifications-view')
def all_classifications_view():
    classifications = Classification.query.all()
    symptoms = Symptom.query.all()

    symptom_classifications_view = []

    for symptom in symptoms:
        print('Symptom', symptom)
        found_symptom_classifications = SymptomClassification.query.filter_by(
            symptom_id=symptom.id).all()

        symptom_classification_view = []

        for symptom_classification in found_symptom_classifications:
            found_classification = None
            found_symptom = None

            for classification_i in classifications:
                if classification_i.id == symptom_classification.classification_id:
                    found_classification = classification_i

            for symptom_i in symptoms:
                if symptom_i.id == symptom_classification.symptom_id:
                    found_symptom = symptom_i

            symptom_classification_view.append({
                'symptom': found_symptom,
                'classification': found_classification,
                'symptom_classification': symptom_classification
            })

        symptom_classifications_view.append({
            'symptom': symptom,
            'symptom_classifications': symptom_classification_view
        })

    return jsonify(symptom_classifications_view)
