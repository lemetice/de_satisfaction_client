from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient
from sqlalchemy import inspect
import os

app = Flask(__name__)

# PostgreSQL Configuration
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'password')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'trustscore')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# MongoDB Configuration
MONGO_HOST = os.getenv('MONGO_HOST', 'mongodb')
MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
MONGO_DB = os.getenv('MONGO_DB', 'trustscore')

client = MongoClient(host=MONGO_HOST, port=MONGO_PORT)
mongo_db = client[MONGO_DB]

# Models for PostgreSQL
class Company(db.Model):
    __tablename__ = 'companies'
    company_id  = db.Column(db.Integer, primary_key=True)
    town = db.Column(db.String)
    country = db.Column(db.String)
    institution_type = db.Column(db.String)
    company_name = db.Column(db.String)
    trust_score = db.Column(db.Float)
    review  = db.Column(db.Integer)
    five_star_percentage = db.Column(db.Float)

# Routes
@app.route('/api/companies', methods=['GET'])
def get_companies():
    companies = Company.query.all()
    result = [
        {
            'company_id': c.company_id,
            'town': c.town,
            'country': c.country,
            'institution_type': c.institution_type,
            'company_name': c.company_name,
            'trust_score': c.trust_score,
            'review': c.review,
            'five_star_percentage': c.five_star_percentage
        }
        for c in companies
    ]
    return jsonify(result), 200

@app.route('/api/comments', methods=['GET'])
def get_comments():
    comments = list(mongo_db.commentaires.find({}, {'_id': 0}))
    return jsonify(comments), 200

inspector = inspect(db.engine)
columns = [col['name'] for col in inspector.get_columns('companies')]
if 'company_id' not in columns:
    print("La colonne 'company_id' n'existe pas.")

if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
