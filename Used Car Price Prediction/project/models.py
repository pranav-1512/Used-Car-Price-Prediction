from project import db,login_manager
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from datetime import datetime
import json
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)

class Users(db.Model,UserMixin):
    __tablename__="Users"
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    predicted_price = db.Column(db.Float)
    prediction_timestamp = db.Column(db.DateTime)
 
    
    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)
    def update_prediction(self, price,Year,Present_Price,Kms_Driven2):
        prediction = Predictions(predicted_price=price,year=Year,present_price=Present_Price,kms_driven=Kms_Driven2,prediction_timestamp=datetime.now())
        self.predictions.append(prediction)
        db.session.commit()
    predictions = db.relationship('Predictions', backref='user', lazy=True)
class Predictions(db.Model):
    __tablename__ = "Predictions"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    predicted_price = db.Column(db.Float)
    prediction_timestamp = db.Column(db.DateTime)
    year = db.Column(db.Integer)  # New field for year
    present_price = db.Column(db.Float)  # New field for present_price
    kms_driven = db.Column(db.Float)
   

