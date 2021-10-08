import csv
from dataclasses import dataclass
from itertools import count
from operator import countOf
import sys
from typing import Any, List, Optional
import uuid

from flask import Flask, jsonify, send_from_directory
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy
from flask import request
from flask_cors import CORS
import json
from pydantic import BaseModel
import pprint

from pydantic.types import UUID4

app = Flask(__name__, static_folder='frontend/public', static_url_path='/')
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./data.sqlite3'
db = SQLAlchemy(app)


# @dataclass
# class Symptom(db.Model):
#     __tablename__ = 'symptoms'
#     id: int
#     name: str

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)


# @dataclass
# class Classification(db.Model):
#     __tablename__ = 'classifications'
#     id: int
#     name: str
#     identifier_name: str

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)
#     identifier_name = db.Column(db.String)


# @dataclass
# class SymptomClassification(db.Model):
#     __tablename__ = 'symptom_classifications'
#     id: int
#     symptom_id: int
#     classification_id: int
#     value: int

#     id = db.Column(db.Integer, primary_key=True)
#     symptom_id = db.Column(db.Integer)
#     classification_id = db.Column(db.Integer)
#     value = db.Column(db.Integer)


# db.create_all()


class Classification(BaseModel):
    index: Optional[int]
    uuid: Optional[str]
    name: Optional[str]


class SymptomClassification(BaseModel):
    uuid: Optional[str]
    symptom_uuid: Optional[str]
    classification_uuid: Optional[str]
    value: Optional[int]


class Symptom(BaseModel):
    uuid: Optional[str]
    name: Optional[str]


class DiagnosticData(BaseModel):
    classifications: Optional[List[Classification]] = []
    symptoms: List[Symptom] = []
    symptom_classifications: List[SymptomClassification] = []


class SymptomClassificationView(BaseModel):
    symptom_classification: Optional[SymptomClassification]
    symptom: Optional[Symptom]
    classification: Optional[Classification]


def get_symptoms_data():
    with open('Simptom.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        counter = 0

        classifications = []
        symptoms = []
        symptom_classifications = []

        for row in csv_reader:
            if counter == 0:
                classifications_list = row[2:len(row)]

                for i, classification in enumerate(classifications_list):
                    classifications.append(Classification(
                        index=i,
                        uuid=f'{uuid.uuid4()}',
                        name=classification
                    ))
            else:
                new_symptom = Symptom(
                    uuid=f'{uuid.uuid4()}',
                    name=row[1]
                )

                symptoms.append(new_symptom)

                # Get values
                for i in range(0, len(classifications)):
                    found_classification = None

                    for classification in classifications:
                        if classification.index == i:
                            found_classification = classification
                            continue

                    # print(row[1], row[i + 2], found_classification)

                    if found_classification != None and counter != 0:
                        symptom_classifications.append(SymptomClassification(
                            uuid=f'{uuid.uuid4()}',
                            classification_uuid=found_classification.uuid,
                            symptom_uuid=new_symptom.uuid,
                            value=int(row[i + 2])
                        ))

            counter += 1

        return DiagnosticData(
            classifications=classifications,
            symptoms=symptoms,
            symptom_classifications=symptom_classifications
        )


diagnostic_data = get_symptoms_data()


class SymptomFrequency(BaseModel):
    symptom: Optional[Symptom] = []
    symptom_classifications: Optional[List[SymptomClassificationView]] = []
    frequency: Optional[int] = 0
    relevancy_percentage: Optional[float] = 0.0


class SawResult(BaseModel):
    classification: Optional[Classification] = None
    normalised_result: Optional[float] = 0.0


class DiagnosticResult(BaseModel):
    diagnostic_data: Optional[DiagnosticData] = None
    symptom_frequencies: Optional[List[SymptomFrequency]] = []
    inputs: Optional[Any] = None
    saw_result: List[SawResult] = []


@app.route('/diagnose')
def diagnose():
    diagnostic_data = get_symptoms_data()

    inputs = json.loads(request.args.get('input'))

    symptom_frequencies: List[SymptomFrequency] = []

    for symptom in diagnostic_data.symptoms:
        symptom_classifications: List[SymptomClassification] = []

        for symptom_classification in diagnostic_data.symptom_classifications:
            if symptom_classification.symptom_uuid == symptom.uuid:
                found_symptom = None

                for symptom in diagnostic_data.symptoms:
                    if symptom.uuid == symptom_classification.symptom_uuid:
                        found_symptom = symptom
                        break

                found_classification = None

                for classification in diagnostic_data.classifications:
                    if classification.uuid == symptom_classification.classification_uuid:
                        found_classification = classification
                        break

                symptom_classifications.append(SymptomClassificationView(
                    symptom_classification=symptom_classification,
                    symptom=found_symptom,
                    classification=found_classification
                ))

        symptom_frequencies.append(SymptomFrequency(
            symptom=symptom, symptom_classifications=symptom_classifications))

    for input in inputs:
        split_input: List[str] = input.split(' ')

        for word in split_input:
            for symptom in diagnostic_data.symptoms:
                count_tf = 0
                split_symptom = symptom.name.split(' ')

                for symptom_term in split_symptom:
                    if word.lower() in symptom_term.lower():
                        count_tf += 1

                # add to symptom_frequencies
                for symptom_frequency in symptom_frequencies:
                    if symptom_frequency.symptom.uuid == symptom.uuid:
                        symptom_frequency.frequency += count_tf

                print(word, 'found in', symptom.name, ':', count_tf)

    # Filter symptom frequencies. If not appear, empty
    new_symptom_frequencies: List[SymptomFrequency] = []

    for symptom_frequency in symptom_frequencies:
        if symptom_frequency.frequency is not 0:
            new_symptom_frequencies.append(symptom_frequency)

    # Calculate relevancy
    total_calculated_relevancy = 0.0

    for symptom_frequency in new_symptom_frequencies:
        total_calculated_relevancy += symptom_frequency.frequency

    for symptom_frequency in new_symptom_frequencies:
        symptom_frequency.relevancy_percentage = symptom_frequency.frequency / \
            total_calculated_relevancy * 100

    # Calculate simple additive weighting
    print('\n======\nSAW matrix\n======\n')

    saw_result_classifications: List[SawResult] = []

    for classification in diagnostic_data.classifications:
        saw_result_classifications.append(
            SawResult(classification=classification))

    for symptom_frequency in new_symptom_frequencies:
        print(symptom_frequency.symptom.name,
              f'({symptom_frequency.relevancy_percentage}% relevancy)', ':')

        for symptom_classification in symptom_frequency.symptom_classifications:
            print(symptom_classification.symptom_classification.value, end=' ')

        print()

        print('normalised:')
        for symptom_classification in symptom_frequency.symptom_classifications:
            normalised_saw_result = symptom_classification.symptom_classification.value * \
                symptom_frequency.relevancy_percentage / 100

            # Append to saw result
            for saw_res in saw_result_classifications:
                if saw_res.classification.uuid == symptom_classification.symptom_classification.classification_uuid:
                    saw_res.normalised_result += normalised_saw_result

            print(normalised_saw_result, end=' ')

        print()

        print('Leaderboard:')

        sorted_symptoms = sorted(
            saw_result_classifications, key=lambda s: s.normalised_result)

        for saw_result in sorted_symptoms:
            print(saw_result.dict())

    return jsonify(DiagnosticResult(
        diagnostic_data=diagnostic_data,
        symptom_frequencies=new_symptom_frequencies,
        inputs=inputs,
        saw_result=sorted_symptoms
    ).dict())


@app.route('/')
def hello():
    return app.send_static_file('index.html')
