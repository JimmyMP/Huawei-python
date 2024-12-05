from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ClimateData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(50), nullable=False)
    maxt = db.Column(db.Float, nullable=False)
    mint = db.Column(db.Float, nullable=False)
    precipitation = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
